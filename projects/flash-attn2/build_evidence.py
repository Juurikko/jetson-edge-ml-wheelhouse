#!/usr/bin/env python3
"""Fail-closed compiler evidence and recovery of ONE immutable native attempt.

A retained-wheel audit is not a rebuild. Original bytes, build identity and raw
verbose commands remain distinct from the new audit environment/provenance.
"""
from __future__ import annotations
import json
import os
from pathlib import Path
import re
import shutil
import zipfile
from prepare import HERE, command, require, sha256, write_json

BUILD_COMMIT = 'e3214a869926c78477ea3b92a43c335ec4c40445'
RUN_ID = '37130165121'
ARTIFACT_ID = 11278673940
ARCHIVE_SHA256 = 'a3518f362977dd924318816dbffe8efd4351494f693331d02612ac725e73f206'
WHEEL_NAME = 'flash_attn-2.8.3.post1+cu132torch214.sm87.synrex0-cp312-cp312-linux_aarch64.whl'
WHEEL_SHA256 = '56e8b5d91ce789a7ded1cbc01e0f88b43346e9d6c34c5414b517e1823f35c9cd'


def check_compile_contract(text: str) -> None:
    require(set(re.findall(r'arch=compute_(\d+[a-z]?)', text)) == {'87'}, 'Unintended nvcc compile targets')
    require(set(re.findall(r'code=sm_(\d+[a-z]?)', text)) == {'87'}, 'Unintended nvcc SASS targets')
    require('code=compute_' not in text, 'Unapproved PTX generation')
    require('-std=c++20' in text and '-std=c++17' not in text, 'Torch C++ standard mismatch')
    overrides = re.findall(r'_GLIBCXX_USE_CXX11_ABI(?:=([^\s\x27\x22]+))?', text)
    require(all(value == '1' for value in overrides) and '-U_GLIBCXX_USE_CXX11_ABI' not in text,
            'Unapproved compiler ABI override')


def retained_commands(log: str) -> str:
    rows = re.findall(r'^\[(\d+)/(\d+)\] (.+)$', log, re.M)
    require(len(rows) == 73 and {int(n) for n, _, _ in rows} == set(range(1, 74))
            and {total for _, total, _ in rows} == {'73'}, 'Incomplete retained compile transcript')
    commands = [text for _, _, text in rows]
    cuda = [text for text in commands if '/bin/nvcc ' in text]
    require(len(cuda) == 72 and sum(text.startswith('g++-13 ') for text in commands) == 1,
            'Unexpected retained compilation topology')
    for text in cuda:
        check_compile_contract(text)
        require(text.count('-gencode arch=compute_87,code=sm_87') == 1 and '--threads 1' in text,
                'Retained CUDA command drift')
    require(all('-std=c++20' in text for text in commands), 'Per-command C++ standard drift')
    sources = [re.findall(r'/flash-attention/(csrc/\S+\.(?:cu|cpp)) ', text) for text in commands]
    require(all(len(paths) == 1 for paths in sources), 'Ambiguous retained source command')
    expected = {'csrc/flash_attn/flash_api.cpp'} | {
        f'csrc/flash_attn/src/flash_{direction}_hdim{dim}_{dtype}{causal}_sm80.cu'
        for direction in ('bwd', 'fwd', 'fwd_split') for dim in (32, 64, 96, 128, 192, 256)
        for dtype in ('fp16', 'bf16') for causal in ('', '_causal')}
    require({paths[0] for paths in sources} == expected, 'Retained source coverage mismatch')
    links = [line for line in log.splitlines() if line.startswith('g++-13 ') and ' -shared ' in line]
    require(len(links) == 1 and 'flash_attn_2_cuda.cpython-312-aarch64-linux-gnu.so' in links[0],
            'Missing retained link command')
    require("creating '" in log and WHEEL_NAME in log and "removing build/bdist.linux-aarch64/wheel" in log,
            'Retained wheel emission was not completed')
    result = '\n'.join(commands + links) + '\n'
    check_compile_contract(result)
    return result


def compiler_abi_evidence(commands: str, work: Path, evidence: Path, elf: Path) -> dict:
    check_compile_contract(commands)
    # Torch 2.14 need not pass a redundant -D when GCC already defaults to ABI 1.
    # Probe the actual frozen host and nvcc host compiler, and require ABI 1 in
    # both preprocessor evaluation and emitted object symbols. Never force it.
    probe = work / 'abi-proof'
    probe.mkdir()
    source = '#include <string>\n#if _GLIBCXX_USE_CXX11_ABI != 1\n#error ABI must be 1\n#endif\nstd::string synrex_abi_probe(std::string x) { return x; }\n'
    cpp, cu = probe / 'probe.cpp', probe / 'probe.cu'
    cpp.write_text(source)
    cu.write_text(source)
    nvcc = str(Path(os.environ['CUDA_HOME']) / 'bin/nvcc')
    invocations = [
        ['g++-13', '-std=c++20', '-c', str(cpp), '-o', str(probe / 'host.o')],
        [nvcc, '-std=c++20', '-ccbin', 'gcc-13', '--threads', '1', '-gencode',
         'arch=compute_87,code=sm_87', '-c', str(cu), '-o', str(probe / 'cuda-host.o')]]
    for args in invocations:
        command(*args)
    symbols = {}
    for label, path in [('host', probe / 'host.o'), ('cuda-host', probe / 'cuda-host.o'), ('wheel', elf)]:
        text = command('readelf', '--wide', '--symbols', str(path))
        require('__cxx11' in text, 'Positive emitted CXX11 ABI evidence missing: ' + label)
        (evidence / ('abi-' + label + '-symbols.txt')).write_text(text + '\n')
        symbols[label] = {'sha256': sha256(path), 'has_cxx11_symbols': True}
    result = {'status': 'PASS', 'required_abi': 1, 'abi_forced_or_changed': False,
              'source': source, 'probe_commands': invocations, 'emitted_symbols': symbols,
              'explanation': 'Effective default ABI 1 proved for frozen GCC/G++ 13.3 and nvcc 13.2.86; Torch ABI 1 separately gated.'}
    write_json(evidence / 'compiler-abi-evidence.json', result)
    return result


def recover(archive: Path, out: Path, work: Path, env: dict) -> dict:
    require(sha256(archive) == ARCHIVE_SHA256, 'Retained artifact archive digest mismatch')
    retained = work / 'retained-native-build'
    require(not retained.exists(), 'Retained audit directory already exists')
    with zipfile.ZipFile(archive) as payload:
        names = payload.namelist()
        require(len(names) == len(set(names)), 'Duplicate retained artifact paths')
        require(all(not n.startswith('/') and '..' not in Path(n).parts for n in names), 'Unsafe retained path')
        require(all((item.external_attr >> 16) & 0o170000 != 0o120000 for item in payload.infolist()), 'Retained symlink forbidden')
        require(payload.testzip() is None, 'Retained artifact ZIP integrity failure')
        payload.extractall(retained)
    old = retained / 'evidence'
    current = out / 'evidence'
    original_env = json.loads((old / 'build-environment.json').read_text())
    require(original_env['factory_commit'] == BUILD_COMMIT and original_env['run_id'] == RUN_ID
            and original_env['run_attempt'] == '1', 'Retained build provenance drift')
    for key in ['python', 'machine', 'glibc', 'gcc', 'gxx', 'nvcc', 'torch', 'torch_cuda',
                'torch_git', 'cxx11_abi', 'max_jobs', 'nvcc_threads', 'authorized_cuda_architectures']:
        require(original_env[key] == env[key], 'Original/new audit contract differs: ' + key)
    require(original_env['os']['ID'] == 'ubuntu' and original_env['os']['VERSION_ID'] == '24.04'
            and original_env['gpu_execution_performed'] is False, 'Original platform evidence drift')
    a = json.loads((old / 'source-lock.resolved.json').read_text())
    b = json.loads((current / 'source-lock.resolved.json').read_text())
    require(a.pop('factory_commit') == BUILD_COMMIT and b.pop('factory_commit') == env['factory_commit'],
            'Source factory identity mismatch')
    require(a == b, 'Re-prepared source lock differs from original native build')
    for name in ['upstream.patch', 'source-file-inventory.json', 'target-contract.json']:
        require(sha256(old / name) == sha256(current / name), 'Re-prepared source bytes differ: ' + name)
    for name in ['source-lock.json', 'cuda-inputs.lock.json', 'prepare.py', 'dependency_gate.py', 'patches/0001-sm87-cxx20.patch']:
        require(sha256(old / 'factory' / name) == sha256(HERE / name), 'Frozen build input changed: ' + name)
    require(json.loads((old / 'cuda-inputs.json').read_text())['inputs'] ==
            json.loads((current / 'cuda-inputs.json').read_text())['inputs'], 'Original CUDA archive identities differ')
    report = json.loads((old / 'torch-install-report.json').read_text())
    inputs = [i for i in report['install'] if i['metadata']['name'].lower() == 'torch']
    require(len(inputs) == 1 and inputs[0]['metadata']['version'] == '2.14.0+cu132'
            and inputs[0]['download_info']['archive_info']['hashes']['sha256'] == a['torch']['wheel_sha256'],
            'Original Torch input provenance mismatch')
    dep = json.loads((old / 'dependency-gate.json').read_text())
    require(dep['status'] in ('PASS', 'PASS_WITH_VERIFIED_TAG_METADATA_EXCEPTION'), 'Original dependency gate failed')
    wheel = retained / 'wheel' / WHEEL_NAME
    require(sha256(wheel) == WHEEL_SHA256 and wheel.stat().st_size == 59708621, 'Retained wheel digest/size mismatch')
    require(not list((out / 'wheel').glob('*.whl')), 'Refusing to replace another wheel')
    shutil.copy2(wheel, out / 'wheel' / WHEEL_NAME)
    text = retained_commands((old / 'build.log').read_text())
    shutil.copy2(old / 'build.log', current / 'build.log')
    (current / 'compile-commands.txt').write_text(text)
    preservation = out / 'preserved'
    preservation.mkdir()
    preserved = preservation / 'run-37130165121-artifact-11278673940.zip'
    shutil.copy2(archive, preserved)
    require(sha256(preserved) == ARCHIVE_SHA256, 'Preservation copy mismatch')
    result = {'mode': 'AUDIT_RETAINED_NATIVE_WHEEL_NOT_REBUILD', 'original_conclusion': 'failure',
              'original_run_id': RUN_ID, 'original_run_attempt': 1, 'original_factory_commit': BUILD_COMMIT,
              'artifact_id': ARTIFACT_ID, 'artifact_zip_sha256': ARCHIVE_SHA256,
              'wheel_sha256': WHEEL_SHA256, 'original_environment': original_env,
              'original_build_log_sha256': sha256(old / 'build.log'), 'compile_commands': 73,
              'command_evidence': 'Complete original verbose Ninja transcript (1..73) and link command; no reconstructed build.ninja claimed',
              'original_ninja_file_retained': False, 'upstream_and_toolchain_reprepared_and_verified': True}
    write_json(current / 'retained-build-provenance.json', result)
    return result
