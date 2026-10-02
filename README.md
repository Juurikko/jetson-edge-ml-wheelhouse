# JetPack 7.2.1 — Jetson AGX Orin / CUDA 13.2 / Python 3.12 / SM87 Wheelhouse

Physically qualified ARM64/SM87 CUDA wheels, exact target locks, build recipes, and reproducible Jetson edge-ML evidence — engineered and qualified by **SynRex Oy**.

**Fully local. Deterministic workflow. Physical-HIL qualified. Auditable.**

**Engineering lead & commercial contact:** Tuomas Pietilä, SynRex Oy · [LinkedIn](https://www.linkedin.com/in/tuomas-pietila/) · [tuomas.pietila@synrex.fi](mailto:tuomas.pietila@synrex.fi)

> **Target:** NVIDIA JetPack 7.2.1 / Jetson Linux (L4T) R39.2.1 on Jetson AGX Orin 64 GB.
>
> NVIDIA release mapping: [JetPack 7.2.1 with Jetson Linux 39.2.1](https://developer.nvidia.com/embedded/jetpack/downloads).
>
> **Status:** R1 is publicly released. The exact eight-wheel set was physically qualified on the AGX Orin, uploaded as GitHub Release assets, downloaded back to the AGX, and SHA-256 round-trip verified before publication.
>
> **Release:** [agx-orin-r39.2.1-cu13.2-py312-sm87-r1](https://github.com/Juurikko/jetson-edge-ml-wheelhouse/releases/tag/agx-orin-r39.2.1-cu13.2-py312-sm87-r1)
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

## Published R1 artifacts

| Artifact | Current state | Qualification headline |
|---|---|---|
| torch-scatter | published R1 | Physical CUDA Q2; graph-stack Q3; LitePT exact-parity integration |
| torch-sparse | published R1 | Physical CUDA Q2; graph-stack Q3 |
| torch-cluster | published R1 | Physical CUDA Q2; graph-stack Q3 |
| spconv | published R1 | Physical SubMConv Q2; LitePT application Q4 |
| native LitePT PointROPE | published R1 | Physical CUDA + C08 exact-parity requalification PASS |
| OpenCV 4.14 CUDA | published R1 | AArch64/SM87 CUDA image + CUDA DNN physical PASS |
| cumm | published R1 | Apache-2.0 metadata corrected; physical TensorView + spconv compatibility PASS |
| Open3D 0.20 CUDA | published R1 | computational ELF bytes preserved; full physical CUDA/geometry/Torch requalification PASS |

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

## SynRex Custom Wheel Foundry

The public R1 wheelhouse is one qualified reference configuration. **SynRex Custom Wheel Foundry** is SynRex's proprietary, **100% locally operable deterministic build, hardware-in-the-loop qualification and release-engineering platform** for native ARM64/CUDA Python stacks. Its core build orchestration, dependency closure, artifact inspection, target qualification, acceptance gating and evidence generation run on infrastructure controlled by SynRex or the licensee; a proprietary SynRex cloud/SaaS control plane is not required.

The platform also builds requested ARM64/CUDA Python wheels for **Jetson AGX Orin and Jetson Orin Nano** against a customer-defined dependency/software stack. External repositories, package mirrors or CI workers may optionally supply source or candidate artifacts, but those inputs are explicitly versioned and hash-bound before qualification rather than becoming the foundry's control plane.

A custom request can pin the JetPack / Jetson Linux release, CUDA toolkit, Python ABI, PyTorch/framework version, upstream package revision, required native GPU architecture and optional features. Depending on scope, the deliverable can include exact source/dependency locks, wheel SHA-256 identities, build recipes, installation material and physical-device qualification evidence.

Custom Wheel Foundry work is a commercial service, not an expansion of the free support matrix of this repository. **Build success is not treated as qualification.** Qualified release candidates are exercised on physical target hardware through hardware-in-the-loop gates appropriate to their scope, including native-library loading, CUDA execution, package interoperability, fresh-environment installation and, where applicable, real model/application execution. A requested configuration is described as qualified only after its own target-specific evidence gates have passed.

**The proprietary SynRex Custom Wheel Foundry software platform is also available for commercial licensing.** A licensee can operate the local foundry capability in its own engineering environment and connect it to its own Jetson HIL hardware. Licensing or acquisition arrangements are scoped separately from custom wheel-build services and do not transfer or override third-party software licences.

[Request a custom wheel build](https://github.com/Juurikko/jetson-edge-ml-wheelhouse/issues/new?template=commercial-advisory.yml) · [Commercial advisory](COMMERCIAL.md) · [Tuomas Pietilä on LinkedIn](https://www.linkedin.com/in/tuomas-pietila/) · [tuomas.pietila@synrex.fi](mailto:tuomas.pietila@synrex.fi)

## Commercial advisory

The public wheelhouse intentionally supports a very narrow, frozen target. SynRex offers fixed-scope commercial advisory and engineering for adjacent or private deployments, especially where the missing piece is not merely compiling code but making the complete stack defensible on real hardware.

Typical engagements include:

- deployment help for production Jetson systems;
- custom board bring-up and BSP / CUDA / Python stack validation;
- model porting and application-level qualification;
- **Custom Wheel Foundry builds for AGX Orin and Orin Nano at specified dependency/software stacks;**
- **commercial licensing of SynRex's proprietary Custom Wheel Foundry software platform;**
- missing ARM64/CUDA wheel ports and private wheelhouses;
- CI-built versus native-device rebuild comparison;
- hardware-in-the-loop qualification and release evidence;
- LiDAR, robotics, vision and multimodal edge-ML integration.

Use the [commercial advisory request](https://github.com/Juurikko/jetson-edge-ml-wheelhouse/issues/new?template=commercial-advisory.yml) for non-confidential initial scoping, or contact Tuomas Pietilä via [LinkedIn](https://www.linkedin.com/in/tuomas-pietila/) or [tuomas.pietila@synrex.fi](mailto:tuomas.pietila@synrex.fi). See [COMMERCIAL.md](COMMERCIAL.md).

## Installation

The R1 binary assets are published in the [R1 GitHub Release](https://github.com/Juurikko/jetson-edge-ml-wheelhouse/releases/tag/agx-orin-r39.2.1-cu13.2-py312-sm87-r1). Verify hashes and the exact target contract before installation. The convenience bundle contains the eight custom wheels plus qualification evidence; base/vendor dependencies such as PyTorch, SciPy and NVIDIA software are not automatically rehosted.

See [docs/installation.md](docs/installation.md).

## Verification

R1 ships SHA-256 manifests, a machine-readable release-asset record, the frozen target contract, and qualification evidence. The release was downloaded back from GitHub to the physical AGX and verified byte-for-byte before publication.

The repository itself is now guarded by a deterministic `repository-integrity` workflow. It validates the frozen target contract, candidate hashes, source-lock consistency, public-redaction rules, and that binary release payloads have not been committed to Git history.

See [docs/verification.md](docs/verification.md), [the R1 publication record](manifests/release-r1-publication.json), [the frozen R1 candidate manifest](manifests/release-r1-candidates.json), and [source provenance](provenance/README.md).

## Case studies

Two application-level studies are being prepared:

- LitePT-L optimization on AGX Orin, including native SM87 PointROPE and native torch-scatter.
- ECLAIR four-scene point-density operating envelope from native density down to 0.5 pts/m².

These are engineering case studies, not claims that four selected scenes replace the broader ECLAIR benchmark.

See [case-studies/README.md](case-studies/README.md).

## Licensing and redistribution

This repository indexes artifacts derived from multiple upstream projects with different licences. There is deliberately **no blanket repository licence applied to third-party wheel contents**.

The R1 release is accompanied by exact source, licence/notice, qualification and redistribution records. Vendor runtimes such as CUDA/cuDNN/NPP, PyTorch, FFmpeg/GStreamer and NVIDIA cuSPARSELt are treated separately and are not automatically rehosted.

See [NOTICE.md](NOTICE.md), the [R1 notice index](notices/README.md), and the [release asset policy](docs/release-assets.md).

## Support boundary

Public issues are for reproducible defects in the **exact published artifacts on the documented target**. The project does not commit to free troubleshooting for different Jetson models, BSP/CUDA/Python combinations, custom carrier boards, deployment environments or private models.

Deployment assistance, custom board bring-up and model porting are handled through commercial advisory. See [SUPPORT.md](SUPPORT.md).

## Disclaimer

These are unofficial community builds. NVIDIA, PyTorch, PyG, OpenCV, Open3D, LitePT and other upstream projects do not endorse these binaries.
