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
from build_evidence import check_compile_contract, retained_commands, recover
from validate import elf_machine, validate_arch_evidence, validate_needed, validate_records


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

    def test_aarch64_glibc_loader_dependency(self):
        # Actual DT_NEEDED from immutable run 37130165121 / artifact 11278673940.
        validate_needed(['libc10.so', 'libtorch_cpu.so', 'libtorch_python.so',
                         'libcudart.so.13', 'libc10_cuda.so', 'libtorch_cuda.so',
                         'libstdc++.so.6', 'libgcc_s.so.1', 'libc.so.6',
                         'ld-linux-aarch64.so.1'])

    def test_unreviewed_dependencies_still_fail(self):
        for dependency in ['libsurprise.so.1', 'libcudart.so.12', 'libcudart.so.14',
                           'ld-linux-aarch64.so.2', 'ld-linux-aarch64_be.so.1',
                           'ld-linux-x86-64.so.2', '/lib/ld-linux-aarch64.so.1',
                           'ld-linux-aarch64.so.1.evil']:
            with self.subTest(dependency=dependency), self.assertRaises(RuntimeError):
                validate_needed(['libc.so.6', 'ld-linux-aarch64.so.1', dependency])
        with self.assertRaises(RuntimeError):
            validate_needed([])

    def compile_fixture(self):
        sources = ['csrc/flash_attn/flash_api.cpp'] + sorted(
            f'csrc/flash_attn/src/flash_{direction}_hdim{dim}_{dtype}{causal}_sm80.cu'
            for direction in ('bwd', 'fwd', 'fwd_split') for dim in (32, 64, 96, 128, 192, 256)
            for dtype in ('fp16', 'bf16') for causal in ('', '_causal'))
        rows = []
        for i, source in enumerate(sources, 1):
            compiler = 'g++-13' if i == 1 else '/cuda/bin/nvcc'
            flags = '' if i == 1 else ' -gencode arch=compute_87,code=sm_87 --threads 1'
            rows.append(f'[{i}/73] {compiler} -std=c++20{flags} -c /work/flash-attention/{source} -o output.o')
        rows.append('g++-13 -shared -o flash_attn_2_cuda.cpython-312-aarch64-linux-gnu.so')
        rows.append("creating 'flash_attn-2.8.3.post1+cu132torch214.sm87.synrex0-cp312-cp312-linux_aarch64.whl'")
        rows.append('removing build/bdist.linux-aarch64/wheel')
        return '\n'.join(rows)

    def test_complete_retained_commands(self):
        text = retained_commands(self.compile_fixture())
        self.assertEqual(text.count('/bin/nvcc '), 72)

    def test_incomplete_or_modified_retained_commands_fail(self):
        original = self.compile_fixture()
        for modified in [original.replace('[73/73]', '[72/73]'),
                         original.replace('code=sm_87', 'code=sm_80', 1),
                         original.replace('flash_fwd_hdim32_bf16_sm80.cu', 'unreviewed.cu'),
                         original.replace('g++-13 -shared', 'unreviewed-linker -shared'),
                         original.replace('-std=c++20', '-std=c++17', 1)]:
            with self.assertRaises(RuntimeError):
                retained_commands(modified)

    def test_abi_zero_override_fails(self):
        flags = '-std=c++20 -gencode arch=compute_87,code=sm_87'
        check_compile_contract(flags)  # Missing redundant define still needs real ABI probes at audit.
        check_compile_contract(flags + ' -D_GLIBCXX_USE_CXX11_ABI=1')
        for extra in [' -D_GLIBCXX_USE_CXX11_ABI=0', ' -U_GLIBCXX_USE_CXX11_ABI',
                      ' -D_GLIBCXX_USE_CXX11_ABI=1 -D_GLIBCXX_USE_CXX11_ABI=0',
                      ' -gencode arch=compute_87,code=compute_87',
                      ' -gencode arch=compute_87a,code=sm_87a']:
            with self.subTest(extra=extra), self.assertRaises(RuntimeError):
                check_compile_contract(flags + extra)

    def test_arbitrary_retained_archive_fails(self):
        import tempfile
        with tempfile.TemporaryDirectory() as directory:
            p = Path(directory) / 'wrong.zip'
            p.write_bytes(b'not the pinned artifact')
            with self.assertRaisesRegex(RuntimeError, 'archive digest mismatch'):
                recover(p, Path(directory), Path(directory), {})

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
