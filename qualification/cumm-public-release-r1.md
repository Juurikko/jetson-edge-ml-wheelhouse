# cumm 0.8.2 — public release R1

## Result

**PASS — public-release candidate**

```text
cumm_cu132-0.8.2-2agxrelease1-cp312-cp312-linux_aarch64.whl
SHA-256 c3e3ae935079638dc255e3b1a923582787ac2220c8f1f98ab9b717121131c5d9
```

Upstream cumm commit:

```text
4c77b38d1ab57d5d1c157adddf67dad93f3a446b
```

## Why this rebuild exists

The accepted internal cumm wheel was already functional on the AGX Orin path, but the frozen upstream source commit has an Apache-2.0 `LICENSE` while its package metadata still declared MIT.

The public release rebuild corrects that stale packaging metadata while retaining the already-qualified CUDA 13 compatibility adaptation:

- Linux extension build: C++17
- target CUDA architecture: SM87
- JIT disabled for the AOT wheel path
- package licence metadata: Apache-2.0
- Apache-2.0 licence embedded in wheel metadata
- public build number: `2agxrelease1`

The computational cumm source was not intentionally modified by the release-hygiene patch.

## Qualification chronology

### R1

Pre-build harness failure: the LitePT application venv did not contain the cumm build toolchain.

### R1P1

Build reached `build_ext`, then stopped because the accepted Wheel Factory venv's `ninja` executable was not exposed on `PATH`.

### R1P2

The exact replacement wheel was successfully built and passed:

- corrected Apache-2.0 package metadata;
- embedded licence presence;
- AArch64 native-object audit;
- isolated cumm + accepted spconv installation.

R1P2 then stopped during physical qualification because the deliberately `--no-deps` qualification target did not itself contain `pccm`.

### R1P3

No rebuild was performed. The exact R1P2 wheel bytes were frozen and qualified using a provenance-checked runtime dependency overlay from the accepted SynRex Wheel Factory environment.

The overlay preserved the frozen application environment's Torch/NumPy while supplying otherwise-missing cumm runtime support packages such as pccm/ccimport.

## Physical qualification

The exact public wheel passed:

- R1P2 static metadata audit;
- AArch64 ELF audit;
- runtime dependency-overlay provenance gate;
- physical cumm TensorView CPU → CUDA → CPU copy on Orin;
- accepted spconv CUDA compatibility smoke using the replacement cumm wheel.

Final status:

```text
CUMM_PHYSICAL_TENSORVIEW_SMOKE=PASS
SPCONV_COMPATIBILITY_CUDA_SMOKE=PASS
CUMM PUBLIC-RELEASE R1P3 QUALIFICATION COMPLETE
NO REBUILD PERFORMED
```

## Evidence hashes

```text
public release wheel
c3e3ae935079638dc255e3b1a923582787ac2220c8f1f98ab9b717121131c5d9

R1P2 static wheel audit
3145a10d207d51d2453efd96e319f81ec2da88a14e04d2d68b4fb1bcbbb1a649

R1P3 runtime dependency overlay
c25729d11534e62cf002596ee83b11b89d539dc5ee00cfb5aa82b7fcf92a8381

R1P3 physical TensorView smoke
48250db6a4710978d1c4a11ec7cb0f2335ac29c02a092abbf001fb2d5656bdc2

R1P3 spconv compatibility smoke
569a2f16b05ca6cddbf5d4f841a25ae3a7039180dd40525b5856f994cb34b314

R1P3 release-candidate record
df56fdeb404d771c97300f03fae69af4eaa6a8317d74ed1779c12c9cc866a2cd

R1P3 qualification bundle
830b446658691195e1b25f3c7f69ce74c5bd854285576253690945e302408c32
```

## Claim boundary

This qualification establishes the exact public cumm wheel on the frozen AGX Orin target and its TensorView/spconv compatibility path. It is not a blanket claim for every cumm operation, GPU architecture, CUDA release, or Jetson model.
