# Open3D 0.20 CUDA — public release R1

## Result

**PASS — public-release candidate**

```text
open3d-0.20.0+cu132sm87-1synrexrelease1-cp312-cp312-linux_aarch64.whl
SHA-256 fae18d4ec2f4f9ebf9d8ac98da73291d6a444e2d3a047a5d1ebc950f47b3b38a
```

Upstream Open3D commit:

```text
b6c5e196384ad71e75b6e6f9c5da22d046221f1d
```

## Release-packaging strategy

The accepted computational Open3D ELF payload was **not recompiled** for this public release.

The public wheel preserves the previously qualified computational ELF bytes while making the distribution closure cleaner for the frozen AGX target:

- `libOpen3D.so.0.20` preserved byte-for-byte;
- `pybind.cpython-312-aarch64-linux-gnu.so` preserved byte-for-byte;
- bundled `libgfortran.so.5` externalized to target `libgfortran5`;
- bundled `libtbb.so.12` externalized to target `libtbb12`;
- unreferenced bundled `libgomp.so.1` removed;
- stale CuTeDSL EULA notice copied from the build-tree notice sweep removed after provenance verification showed no CuTeDSL payload outside the licence tree;
- remaining Open3D/third-party notices retained.

## Computational ELF identities

```text
libOpen3D.so.0.20
SHA-256 af40b4b19e9b516d22d21f5a1da9609c88cb85284cb82fb9ba15c146168501a6

pybind.cpython-312-aarch64-linux-gnu.so
SHA-256 f8a86b14eefd55dc2434576007a3b0c62b1c840dd78f099a2b7a9a1a1f5042cd
```

These are the same computational ELF identities as the already accepted physical AGX qualification baseline.

## Qualification gates

The public wheel passed:

- accepted baseline identity gate;
- system `libgfortran5` / `libtbb12` runtime gate;
- computational ELF identity gate;
- CuTeDSL/EULA provenance gate;
- release-thinning gate;
- external runtime resolution gate;
- candidate RECORD/static integrity audit;
- isolated candidate install;
- Open3D import and external-runtime provenance;
- full physical AGX CUDA / geometry / Torch qualification.

Final physical marker:

```text
OPEN3D_PUBLIC_RELEASE_PHYSICAL_GATE=PASS
```

The physical qualification covered the same nine areas used by the accepted baseline:

1. native dynamic loading;
2. CUDA tensor arithmetic and non-contiguous views;
3. linear algebra solve/matmul;
4. point-cloud voxel downsampling;
5. nearest-neighbor search;
6. tensor ICP with known translation;
7. repeated synchronized CUDA execution;
8. PyTorch 2.14 CUDA DLPack zero-copy;
9. fresh-process PyTorch → Open3D import order.

## Evidence hashes

```text
public release wheel
fae18d4ec2f4f9ebf9d8ac98da73291d6a444e2d3a047a5d1ebc950f47b3b38a

system runtime hash record
636ba969e3dd907765ed8448406771155f5b3ae5697b24829fa21cef3018fdf2

CuTeDSL/EULA provenance
2470e26c82d40402281fa120e656df3a698618424836a68aeb0fba06102a2223

release thinning
fd96003c4f434a9ee06495130b975c679c33ba75a9d062f87ec1b87e9c341436

post-thinning ldd record
7630aa98cc8315f31cd4dfb6b545286a3febd5f6ad7786fa76560dd069fe8070

static public candidate audit
ed5f6f85ca9e94260ca4332a4becbbc235c8b12f85e3c004ea0ccc3bf13433bb

external runtime provenance
4c68c15eebee99ca7e692a83df4f4435e68c851ea0d36a3155a588213dd6511a

physical AGX public-release qualification
3dbb5be3cc889c6e9836170eb81436a261b6edeb954fc33347cc7723a0157b54

release-candidate record
14bdef9a643133a7b90c9056838f9e3c0324e10544cbe67e90428ea127861828
```

Evidence bundle:

```text
SYNREX_OPEN3D_PUBLIC_RELEASE_R1.tar.gz
bytes 1341454695
SHA-256 5946f0d90e0c58af15dcdbd96c33d7faa6b6c13b32427895675ee6065893799d
```

The remote archive was observed only after the release script had reached its terminal COMPLETE state.

## Claim boundary

This qualification covers the exact public wheel on the frozen AGX Orin R39.2.1 / CUDA 13.2 / Python 3.12 / SM87 target. It does not imply support for other Jetson models, other CUDA/BSP combinations, or the optional Open3D-ML model stack.
