# JetPack 7.2.1 — Jetson AGX Orin / CUDA 13.2 / Python 3.12 / SM87 Wheelhouse

Physically qualified ARM64/SM87 CUDA wheels, exact target locks, build recipes, and reproducible Jetson edge-ML evidence — engineered and qualified by **SynRex Oy**.

> **Target:** NVIDIA JetPack 7.2.1 / Jetson Linux (L4T) R39.2.1 on Jetson AGX Orin 64 GB.
>
> **Status:** eight-wheel R1 candidate set qualified by exact clean-install on the physical AGX Orin. No binary release is published yet.
>
> **Need this on a different target?** Deployment help, custom board bring-up and model porting are offered through [commercial advisory](COMMERCIAL.md). This public repository is a self-service reference and qualification showcase, not a general-purpose free Jetson support service.

## Qualified target

The first release channel is intentionally narrow:

- NVIDIA Jetson AGX Orin 64 GB
- NVIDIA JetPack 7.2.1
- Jetson Linux / L4T R39.2.1
- Linux `aarch64`
- Ubuntu 24.04.4 LTS
- kernel 6.8.12-1021-tegra
- glibc 2.39
- NVIDIA driver 595.78
- CUDA 13.2.86
- GCC/G++ 13.3.0
- CPython 3.12.3
- PyTorch 2.14.0+cu132
- Orin GPU, compute capability 8.7 / SM87

Nearby Jetson configurations may work, but they are **not qualified by this release** unless explicitly listed.

See [SUPPORTED_TARGETS.md](SUPPORTED_TARGETS.md) and the [machine-readable target contract](targets/agx-orin-r39.2.1-cu13.2-py312-sm87/target-contract.json).

## Why this repository exists

Jetson developers often reach a point where upstream Python packages are missing the exact ARM64/CUDA/Python combination required by a current BSP. This repository is intended to make those gaps reproducible rather than anecdotal.

A wheel is not called “supported” here merely because it built. Each artifact is tied to:

- an exact upstream source commit;
- an exact target contract;
- an exact SHA-256;
- a documented build origin;
- a stated qualification scope;
- known limitations and redistribution notices.

## Planned first-release artifacts

| Artifact | Current state | Qualification headline |
|---|---|---|
| torch-scatter | release candidate | Physical CUDA Q2; graph-stack Q3; LitePT exact-parity integration |
| torch-sparse | release candidate | Physical CUDA Q2; graph-stack Q3 |
| torch-cluster | release candidate | Physical CUDA Q2; graph-stack Q3 |
| spconv | release candidate | Physical SubMConv Q2; LitePT application Q4 |
| native LitePT PointROPE | release candidate | Physical CUDA + C08 exact-parity requalification PASS |
| OpenCV 4.14 CUDA | release candidate | AArch64/SM87 CUDA image + CUDA DNN physical PASS |
| cumm | release candidate | Apache-2.0 metadata corrected; physical TensorView + spconv compatibility PASS |
| Open3D 0.20 CUDA | release candidate | computational ELF bytes preserved; full physical CUDA/geometry/Torch requalification PASS |

Exact hashes and qualification boundaries are documented in [wheels/README.md](wheels/README.md). The combined eight-wheel set also passed the [R1 exact clean-install qualification](qualification/r1-clean-install.md).

## Qualification levels

- Q0 — SOURCE_LOCKED
- Q1 — BUILD_STATIC_CPU
- Q2 — DEVICE_GPU
- Q3 — STACK_HIL
- Q4 — MODEL_APPLICATION
- Q5 — PERFORMANCE
- Q6 — OFFLINE_CONTAINER

See [qualification/qualification-levels.md](qualification/qualification-levels.md).

## Commercial advisory

The public wheelhouse intentionally supports a very narrow, frozen target. SynRex offers fixed-scope commercial advisory and engineering for adjacent or private deployments, especially where the missing piece is not merely compiling code but making the complete stack defensible on real hardware.

Typical engagements include:

- deployment help for production Jetson systems;
- custom board bring-up and BSP / CUDA / Python stack validation;
- model porting and application-level qualification;
- missing ARM64/CUDA wheel ports and private wheelhouses;
- CI-built versus native-device rebuild comparison;
- hardware-in-the-loop qualification and release evidence;
- LiDAR, robotics, vision and multimodal edge-ML integration.

Use the [commercial advisory request](https://github.com/Juurikko/jetson-edge-ml-wheelhouse/issues/new?template=commercial-advisory.yml) for non-confidential initial scoping. See [COMMERCIAL.md](COMMERCIAL.md).

## Installation

Binary installation instructions will be published with the first GitHub Release. Until then, this repository is documentation/manifest-first and intentionally does not publish an install command pointing at unreleased artifacts.

See [docs/installation.md](docs/installation.md).

## Verification

The first release will ship SHA-256 manifests, a machine-readable wheelhouse lock, and target-verification tooling.

The repository itself is now guarded by a deterministic `repository-integrity` workflow. It validates the frozen target contract, candidate hashes, source-lock consistency, public-redaction rules, and that binary release payloads have not been committed to Git history.

See [docs/verification.md](docs/verification.md), [the R1 candidate manifest](manifests/release-r1-candidates.json), and [source provenance](provenance/README.md).

## Case studies

Two application-level studies are being prepared:

- LitePT-L optimization on AGX Orin, including native SM87 PointROPE and native torch-scatter.
- ECLAIR four-scene point-density operating envelope from native density down to 0.5 pts/m².

These are engineering case studies, not claims that four selected scenes replace the broader ECLAIR benchmark.

See [case-studies/README.md](case-studies/README.md).

## Licensing and redistribution

This repository indexes artifacts derived from multiple upstream projects with different licences. There is deliberately **no blanket repository licence applied to third-party wheel contents**.

Each release asset will carry its own source, licence/notice and redistribution record. Vendor runtimes such as CUDA/cuDNN/NPP, PyTorch, FFmpeg/GStreamer and NVIDIA cuSPARSELt are treated separately and are not automatically rehosted.

See [NOTICE.md](NOTICE.md), the [R1 notice index](notices/README.md), and the [release asset policy](docs/release-assets.md).

## Support boundary

Public issues are for reproducible defects in the **exact published artifacts on the documented target**. The project does not commit to free troubleshooting for different Jetson models, BSP/CUDA/Python combinations, custom carrier boards, deployment environments or private models.

Deployment assistance, custom board bring-up and model porting are handled through commercial advisory. See [SUPPORT.md](SUPPORT.md).

## Disclaimer

These are unofficial community builds. NVIDIA, PyTorch, PyG, OpenCV, Open3D, LitePT and other upstream projects do not endorse these binaries.
