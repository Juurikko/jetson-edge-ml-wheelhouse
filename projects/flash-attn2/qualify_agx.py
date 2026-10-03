#!/usr/bin/env python3
"""Run only later, explicitly on AGX, in an already prepared candidate environment.

This script never installs packages, downloads inputs, changes firmware, or rebuilds
any dependency. Successful numerical tests alone cannot promote the wheel: the
frozen official LitePT anchor is mandatory for PHYSICAL_AGX_QUALIFIED.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib
import importlib.metadata as metadata
import json
from pathlib import Path
import platform
import re
import subprocess
import sys
import traceback
import zipfile

from prepare import require, sha256, write_json
from litept_anchor import run_anchor

# Read-only identities from the existing R1 publication candidate snapshot.
# These are NOT replacement qualification records or newly built dependencies.
R1 = {
    'cumm_cu132-0.8.2-2agxrelease1-cp312-cp312-linux_aarch64.whl':
        'c3e3ae935079638dc255e3b1a923582787ac2220c8f1f98ab9b717121131c5d9',
    'spconv_cu132-2.3.8-1agxlocal0-cp312-cp312-linux_aarch64.whl':
        '4d473deb40425d018fc0198100838ba6cccc68f8fcdbb146216e4aedd17754b9',
    'synrex_pointrope_cu132_sm87-0.0.0+pt214cu132sm87.2-cp312-cp312-linux_aarch64.whl':
        '273fe321b79e51dd19b2c96f12080d4f945de58c13be51082428f61c64ceab1b',
    'torch_scatter-2.1.2+pt214cu132sm87-1agxlocal0-cp312-cp312-linux_aarch64.whl':
        '04086e77c00ebd10a5ffdea865582bcb9940ec251d74fe7cdefad095da0ff00d',
    'torch_cluster-1.6.3+pt214cu132sm87-1agxlocal0-cp312-cp312-linux_aarch64.whl':
        'abed65ec74fb796cfd4c7b7d510fc1e8c49ce9a4f4202fd5e98b708fee755a8c',
}


def installed_matches(wheel: Path, expected_sha: str) -> dict:
    from packaging.utils import parse_wheel_filename
    require(sha256(wheel) == expected_sha, 'Wheel bytes do not match frozen identity: ' + wheel.name)
    name, version, _, _ = parse_wheel_filename(wheel.name)
    dist = metadata.distribution(name)
    require(dist.version == str(version), 'Installed distribution version differs: ' + name)
    checked = 0
    with zipfile.ZipFile(wheel) as archive:
        for path in archive.namelist():
            if path.endswith(('.py', '.so')) or '.so.' in path:
                installed = Path(dist.locate_file(path))
                require(installed.is_file(), 'Installed wheel code missing: ' + path)
                require(sha256(installed) == hashlib.sha256(archive.read(path)).hexdigest(), 'Installed code differs from wheel: ' + path)
                checked += 1
    require(checked > 0, 'No installed wheel code verified')
    return {'filename': wheel.name, 'sha256': expected_sha, 'installed_version': dist.version, 'code_files_verified': checked}


def hardware_contract() -> dict:
    import torch
    require(platform.machine() == 'aarch64' and platform.python_version() == '3.12.3', 'CPU/Python target drift')
    require(platform.libc_ver() == ('glibc', '2.39'), 'glibc drift')
    os_release = platform.freedesktop_os_release()
    require(os_release.get('ID') == 'ubuntu' and os_release.get('VERSION_ID') == '24.04', 'OS drift')
    device_model = Path('/proc/device-tree/model').read_bytes().decode().rstrip('\0')
    require('Jetson AGX Orin' in device_model, 'Not a physical AGX Orin')
    meminfo = Path('/proc/meminfo').read_text()
    total_kib = int(re.search(r'MemTotal:\s+(\d+)', meminfo).group(1))
    require(total_kib > 50 * 1024 * 1024, 'Not the 64 GB AGX memory class')
    l4t = Path('/etc/nv_tegra_release').read_text()
    require('R39' in l4t and re.search(r'REVISION:\s*2\.1(?:\D|$)', l4t), 'L4T R39.2.1 not confirmed')
    jetpack = subprocess.check_output(['dpkg-query', '-W', '-f=${Version}', 'nvidia-jetpack'], text=True).strip()
    require(jetpack.startswith('7.2.1'), 'JetPack package identity not confirmed')
    require(platform.release() == '6.8.12-1021-tegra', 'Frozen physical kernel drift')
    nvcc = subprocess.check_output(['/usr/local/cuda-13.2/bin/nvcc', '--version'], text=True)
    require(re.search(r'\bV13\.2\.86\b', nvcc), 'CUDA compiler drift')
    for compiler in ('gcc', 'g++'):
        require(subprocess.check_output([compiler, '-dumpfullversion'], text=True).strip() == '13.3.0', 'Compiler drift: ' + compiler)
    require(torch.__version__ == '2.14.0+cu132' and torch.version.cuda == '13.2', 'Torch/CUDA ABI drift')
    require(torch.version.git_version == '08187d9e0fba026dc8217405802ab5381dc88d90', 'Torch source drift')
    require(bool(torch._C._GLIBCXX_USE_CXX11_ABI), 'Torch CXX11 ABI drift')
    require(torch.cuda.is_available() and torch.cuda.get_device_capability(0) == (8, 7), 'SM87 CUDA device unavailable')
    require(torch.cuda.is_bf16_supported(), 'BF16 unavailable on this target')
    return {'device_model': device_model, 'memory_total_kib': total_kib, 'jetpack': jetpack,
            'l4t': l4t.strip(), 'kernel': platform.release(), 'nvcc': nvcc.strip(),
            'torch': torch.__version__, 'torch_git': torch.version.git_version,
            'gpu': torch.cuda.get_device_name(0), 'compute_capability': [8, 7],
            'memory_note': 'Jetson unified memory, not dedicated discrete VRAM'}


def numerical_tests() -> list[dict]:
    import torch
    import flash_attn
    torch.manual_seed(20261003)
    torch.backends.cuda.matmul.allow_tf32 = False
    torch.backends.cudnn.allow_tf32 = False
    results = []
    for dtype in (torch.float16, torch.bfloat16):
        tolerance = 0.005 if dtype == torch.float16 else 0.04
        for head_dim in (18, 32, 64, 128, 192, 256):
            for causal in (False, True):
                q, k, v = [torch.randn(1, 65, 2, head_dim, device='cuda', dtype=dtype) for _ in range(3)]
                actual = flash_attn.flash_attn_func(q, k, v, dropout_p=0.0, causal=causal)
                qf, kf, vf = [x.float().transpose(1, 2) for x in (q, k, v)]
                logits = qf @ kf.transpose(-1, -2) * head_dim ** -0.5
                if causal:
                    mask = torch.ones(65, 65, device='cuda', dtype=torch.bool).triu(1)
                    logits = logits.masked_fill(mask, float('-inf'))
                expected = (logits.softmax(dim=-1) @ vf).transpose(1, 2)
                torch.cuda.synchronize()
                torch.testing.assert_close(actual.float(), expected, rtol=tolerance, atol=tolerance)
                results.append({'kind': 'dense_forward', 'dtype': str(dtype), 'head_dim': head_dim, 'causal': causal,
                                'max_abs_error': float((actual.float() - expected).abs().max()), 'rtol': tolerance, 'atol': tolerance, 'status': 'PASS'})
        lengths = (17, 65, 3)
        cu = torch.tensor([0, 17, 82, 85], device='cuda', dtype=torch.int32)
        for head_dim in (18, 64):
            packed = torch.randn(85, 3, 2, head_dim, device='cuda', dtype=dtype)
            actual = flash_attn.flash_attn_varlen_qkvpacked_func(packed, cu, max_seqlen=65, dropout_p=0.0)
            references = []
            left = 0
            for length in lengths:
                q, k, v = packed[left:left + length].float().unbind(dim=1)
                q, k, v = [x.transpose(0, 1) for x in (q, k, v)]
                references.append(((q @ k.transpose(-1, -2) * head_dim ** -0.5).softmax(dim=-1) @ v).transpose(0, 1))
                left += length
            expected = torch.cat(references)
            torch.cuda.synchronize()
            torch.testing.assert_close(actual.float(), expected, rtol=tolerance, atol=tolerance)
            results.append({'kind': 'varlen_packed_forward', 'dtype': str(dtype), 'head_dim': head_dim,
                            'lengths': list(lengths), 'max_abs_error': float((actual.float() - expected).abs().max()), 'status': 'PASS'})
        q, k, v = [torch.randn(1, 17, 2, 64, device='cuda', dtype=dtype, requires_grad=True) for _ in range(3)]
        output = flash_attn.flash_attn_func(q, k, v, dropout_p=0.0)
        output.float().square().mean().backward()
        torch.cuda.synchronize()
        require(all(x.grad is not None and bool(torch.isfinite(x.grad).all()) and bool(x.grad.abs().sum() > 0) for x in (q, k, v)), 'Backward smoke failed')
        results.append({'kind': 'backward_smoke', 'dtype': str(dtype), 'head_dim': 64, 'dropout': 0.0, 'status': 'PASS'})
    return results


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--execute-on-agx', action='store_true', help='Explicit authorization to run local GPU tests')
    parser.add_argument('--bundle', type=Path, required=True)
    parser.add_argument('--r1-wheelhouse', type=Path, required=True)
    parser.add_argument('--litept-repo', type=Path, required=True)
    parser.add_argument('--anchor-spec', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True, help='New evidence directory; never overwrite previous qualification')
    args = parser.parse_args()
    require(args.execute_on_agx, 'Device execution must be explicitly requested')
    args.output.mkdir(parents=True, exist_ok=False)
    report = {'schema': 'synrex.flash_attn2.agx_qualification.v1',
              'physical_state': 'CANDIDATE_NOT_PHYSICALLY_QUALIFIED', 'status': 'RUNNING',
              'harness_sha256': sha256(Path(__file__)), 'dependency_installs': False, 'firmware_changes': False}
    report_file = args.output / 'qualification.json'
    write_json(report_file, report)
    try:
        bundle = args.bundle.resolve()
        sums = (bundle / 'SHA256SUMS').read_text().splitlines()
        require(bool(sums), 'Bundle digest inventory missing')
        for line in sums:
            digest, relative = line.split('  ', 1)
            path = (bundle / relative).resolve()
            require(path.is_relative_to(bundle) and path.is_file(), 'Unsafe or missing bundle entry')
            require(sha256(path) == digest, 'Bundle checksum mismatch: ' + relative)
        manifest = json.loads((bundle / 'build-manifest.json').read_text())
        require(manifest['build_state'] == 'CI_BUILD_VALIDATED' and manifest['physical_state'] == 'CANDIDATE_NOT_PHYSICALLY_QUALIFIED', 'Not a validated CI candidate')
        report['ci_manifest_sha256'] = sha256(bundle / 'build-manifest.json')
        report['hardware'] = hardware_contract()
        report['candidate'] = installed_matches(bundle / 'wheel' / manifest['wheel']['filename'], manifest['wheel']['sha256'])
        report['qualified_r1_inputs'] = [installed_matches(args.r1_wheelhouse / name, digest) for name, digest in R1.items()]
        importlib.import_module('flash_attn')
        extension = importlib.import_module('flash_attn_2_cuda')
        expected_elf = manifest['elfs'][0]
        require(sha256(Path(extension.__file__)) == expected_elf['sha256'], 'Imported extension is not the audited ELF')
        report['numerical_tests'] = numerical_tests()
        write_json(report_file, report)
        report['official_litept_anchor'] = run_anchor(args.litept_repo.resolve(), args.anchor_spec.resolve())
        report['status'] = 'PASS'
        report['physical_state'] = 'PHYSICAL_AGX_QUALIFIED'
        report['scope'] = 'Exact wheel, frozen AGX stack, tested FP16/BF16 forward cases, head64 no-dropout backward smoke, frozen official LitePT post-transform inference anchor'
        report['limitations'] = ['Not all FlashAttention features or head-dimension backward cases tested',
                                 'No performance/energy qualification', 'No semantic accuracy claim', 'No publication authorization implied']
    except Exception as exc:
        report['status'] = 'FAIL'
        report['failure'] = type(exc).__name__ + ': ' + str(exc)
        (args.output / 'failure.txt').write_text(traceback.format_exc())
        raise
    finally:
        write_json(report_file, report)
        (args.output / 'qualification.sha256').write_text(sha256(report_file) + '  qualification.json\n')
    print('PHYSICAL_AGX_QUALIFIED: ' + report['candidate']['sha256'])


if __name__ == '__main__':
    main()
