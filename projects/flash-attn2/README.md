# FlashAttention-2 / ARM64 / CUDA 13.2.86 / SM87

Implementation branch: `build/flash-attn2-cu132-sm87-r0`.

This is an isolated candidate project, not an addition to the physically qualified R1 release. The first public ARM64 Actions build was triggered by commit `b5a75f6f610a3647d9aa1f77d951e2c9da7df732`. Consult the exact Actions run conclusion and its build manifest; this README is not evidence that compilation or physical qualification passed.

## Frozen scope

Jetson AGX Orin 64 GB, JetPack 7.2.1, L4T R39.2.1, Ubuntu 24.04, Linux AArch64, CPython 3.12.3, GCC/G++ 13.3.0, CUDA nvcc 13.2.86, PyTorch 2.14.0+cu132, CXX11 ABI enabled, SM87 SASS only. The existing repository target contract remains unchanged.

FlashAttention-2 is pinned to upstream tag `v2.8.3.post1`, annotated tag object `91ffc2ac7c36f333efa23bde332ba2727a39d093`, commit `a8aa52b1ab3e9ca574c8a33b3f35afc017ffa2e2`. CUTLASS is pinned to the upstream gitlink `dc4817921edda44a549197ff3a9dcf5df0636e7b`. No FA3/Hopper or FA4/Blackwell replacement is used.

The stable tag exposes `FLASH_ATTN_CUDA_ARCHS` but does not implement an `87` branch. The local recipe adds only explicit `arch=compute_87,code=sm_87` selection. It also minimally backports the Linux C++20 selection required by Torch 2.14 from upstream PR 2879. No CUDA kernel, runtime dispatch, dtype, backward, dropout or head-dimension feature is disabled or rewritten in this initial patch. Source filenames ending in `_sm80.cu` denote upstream Ampere template translation units, not the emitted GPU architecture; the latter is independently checked in the compiled ELF.

CUDA toolkit release **13.2.2** supplies the required nvcc **13.2.86**. Using toolkit 13.2.0 or 13.2.1 would silently change the compiler. The recipe instead downloads seven individually SHA256-locked native `linux-sbsa` redistribution archives, including the separately packaged NVVM compiler. It does not install CUDA drivers.

## Actual implementation

- `source-lock.json`, `cuda-inputs.lock.json`: pristine source, target, compiler archives and compatibility policy.
- `prepare.py`: validates exact source/tag/gitlink identities, exports CUDA-only build sources without fetching ROCm CK, applies three exact setup.py replacements, emits and independently reapplies a unified patch, records its SHA256 and all exported source files, and provisions the locked compiler.
- `build.sh`: installs exact Torch and build-tool versions into a disposable venv; records pip input hashes; runs an SM87 FP16/BF16 type compilation probe; compiles the real upstream extension with `MAX_JOBS=2`, `NVCC_THREADS=1`, no build isolation and no prebuilt fallback.
- `validate.py`: gates CPU/Python/compiler/Torch ABI, wheel RECORD, ELF dependencies, SM87 SASS, absence of PTX, compiler flags, licenses and mandatory provenance. Only its final successful audit can write a `CI_BUILD_VALIDATED` manifest.
- `test_factory.py`: negative tests for patch context drift, extra/missing GPU architectures, PTX, malformed ELF, unsafe wheel paths and altered wheel RECORD hashes.
- `qualify_agx.py`, `litept_anchor.py`: offline device-phase tests; never invoked by CI, and never install or rebuild dependencies.

The workflow uses the public `ubuntu-24.04-arm` allocation, a bounded two-job/one-nvcc-thread build, and disposable runner SDK/cache cleanup. Runs are serialized on this branch. A 12 GiB memory-class and 12 GiB free-disk minimum are checked before the heavy build. This is not a self-hosted runner workflow.

## Trigger and evidence

Push a code/lock/workflow correction to this branch to trigger the build. Documentation-only Markdown changes do not restart it. A manual `workflow_dispatch` entry is also present; GitHub's UI availability for a branch-only workflow depends on workflow registration. The initial build was triggered by a real push, not a simulated dispatch.

The artifact is named `flash-attn2-sm87-attempt-<run-id>-<attempt>`. An attempt artifact may contain failure diagnostics. Its existence alone does **not** mean a validated wheel exists.

A successful bundle contains:

```text
wheel/flash_attn-2.8.3.post1+cu132torch214.sm87.synrex0-cp312-cp312-linux_aarch64.whl
build-manifest.json
SHA256SUMS
evidence/source-lock.resolved.json
evidence/upstream.patch
evidence/source-file-inventory.json
evidence/cuda-inputs.json
evidence/cuda-redist-index.json
evidence/build-environment.json
evidence/build.log
evidence/build.ninja.txt
evidence/compile-commands.txt
evidence/torch-install-report.json
evidence/build-tools-install-report.json
evidence/pip-inspect.json
evidence/pip-freeze.txt
evidence/wheel-content-inventory.json
evidence/elf-inventory.json
evidence/elf-header.txt
evidence/elf-dynamic.txt
evidence/elf-versions.txt
evidence/dependency-ldd.txt
evidence/cuda-elf-list.txt
evidence/cuda-ptx-list.txt
evidence/cuda-resource-usage.txt
evidence/licenses/
evidence/factory/
```

The resolved source lock replaces the recipe's derived-patch marker with the actual patch SHA256 and patched setup.py digest. The factory Git commit and exact original source Git blob bind the deterministic patch recipe before compilation. Input download reports retain the resolved Torch/build dependency hashes; bit-for-bit reproducibility across independent builders is not claimed until separately demonstrated.

Both wheel filename and internal RECORD are checked. Every ELF must be the expected AArch64 extension. Unexpected bundled libraries, unreviewed ELF dependencies/RPATH, non-SM87 device code, PTX, Torch/CUDA/compiler drift and missing provenance fail closed. A native hosted runner still has no Orin GPU: the compiler probe and ELF inspection are not CUDA runtime tests.

## State boundaries

| State | Required evidence |
|---|---|
| `CI_BUILD_VALIDATED` | Exact source and ABI checks, successful wheel compilation, complete static/package/device-code audit. Maps to existing Q1 scope only. |
| `CANDIDATE_NOT_PHYSICALLY_QUALIFIED` | Mandatory physical state of every cloud-produced candidate, including a green CI artifact. |
| `PHYSICAL_AGX_QUALIFIED` | Exact candidate bytes installed on the frozen AGX; hardware/stack checks, numerical tests, backward smoke, exact already-qualified R1 dependency checks, and the frozen official LitePT inference anchor all pass. |

This workflow has read-only repository permissions and no release-publishing step. A later publication requires separate review and explicit authorization. Main, published release assets, R1 source locks, hashes and qualification records are preserved.

## Later AGX phase: explicit and offline

**Do not run this phase during the initial cloud build.** The harness has not itself been physically qualified. A later authorized session must prepare an isolated candidate environment without altering the accepted R1 environment, install only the exact candidate with dependency resolution disabled, and supply existing qualified R1 wheels for byte checks. This project neither rebuilds nor replaces cumm, spconv, PointROPE, PyG, OpenCV or Open3D.

Required application anchor inputs are a pristine local checkout of official LitePT at the pinned commit, a real pretrained model checkpoint, a real post-transform sample tensor dictionary, and a specification frozen before execution. Keep checkpoint/sample/specification files outside the pristine LitePT tree. The checkpoint must be readable with `torch.load(weights_only=True)` and must strictly match the official ScanNet small-v1m1 model. The sample must contain CPU tensors including `feat`, `grid_coord`, and `offset`, as consumed by the official model; preprocessing and semantic accuracy are outside this first anchor's scope.

Example specification structure (replace descriptions and hashes with actual reviewed values; these placeholders cannot pass):

```json
{
  "schema": "synrex.litept.flash_attn_anchor.v1",
  "litept_commit": "436d04801c8151faebe66a1b2d368a9711e7e6aa",
  "config": "configs/scannet/semseg-litept-small-v1m1.py",
  "config_sha256": "REQUIRED_SHA256",
  "synthetic_input": false,
  "dataset_description": "REQUIRED_REAL_SAMPLE_PROVENANCE",
  "checkpoint_origin": "REQUIRED_PRETRAINED_CHECKPOINT_PROVENANCE",
  "checkpoint": {"file": "checkpoint.pth", "sha256": "REQUIRED_SHA256"},
  "sample": {"file": "post_transform_sample.pt", "sha256": "REQUIRED_SHA256"}
}
```

From the prepared AGX candidate venv, the later explicit command is:

```bash
python /path/to/bundle/evidence/factory/qualify_agx.py \
  --execute-on-agx \
  --bundle /path/to/bundle \
  --r1-wheelhouse /path/to/existing-qualified-r1-wheels \
  --litept-repo /path/to/pristine-LitePT \
  --anchor-spec /path/to/frozen-anchor.json \
  --output /path/to/new-qualification-evidence
```

The output directory must not already exist. No old evidence is overwritten. FP16 and BF16 forward checks include head dimensions 18 (official LitePT), 32, 64, 128, 192 and 256, causal/noncausal cases, and variable-length packed input. Backward is a bounded head64/no-dropout smoke test, not universal training qualification. The official model run counts FlashAttention, PointROPE and spconv calls; then reruns identical weights/input/RNG with an independent FP32 math attention reference. The frozen model-output gates are `rtol=0.02`, `atol=0.02` and zero changed class IDs. Any failure stops promotion; tolerances are not relaxed automatically.

Official LitePT's imports also include `pointops` and Python framework utilities. A missing already-existing application dependency must be reported explicitly; the harness does not fake optional imports or install/rebuild them. Large-head shared-memory behavior and the full device import/runtime ABI remain physical test questions until that phase executes.
