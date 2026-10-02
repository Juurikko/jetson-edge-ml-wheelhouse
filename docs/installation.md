# Installation

R1 is published at:

https://github.com/Juurikko/jetson-edge-ml-wheelhouse/releases/tag/agx-orin-r39.2.1-cu13.2-py312-sm87-r1

Tag:

```text
agx-orin-r39.2.1-cu13.2-py312-sm87-r1
```

Qualified target:

```text
NVIDIA Jetson AGX Orin 64 GB
JetPack 7.2.1
Jetson Linux / L4T R39.2.1
Linux aarch64
Ubuntu 24.04.4 LTS
CUDA 13.2.86
CPython 3.12.3
PyTorch 2.14.0+cu132
SM87 / compute capability 8.7
```

Nearby configurations may work, but they are not qualified by this release unless explicitly documented.

## Download

With GitHub CLI:

```bash
TAG=agx-orin-r39.2.1-cu13.2-py312-sm87-r1
REPO=Juurikko/jetson-edge-ml-wheelhouse

mkdir -p synrex-r1
cd synrex-r1

gh release download "$TAG" --repo "$REPO"
```

This downloads all 15 published assets: eight custom wheels, the convenience bundle, and the release/qualification evidence files.

The convenience bundle is:

```text
SYNREX_AGX_ORIN_R1_8_WHEEL_BUNDLE.tar.gz
SHA-256 7822dc319af66b02b5fb4722707aad6c0f588f3eea22a50d2887288ee933f5d3
bytes 511233267
```

## Verify before installation

After downloading all release assets into one directory:

```bash
sha256sum -c SHA256SUMS_R1.txt
```

The command must report `OK` for every listed asset.

The authoritative exact wheel hashes are also documented in [../wheels/README.md](../wheels/README.md), and the published release identity is recorded in [../manifests/release-r1-publication.json](../manifests/release-r1-publication.json).

## Dependency boundary

This release is **not** a redistribution of the complete JetPack/PyTorch environment.

The published custom wheels were qualified against the frozen target stack, but base/vendor dependencies such as PyTorch, SciPy, CUDA, cuDNN, NPP, NVIDIA cuSPARSELt and system multimedia/runtime libraries remain separately sourced and subject to their own licences.

Do not assume that `pip install *.whl` into an arbitrary Jetson environment reproduces the qualified stack. First match the documented target and required base dependencies, then install only the custom wheel set appropriate to that environment.

## Qualification boundary

The exact eight-wheel R1 set passed:

- hash binding to the frozen release candidates;
- fresh combined installation on the physical AGX Orin;
- package/runtime interoperability checks;
- hardware-in-the-loop CUDA/application gates appropriate to each artifact;
- GitHub upload followed by AGX round-trip download and SHA-256 verification before publication.

Build success alone is not treated as qualification.

See [../qualification/r1-clean-install.md](../qualification/r1-clean-install.md), [verification.md](verification.md), and [release-assets.md](release-assets.md).
