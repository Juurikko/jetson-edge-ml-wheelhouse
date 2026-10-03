# CI iteration notes

These are development notes, not physical qualification records. Do not edit or replace the accepted R1 evidence with this material.

## Run 1: 37128943758

Factory commit: `b5a75f6f610a3647d9aa1f77d951e2c9da7df732`.

Actions run: https://github.com/Juurikko/jetson-edge-ml-wheelhouse/actions/runs/37128943758

Result: **FAIL before FlashAttention compilation**, on `pip check`.

Passed: existing public repository integrity; unchanged R1 manifests/provenance/qualification/target contract; all ten factory unit tests; exact annotated FA2 tag, peeled commit, original setup.py blob and CUTLASS gitlink; independently reapplied minimal patch; all seven SHA256-locked CUDA archives; exact native compiler/Torch/Python preflight.

The real runner was `ubuntu-24.04-arm`, image `20260927.135.1`, Ubuntu 24.04.5, Python 3.12.3, GCC/G++ 13.3.0, glibc 2.39, approximately 15 GiB RAM and 116 GiB available disk after disposable SDK/cache cleanup. The hosted Azure kernel is not the deployment's Tegra kernel and is not represented as such.

The failing line was:

```text
nvidia-cusparselt-cu13 0.8.1 is not supported on this platform
```

The official input filename was ARM64 and Torch had already imported successfully, but neither fact alone justifies ignoring a dependency failure. Commit `e3214a869926c78477ea3b92a43c335ec4c40445` adds a narrow diagnostic gate. It requires this exact sole warning and exit code, the exact cuSPARSELt archive SHA256, the recorded ARM64 URL, the installed version, original internal WHEEL tags that reproduce the unsupported-tag warning, and independently verified AArch64 machine IDs for every installed cuSPARSELt ELF. The original metadata and raw `pip check` result are retained. No metadata or library is rewritten. All other failures still stop.

Run 1 diagnostic artifact ID: `11276360853`.

Artifact ZIP SHA256: `6d710e8c34ffef0f16d7b5f257904e85039533eea737dd76e60fbbac42813274`.

This artifact contains preparation/provenance diagnostics, **not a FlashAttention wheel**.

## Identities measured and frozen after run 1

Minimal setup.py patch SHA256:

`3cad833188ecc3e4fe9f8d9c0c45dea141e03de40421cf36eb819dacc708d5bd`

The exact emitted patch is now tracked at `patches/0001-sm87-cxx20.patch`; `prepare.py` rejects any regenerated-patch digest drift.

Official Torch ARM64/cp312 wheel SHA256:

`ace5d911d05b47e8c673ade02ff1736c70c66c3fa97cf85fe3d70d28c302799c`

Exact NVIDIA cuSPARSELt input SHA256:

`4dca476c50bf4780d46cd0bfbd82e2bc10a08e4fef7950917ce8d7578d22a23f`

## Compiler and runtime distinction

The compiler, CRT, CUDA headers, CUDA runtime archive, CCCL, cuobjdump, nvdisasm and NVVM provisioned by this factory are individually hash-locked NVIDIA CUDA 13.2.2 redistribution components at **13.2.86**. `CUDA_HOME` points only to that compiler prefix. The compiler version and SM87 flags are checked before compilation and again during final audit.

The official Torch `2.14.0+cu132` wheel's metadata independently requests the pip `cuda-toolkit==13.2.1` runtime dependency set. In run 1 this included CUDA runtime 13.2.75, NVRTC 13.2.78 and cuSPARSELt 0.8.1, alongside Torch's other external libraries. Some of Torch's dependency requirements are ranges; the actual resolved versions and available archive hashes are retained in pip reports and the installed environment inventory. These packages do not supply or replace the selected nvcc. They are not bundled into the FlashAttention wheel, and this workflow does not install them on a Jetson.

Do not claim bit-for-bit reproducibility across independent machines or a fully frozen transitive Python dependency closure solely from version pins. The source/compiler/Torch identities are frozen, and each attempt records its actual dependency closure for review. Physical CUDA runtime compatibility is a separate later qualification gate.

## Run 2

Factory commit: `e3214a869926c78477ea3b92a43c335ec4c40445`.

Actions run: https://github.com/Juurikko/jetson-edge-ml-wheelhouse/actions/runs/37130165121

Triggered by a real development-branch push. Consult the run conclusion and its artifact's final `build-manifest.json`; launching the run is not `CI_BUILD_VALIDATED` evidence.

## Device boundary

No physical AGX command, installation, package rebuild, firmware operation or GPU test has been executed by this project phase. `qualify_agx.py` and `litept_anchor.py` are prepared source code only. Full official LitePT qualification requires a reviewed real checkpoint and post-transform sample with frozen hashes, pristine official model source, and the already-qualified dependency wheels. Missing inputs or dependencies must stop, not be replaced with synthetic application evidence or fake imports.
