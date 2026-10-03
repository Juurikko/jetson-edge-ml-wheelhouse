# Exact AArch64 glibc loader validator correction

Run 37130165121, attempt 1, is immutable **failure** evidence, not a failed native compilation. Artifact 11278673940 was independently downloaded: ZIP SHA256 `a3518f362977dd924318816dbffe8efd4351494f693331d02612ac725e73f206`, wheel SHA256 `56e8b5d91ce789a7ded1cbc01e0f88b43346e9d6c34c5414b517e1823f35c9cd`.

The glibc **2.39** source names `ld-linux-aarch64.so.1` as the little-endian AArch64 loader in [sysdeps/unix/sysv/linux/aarch64/shlib-versions](https://github.com/bminor/glibc/blob/glibc-2.39/sysdeps/unix/sysv/linux/aarch64/shlib-versions). Independently fetched Git blob: `e1768a7361ed720f589056f1f8bd06f0eba7abba`. This is the standard loader identity for the frozen glibc/AArch64 contract. The ELF GLIBC-version ceiling remains 2.39 and dependency resolution must still pass on native Ubuntu 24.04.

`validate_needed()` is the previous exact allow-list factored for testing, with only this one additional name. No wildcard, prefix, foreign loader, absolute-path dependency, alternate CUDA major version, or arbitrary new library is allowed. The regression uses the actual ten DT_NEEDED entries; eight negative dependency cases and an empty inventory must fail. Existing ELF, SM87, no-PTX, wheel RECORD, patch, source and toolchain gates remain unchanged.

No FlashAttention source, CUDA, Torch, compiler, ABI or source patch changed. Names such as `_sm80.cu` are upstream filenames, not evidence about compiled targets. The final binary still requires cuobjdump SM87-only device-code evidence and absence of PTX. No AGX was accessed and no publication or physical qualification is authorized.
