#!/usr/bin/env python3
"""Cloud checks are static/CPU checks, never physical CUDA qualification."""
from __future__ import annotations

import argparse
import base64
import csv
import hashlib
import importlib.metadata
import io
import json
import os
from pathlib import Path
import platform
import re
import shutil
import struct
import subprocess
import sys
import zipfile

from prepare import HERE, ROOT, command, require, sha256, write_json


def environment() -> dict:
    import torch
    lock = json.loads((HERE / 'source-lock.json').read_text())
    require(platform.machine() == 'aarch64', 'Build is not native AArch64')
    require(platform.python_version() == lock['build']['python'], 'CPython version drift')
    require(sys.implementation.name == 'cpython', 'Not CPython')
    os_release = platform.freedesktop_os_release()
    require(os_release.get('ID') == 'ubuntu' and os_release.get('VERSION_ID') == '24.04', 'Ubuntu target drift')
    require(platform.libc_ver() == ('glibc', lock['build']['glibc']), 'glibc version drift')
    for compiler, key in [('gcc-13', 'gcc'), ('g++-13', 'gxx')]:
        require(command(compiler, '-dumpfullversion') == lock['build'][key], compiler + ' drift')
    nvcc = command(str(Path(os.environ['CUDA_HOME']) / 'bin/nvcc'), '--version')
    require(re.search(r'\bV13\.2\.86\b', nvcc) is not None, 'CUDA compiler version drift')
    require(torch.__version__ == lock['torch']['version'], 'Torch version drift')
    require(torch.version.cuda == lock['torch']['cuda'], 'Torch CUDA version drift')
    require(torch.version.git_version == lock['torch']['git'], 'Torch source identity drift')
    require(bool(torch._C._GLIBCXX_USE_CXX11_ABI) is True, 'Torch CXX11 ABI drift')
    require(os.environ.get('FLASH_ATTN_CUDA_ARCHS') == '87', 'FA architecture environment drift')
    require(os.environ.get('TORCH_CUDA_ARCH_LIST') == '8.7', 'Torch architecture environment drift')
    require(os.environ.get('FLASH_ATTENTION_FORCE_BUILD') == 'TRUE', 'Prebuilt wheel fallback not disabled')
    require(os.environ.get('FLASH_ATTENTION_FORCE_CXX11_ABI', 'FALSE') == 'FALSE', 'Must validate ABI, not override it')
    require(os.environ.get('MAX_JOBS') == '2' and os.environ.get('NVCC_THREADS') == '1', 'Unreviewed parallelism')
    factory_sha = command('git', 'rev-parse', 'HEAD', cwd=ROOT)
    require(factory_sha == os.environ.get('GITHUB_SHA'), 'Checkout/provenance SHA mismatch')
    require(os.environ.get('GITHUB_REPOSITORY') == 'Juurikko/jetson-edge-ml-wheelhouse', 'Unexpected build repository')
    require(bool(os.environ.get('GITHUB_RUN_ID')), 'Missing CI run identity')
    return {
        'python': platform.python_version(), 'machine': platform.machine(),
        'glibc': platform.libc_ver(), 'os': os_release,
        'kernel': platform.release(), 'gcc': command('gcc-13', '--version'),
        'gxx': command('g++-13', '--version'), 'nvcc': nvcc,
        'torch': torch.__version__, 'torch_cuda': torch.version.cuda,
        'torch_git': torch.version.git_version, 'cxx11_abi': bool(torch._C._GLIBCXX_USE_CXX11_ABI),
        'torch_config': torch.__config__.show(), 'factory_commit': factory_sha,
        'runner_image': os.environ.get('ImageVersion'), 'runner_arch': os.environ.get('RUNNER_ARCH'),
        'run_id': os.environ['GITHUB_RUN_ID'], 'run_attempt': os.environ.get('GITHUB_RUN_ATTEMPT'),
        'run_url': 'https://github.com/' + os.environ['GITHUB_REPOSITORY'] + '/actions/runs/' + os.environ['GITHUB_RUN_ID'],
        'max_jobs': 2, 'nvcc_threads': 1, 'authorized_cuda_architectures': ['sm_87'],
        'gpu_execution_performed': False, 'deployment_l4t_is_not_runner_l4t': True,
    }


def elf_machine(data: bytes) -> int:
    require(len(data) >= 64 and data[:4] == b'\x7fELF', 'Not an ELF object')
    require(data[4] == 2 and data[5] == 1, 'Expected little-endian 64-bit ELF')
    return struct.unpack_from('<H', data, 18)[0]


def validate_arch_evidence(elf_listing: str, resources: str, ptx_listing: str) -> None:
    require(set(re.findall(r'\bsm_(\d+[a-z]?)\b', elf_listing)) == {'87'}, 'Missing SM87 SASS or unintended CUDA architectures')
    require(set(re.findall(r'arch\s*=\s*sm_(\d+[a-z]?)\b', resources)) == {'87'}, 'Resource headers do not prove exclusive SM87 code')
    require(re.search(r'PTX file\s+\d+\s*:', ptx_listing, re.I) is None, 'PTX present: this contract permits SM87 SASS only')
    require(re.search(r'\b(?:sm|compute)_\d+', ptx_listing) is None, 'Unexpected device target in PTX inventory')


def validate_records(wheel: zipfile.ZipFile) -> list[dict]:
    names = wheel.namelist()
    require(len(names) == len(set(names)), 'Duplicate wheel paths')
    require(all(not n.startswith('/') and '..' not in Path(n).parts for n in names), 'Unsafe wheel path')
    records = [n for n in names if n.endswith('.dist-info/RECORD')]
    require(len(records) == 1, 'Wheel RECORD missing or ambiguous')
    rows = list(csv.reader(io.StringIO(wheel.read(records[0]).decode())))
    require({r[0] for r in rows} == set(names), 'Wheel RECORD coverage mismatch')
    inventory = []
    for name, digest, size in rows:
        data = wheel.read(name)
        if name != records[0]:
            expected = 'sha256=' + base64.urlsafe_b64encode(hashlib.sha256(data).digest()).decode().rstrip('=')
            require(digest == expected and int(size) == len(data), 'Wheel RECORD mismatch: ' + name)
        inventory.append({'path': name, 'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest(), 'elf': data.startswith(b'\x7fELF')})
    return inventory


def audit() -> None:
    from packaging.utils import parse_wheel_filename
    out = Path(os.environ['FA_OUT']).resolve()
    evidence = out / 'evidence'
    work = Path(os.environ['FA_WORK']).resolve()
    env = environment()
    wheels = list((out / 'wheel').glob('*.whl'))
    require(len(wheels) == 1, 'Expected exactly one real wheel')
    wheel_file = wheels[0]
    name, version, _, tags = parse_wheel_filename(wheel_file.name)
    require(name == 'flash-attn', 'Wrong distribution')
    require({str(t) for t in tags} == {'cp312-cp312-linux_aarch64'}, 'Wrong wheel platform or ABI tag')
    require(str(version) == '2.8.3.post1+cu132torch214.sm87.synrex0', 'Unexpected wheel source/build version')
    unpacked = work / 'wheel-inspection'
    unpacked.mkdir()
    with zipfile.ZipFile(wheel_file) as wheel:
        inventory = validate_records(wheel)
        wheel.extractall(unpacked)
        metadata = [n for n in wheel.namelist() if n.endswith('.dist-info/METADATA')]
        require(len(metadata) == 1, 'Wheel metadata missing')
        (evidence / 'wheel-METADATA.txt').write_bytes(wheel.read(metadata[0]))
        require(any('LICENSE' in n.upper() for n in wheel.namelist()), 'Wheel license missing')
    write_json(evidence / 'wheel-content-inventory.json', inventory)
    elfs = [r for r in inventory if r['elf']]
    require(len(elfs) == 1 and Path(elfs[0]['path']).name.startswith('flash_attn_2_cuda'), 'Unexpected bundled ELF libraries')
    elf_inventory = []
    for entry in elfs:
        elf = unpacked / entry['path']
        require(elf_machine(elf.read_bytes()) == 183, 'Non-AArch64 ELF inside wheel')
        header = command('readelf', '-h', str(elf))
        dynamic = command('readelf', '-d', str(elf))
        versions = command('readelf', '--version-info', str(elf))
        needed = re.findall(r'\(NEEDED\).*?\[(.*?)\]', dynamic)
        allowed = {'libc10.so', 'libtorch.so', 'libtorch_cpu.so', 'libtorch_python.so', 'libc10_cuda.so',
                   'libtorch_cuda.so', 'libcudart.so.13', 'libstdc++.so.6', 'libm.so.6', 'libgcc_s.so.1',
                   'libc.so.6', 'libpthread.so.0', 'libdl.so.2', 'librt.so.1'}
        require(bool(needed) and set(needed) <= allowed, 'Unreviewed ELF dependencies: ' + repr(set(needed) - allowed))
        require('(RPATH)' not in dynamic and '(RUNPATH)' not in dynamic, 'Unreviewed RPATH/RUNPATH')
        glibc_required = [tuple(map(int, v.split('.'))) for v in re.findall(r'\bGLIBC_(\d+(?:\.\d+)+)\b', versions)]
        require(not glibc_required or max(glibc_required) <= (2, 39), 'GLIBC newer than AGX')
        for label, text in [('elf-header', header), ('elf-dynamic', dynamic), ('elf-versions', versions)]:
            (evidence / (label + '.txt')).write_text(text + '\n')
        ldd = subprocess.run(['ldd', str(elf)], text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        (evidence / 'dependency-ldd.txt').write_text(ldd.stdout)
        require(ldd.returncode == 0, 'ldd failed')
        unresolved = re.findall(r'^\s*(\S+)\s+=>\s+not found', ldd.stdout, re.M)
        require(set(unresolved) <= {'libcuda.so.1', 'libnvidia-ml.so.1'}, 'Non-driver dependency unresolved: ' + repr(unresolved))
        cuobjdump = str(Path(os.environ['CUDA_HOME']) / 'bin/cuobjdump')
        listings = {}
        for option, label in [('--list-elf', 'cuda-elf-list'), ('--list-ptx', 'cuda-ptx-list'), ('--dump-resource-usage', 'cuda-resource-usage')]:
            listings[label] = command(cuobjdump, option, str(elf))
            (evidence / (label + '.txt')).write_text(listings[label] + '\n')
        validate_arch_evidence(listings['cuda-elf-list'], listings['cuda-resource-usage'], listings['cuda-ptx-list'])
        elf_inventory.append({**entry, 'e_machine': 183, 'needed': needed, 'unresolved_driver_libraries': unresolved,
                              'sass_architectures': ['sm_87'], 'ptx_architectures': []})
    write_json(evidence / 'elf-inventory.json', elf_inventory)
    ninja_files = list((work / 'flash-attention/build').rglob('build.ninja'))
    require(len(ninja_files) == 1, 'Missing or ambiguous build command evidence')
    ninja = ninja_files[0].read_text()
    require(set(re.findall(r'arch=compute_(\d+)', ninja)) == {'87'}, 'Unintended nvcc compile targets')
    require(set(re.findall(r'code=sm_(\d+)', ninja)) == {'87'}, 'Unintended nvcc SASS targets')
    require('code=compute_' not in ninja, 'Unapproved PTX generation')
    require('-std=c++20' in ninja and '-std=c++17' not in ninja, 'Torch C++ standard mismatch')
    require('_GLIBCXX_USE_CXX11_ABI=1' in ninja, 'Missing positive CXX11 ABI compiler evidence')
    shutil.copy2(ninja_files[0], evidence / 'build.ninja.txt')
    commands = command('ninja', '-f', str(ninja_files[0]), '-t', 'commands', cwd=ninja_files[0].parent)
    (evidence / 'compile-commands.txt').write_text(commands + '\n')
    source_lock = json.loads((evidence / 'source-lock.resolved.json').read_text())
    require(source_lock['factory_commit'] == env['factory_commit'], 'Source/factory provenance mismatch')
    require(sha256(evidence / 'upstream.patch') == source_lock['patch_policy']['applied_patch_sha256'], 'Patch digest mismatch')
    require(source_lock['upstream']['commit'] == 'a8aa52b1ab3e9ca574c8a33b3f35afc017ffa2e2', 'Source identity mismatch')
    pip_report = json.loads((evidence / 'torch-install-report.json').read_text())
    torch_inputs = [i for i in pip_report['install'] if i['metadata']['name'].lower() == 'torch']
    require(len(torch_inputs) == 1, 'Missing exact torch download provenance')
    require(torch_inputs[0]['metadata']['version'] == '2.14.0+cu132', 'Torch input mismatch')
    require(bool(torch_inputs[0]['download_info']['archive_info']['hashes'].get('sha256')), 'Torch input SHA256 missing')
    for filename in ['source-lock.resolved.json', 'cuda-inputs.json', 'source-file-inventory.json',
                     'build-environment.json', 'torch-install-report.json', 'build-tools-install-report.json',
                     'pip-inspect.json', 'pip-freeze.txt', 'build.log', 'factory/qualify_agx.py',
                     'factory/litept_anchor.py', 'factory/NOTICE.md']:
        require((evidence / filename).is_file() and (evidence / filename).stat().st_size > 0, 'Incomplete evidence: ' + filename)
    manifest = {
        'schema': 'synrex.flash_attn2.ci_build_manifest.v1',
        'build_state': 'CI_BUILD_VALIDATED',
        'physical_state': 'CANDIDATE_NOT_PHYSICALLY_QUALIFIED',
        'qualification_level': 'Q1_BUILD_STATIC_CPU',
        'gpu_execution_performed': False, 'published_release': False,
        'wheel': {'filename': wheel_file.name, 'sha256': sha256(wheel_file), 'bytes': wheel_file.stat().st_size},
        'target_contract': json.loads((evidence / 'target-contract.json').read_text()),
        'environment': env, 'source_lock_sha256': sha256(evidence / 'source-lock.resolved.json'),
        'patch_sha256': sha256(evidence / 'upstream.patch'),
        'torch_input': torch_inputs[0]['download_info'],
        'elfs': elf_inventory,
        'limitations': ['No Orin GPU in GitHub CI', 'No physical import/forward/backward qualification',
                        'No official LitePT inference performed in CI', 'No performance claim'],
    }
    # This is the only cloud promotion point, after all checks passed.
    write_json(out / 'build-manifest.json', manifest)
    sums = [sha256(p) + '  ' + str(p.relative_to(out)) for p in sorted(out.rglob('*')) if p.is_file() and p.name != 'SHA256SUMS']
    (out / 'SHA256SUMS').write_text('\n'.join(sums) + '\n')
    print('CI_BUILD_VALIDATED / CANDIDATE_NOT_PHYSICALLY_QUALIFIED', flush=True)
    print('WHEEL_SHA256=' + sha256(wheel_file), flush=True)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('mode', choices=['preflight', 'audit'])
    args = parser.parse_args()
    if args.mode == 'preflight':
        evidence = Path(os.environ['FA_OUT']) / 'evidence'
        write_json(evidence / 'build-environment.json', environment())
        print('Exact native compiler/Torch/Python contract: PASS', flush=True)
    else:
        audit()


if __name__ == '__main__':
    main()
