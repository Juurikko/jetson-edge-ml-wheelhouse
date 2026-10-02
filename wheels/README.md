# Wheel status

This page records the exact wheel bytes published in the R1 GitHub Release.

Release: https://github.com/Juurikko/jetson-edge-ml-wheelhouse/releases/tag/agx-orin-r39.2.1-cu13.2-py312-sm87-r1

All eight wheels below are published R1 assets and retain the exact SHA-256 identities that passed physical qualification before publication.

## Published R1 — exact bytes

### torch-scatter

```text
torch_scatter-2.1.2+pt214cu132sm87-1agxlocal0-cp312-cp312-linux_aarch64.whl
SHA-256 04086e77c00ebd10a5ffdea865582bcb9940ec251d74fe7cdefad095da0ff00d
source f514c10f920b5aeed2eb162092f0ad20d3edee52
```

Scope: Q2 physical CUDA PASS; Q3 graph-stack HIL PASS; LitePT A3 exact-parity integration PASS.

### torch-sparse

```text
torch_sparse-0.6.18+pt214cu132sm87-1agxlocal0-cp312-cp312-linux_aarch64.whl
SHA-256 6462630ebbbf3d0f7c854ee79fe213dbe968c8327f9f17b3672d73be3396e6d2
source ef897d8a019771c0d93d6de2e4d3dda52e8faf62
```

Scope: Q2 physical CUDA PASS; Q3 graph-stack HIL PASS. BF16 native SpMM is outside the accepted qualification scope.

### torch-cluster

```text
torch_cluster-1.6.3+pt214cu132sm87-1agxlocal0-cp312-cp312-linux_aarch64.whl
SHA-256 abed65ec74fb796cfd4c7b7d510fc1e8c49ce9a4f4202fd5e98b708fee755a8c
source e9a855c284b45edcbf0282cf70ac09bee0ce4e49
```

Scope: Q2 physical CUDA PASS; Q3 graph-stack HIL PASS.

### spconv

```text
spconv_cu132-2.3.8-1agxlocal0-cp312-cp312-linux_aarch64.whl
SHA-256 4d473deb40425d018fc0198100838ba6cccc68f8fcdbb146216e4aedd17754b9
source 263d6b47425ef843c82f997b12d8b714013d216c
```

Scope: Q2 physical FP32 SubMConv oracle PASS; Q4 LitePT application parity PASS.

### native LitePT PointROPE — public release rebuild R1

```text
synrex_pointrope_cu132_sm87-0.0.0+pt214cu132sm87.2-cp312-cp312-linux_aarch64.whl
SHA-256 273fe321b79e51dd19b2c96f12080d4f945de58c13be51082428f61c64ceab1b
source 436d04801c8151faebe66a1b2d368a9711e7e6aa
```

Scope: static wheel/licence audit PASS; AArch64/SM87 PASS; physical CUDA smoke PASS; C08 A3 exact raw-ID parity PASS.

This release rebuild supersedes the internal licence-incomplete `.1` wheel for public distribution.

### cumm 0.8.2 — public release rebuild R1

```text
cumm_cu132-0.8.2-2agxrelease1-cp312-cp312-linux_aarch64.whl
SHA-256 c3e3ae935079638dc255e3b1a923582787ac2220c8f1f98ab9b717121131c5d9
source 4c77b38d1ab57d5d1c157adddf67dad93f3a446b
```

Scope: corrected Apache-2.0 metadata PASS; AArch64 ELF PASS; physical TensorView CUDA copy PASS; accepted spconv CUDA compatibility PASS.

The public wheel replaces the stale-metadata internal wheel for public distribution.

### Open3D 0.20 CUDA — public release R1

```text
open3d-0.20.0+cu132sm87-1synrexrelease1-cp312-cp312-linux_aarch64.whl
SHA-256 fae18d4ec2f4f9ebf9d8ac98da73291d6a444e2d3a047a5d1ebc950f47b3b38a
source b6c5e196384ad71e75b6e6f9c5da22d046221f1d
```

Scope: computational ELF bytes preserved; system libgfortran/TBB runtimes externalized; full physical CUDA/geometry/Torch requalification PASS.

### OpenCV 4.14 CUDA

```text
opencv_contrib_python_cuda_synrex-4.14.0+cu132sm87-2synrexci0-cp312-cp312-linux_aarch64.whl
SHA-256 a994978776cb7c24eee3108da4a18431fcd5efd0604d852675ee2d25effbb8f1
OpenCV source 0654a42e19215ef25b1d367d822f3c630447e7c7
opencv_contrib source a8e9acd62cabd30419dba83007f2ac0d07de5e2c
```

Scope: physical CUDA image operations PASS; CUDA DNN Conv+ReLU PASS. FFmpeg/GStreamer/CUDA runtime libraries are external dependencies, not bundled release assets.

## R1 publication status

**Published.** Eight exact custom wheels are available as individual GitHub Release assets and inside the convenience bundle `SYNREX_AGX_ORIN_R1_8_WHEEL_BUNDLE.tar.gz`.

The complete 15-asset release was downloaded back from GitHub to the physical AGX and SHA-256 round-trip verified before publication.

## Base/vendor dependencies

PyTorch, SciPy, NVIDIA CUDA/cuDNN/NPP, NVIDIA cuSPARSELt and OpenCV system multimedia runtime dependencies are pinned separately and are not automatically rehosted by this project.
