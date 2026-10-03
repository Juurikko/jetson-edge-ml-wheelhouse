#!/usr/bin/env python3
import base64
import hashlib
import io
from pathlib import Path
import struct
import sys
import unittest
import zipfile

sys.path.insert(0, str(Path(__file__).resolve().parent))
from prepare import patch_setup
from validate import elf_machine, validate_arch_evidence, validate_records


class FactoryTests(unittest.TestCase):
    def test_patch_is_minimal_and_context_checked(self):
        original = ('    if "80" in cuda_archs():\n'
                    '        cc_flag.append("-gencode")\n'
                    '        cc_flag.append("arch=compute_80,code=sm_80")\n'
                    '    nvcc_flags = [\n    "-O3",\n    "-std=c++17",\n    ]\n'
                    '    compiler_c17_flag=["-O3", "-std=c++17"]\n')
        patched = patch_setup(original)
        self.assertIn('arch=compute_87,code=sm_87', patched)
        self.assertIn('(TORCH_MAJOR, TORCH_MINOR) >= (2, 14)', patched)
        self.assertNotIn('FLASHATTENTION_DISABLE', patched)
        with self.assertRaises(RuntimeError):
            patch_setup(patched)
        with self.assertRaises(RuntimeError):
            patch_setup(original.replace('compiler_c17_flag', 'changed_upstream'))

    def test_exact_sm87(self):
        validate_arch_evidence('ELF file 1: kernel.sm_87.cubin', 'arch = sm_87\n', '')

    def test_missing_device_code(self):
        with self.assertRaises(RuntimeError):
            validate_arch_evidence('', '', '')

    def test_extra_architecture(self):
        with self.assertRaises(RuntimeError):
            validate_arch_evidence('sm_87 sm_80', 'arch = sm_87', '')

    def test_header_architecture_mismatch(self):
        with self.assertRaises(RuntimeError):
            validate_arch_evidence('sm_87', 'arch = sm_80', '')

    def test_ptx_forbidden(self):
        with self.assertRaises(RuntimeError):
            validate_arch_evidence('sm_87', 'arch = sm_87', 'PTX file 1: compute_87.ptx')

    def test_native_elf_machine(self):
        elf = bytearray(64)
        elf[:6] = b'\x7fELF\x02\x01'
        struct.pack_into('<H', elf, 18, 183)
        self.assertEqual(elf_machine(elf), 183)
        elf[4] = 1
        with self.assertRaises(RuntimeError):
            elf_machine(elf)
        with self.assertRaises(RuntimeError):
            elf_machine(b'not an ELF')

    def make_wheel(self, digest_override=None, path='flash_attn/example.py'):
        content = b'# source\n'
        digest = digest_override or ('sha256=' + base64.urlsafe_b64encode(hashlib.sha256(content).digest()).decode().rstrip('='))
        record = 'flash_attn-2.8.3.post1.dist-info/RECORD'
        payload = io.BytesIO()
        with zipfile.ZipFile(payload, 'w') as archive:
            archive.writestr(path, content)
            archive.writestr(record, f'{path},{digest},{len(content)}\n{record},,\n')
        payload.seek(0)
        return zipfile.ZipFile(payload)

    def test_wheel_record(self):
        with self.make_wheel() as archive:
            self.assertEqual(len(validate_records(archive)), 2)

    def test_tampered_record(self):
        with self.make_wheel('sha256=wrong') as archive:
            with self.assertRaises(RuntimeError):
                validate_records(archive)

    def test_unsafe_wheel_path(self):
        with self.make_wheel(path='../escape.py') as archive:
            with self.assertRaises(RuntimeError):
                validate_records(archive)


if __name__ == '__main__':
    unittest.main(verbosity=2)
