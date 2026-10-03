#!/usr/bin/env python3
"""Supplement the full cubin inventory with all-fatbinary PTX and real SASS."""
from __future__ import annotations
from pathlib import Path
import re
from prepare import command, require, sha256, write_json


def validate_no_ptx_dump(text: str) -> None:
    # CUDA 13.2 prints ELF-only fatbinary headers even for --dump-ptx.
    # Remove only complete, exact SM87/Linux/64-bit ELF header blocks; any
    # PTX body/header, other architecture or unknown text remains a failure.
    header = (r"Fatbin elf code:\n=+\narch = sm_87\n"
              r"code version = \[1,8\]\nhost = linux\ncompile_size = 64bit(?:\n|$)")
    remainder = re.sub(header, '', text).strip()
    require(not remainder or re.fullmatch(r"cuobjdump info\s*: No PTX file found to extract from '[^'\n]+'\.(?: You may try with -all option\.)?", remainder) is not None,
        'PTX code or unrecognized all-fatbinary PTX inspection output')


def full_device_audit(cuobjdump: str, elf: Path, evidence: Path) -> dict:
    resources = command(cuobjdump, '--all-fatbin', '--dump-resource-usage', str(elf))
    arches = re.findall(r'arch\s*=\s*sm_(\d+[a-z]?)\b', resources)
    require(set(arches) == {'87'}, 'All-fatbinary inspection found missing or non-SM87 SASS')
    (evidence / 'cuda-all-resource-usage.txt').write_text(resources + '\n')
    ptx = command(cuobjdump, '--all-fatbin', '--dump-ptx', str(elf))
    (evidence / 'cuda-all-ptx-dump.txt').write_text(ptx + '\n')
    validate_no_ptx_dump(ptx)
    functions = re.findall(r'^\s*Function (\S+):\s*$', resources, re.M)
    selected = {}
    for dtype, marker in [('fp16', 'half_t'), ('bf16', 'bfloat16_t')]:
        candidates = [name for name in functions if 'flash_fwd_kernel' in name and marker in name]
        require(bool(candidates), 'Missing emitted forward dtype kernel: ' + dtype)
        # Select real emitted symbols, never infer an architecture from source filenames.
        selected[dtype] = next((name for name in candidates if '_traitsILi32E' in name), candidates[0])
    sass = command(cuobjdump, '--all-fatbin', '--dump-sass', '--function', ','.join(selected.values()), str(elf))
    (evidence / 'cuda-sass-fp16-bf16-samples.txt').write_text(sass + '\n')
    require(set(re.findall(r'\bsm_(\d+[a-z]?)\b', sass)) == {'87'}, 'SASS sample architecture mismatch')
    require(all(name in sass for name in selected.values()), 'Requested dtype SASS disassembly missing')
    require(re.search(r'/\*[0-9a-fA-F]{4,}\*/', sass) is not None, 'No actual SASS instructions emitted by disassembler')
    files = ['cuda-all-resource-usage.txt', 'cuda-all-ptx-dump.txt', 'cuda-sass-fp16-bf16-samples.txt']
    result = {'status': 'PASS', 'sass_architectures': ['sm_87'], 'ptx_architectures': [],
              'all_fatbinary_sections_inspected': True, 'all_fatbinary_architecture_headers': len(arches),
              'resource_function_entries': len(functions), 'representative_forward_sass_symbols': selected,
              'sass_samples_are_not_a_substitute_for_complete_architecture_inventory': True,
              'gpu_execution_performed': False,
              'reports': {name: {'sha256': sha256(evidence / name), 'bytes': (evidence / name).stat().st_size} for name in files}}
    write_json(evidence / 'device-code-full-audit.json', result)
    return result
