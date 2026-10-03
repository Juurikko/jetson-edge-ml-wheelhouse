#!/usr/bin/env python3
"""Reject dependency errors; diagnose one exact NVIDIA wheel metadata anomaly.

No third-party wheel metadata or binary is changed. An unsupported-tag exception
requires the exact recorded ARM64 wheel hash and independently checked ELF bytes.
"""
from __future__ import annotations
import importlib.metadata as metadata
import json
import os
from pathlib import Path
import subprocess
import sys
from packaging.tags import parse_tag, sys_tags
from prepare import require, sha256, write_json
from validate import elf_machine

NAME = 'nvidia-cusparselt-cu13'
VERSION = '0.8.1'
INPUT_SHA256 = '4dca476c50bf4780d46cd0bfbd82e2bc10a08e4fef7950917ce8d7578d22a23f'
WARNING = 'nvidia-cusparselt-cu13 0.8.1 is not supported on this platform'


def main() -> None:
    evidence = Path(os.environ['FA_OUT']) / 'evidence'
    check = subprocess.run([sys.executable, '-m', 'pip', 'check'], text=True,
                           stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    (evidence / 'pip-check.txt').write_text(check.stdout)
    print(check.stdout, flush=True)
    report = {'raw_pip_check_exit_code': check.returncode, 'raw_pip_check': check.stdout,
              'status': 'FAIL', 'third_party_metadata_modified': False, 'binary_modified': False}
    try:
        if check.returncode == 0:
            report['status'] = 'PASS'
            return
        lines = [line.strip() for line in check.stdout.splitlines() if line.strip()]
        require(check.returncode == 1 and lines == [WARNING], 'Unreviewed dependency failure')
        inputs = json.loads((evidence / 'torch-install-report.json').read_text())['install']
        matches = [x for x in inputs if x['metadata']['name'].lower().replace('_', '-') == NAME]
        require(len(matches) == 1, 'Missing NVIDIA dependency provenance')
        item = matches[0]
        require(item['metadata']['version'] == VERSION, 'cuSPARSELt version drift')
        require(item['download_info']['archive_info']['hashes']['sha256'] == INPUT_SHA256, 'cuSPARSELt input byte drift')
        require(item['download_info']['url'].endswith('nvidia_cusparselt_cu13-0.8.1-py3-none-manylinux2014_aarch64.whl'), 'Unexpected NVIDIA wheel platform')
        dist = metadata.distribution(NAME)
        require(dist.version == VERSION, 'Installed cuSPARSELt identity mismatch')
        wheel_metadata = dist.read_text('WHEEL')
        require(bool(wheel_metadata), 'cuSPARSELt WHEEL metadata missing')
        (evidence / 'cusparselt-original-WHEEL.txt').write_text(wheel_metadata)
        (evidence / 'cusparselt-original-METADATA.txt').write_text(dist.read_text('METADATA') or '')
        tags = set()
        for line in wheel_metadata.splitlines():
            if line.startswith('Tag: '):
                tags.update(parse_tag(line[5:].strip()))
        require(bool(tags) and not tags.intersection(set(sys_tags())), 'Failure is not reproduced by installed wheel tags')
        elfs = []
        for relative in dist.files or []:
            path = Path(dist.locate_file(relative))
            if path.is_file():
                with path.open('rb') as stream:
                    header = stream.read(64)
                if header.startswith(b'\x7fELF'):
                    machine = elf_machine(header)
                    require(machine == 183, 'NVIDIA wheel contains non-AArch64 ELF')
                    elfs.append({'path': str(relative), 'e_machine': machine, 'sha256': sha256(path), 'bytes': path.stat().st_size})
        require(bool(elfs), 'No actual AArch64 cuSPARSELt library found')
        report.update(status='PASS_WITH_VERIFIED_TAG_METADATA_EXCEPTION', package=NAME,
                      version=VERSION, input_sha256=INPUT_SHA256, original_wheel_tags=sorted(map(str, tags)),
                      elfs=elfs, scope='Known input-wheel tag anomaly only; no CUDA runtime qualification',
                      rationale='Exact ARM64 NVIDIA input bytes; every installed ELF independently proves AArch64; no missing/version-conflicting dependencies accepted')
        print(json.dumps(report, indent=2), flush=True)
    finally:
        write_json(evidence / 'dependency-gate.json', report)


if __name__ == '__main__':
    main()
