# R1 exact 8-wheel clean-install qualification

## Result

**PASS**

```text
EXACT_8_WHEEL_CLEAN_INSTALL=PASS
RELEASE_CANDIDATE_COUNT=8
```

Target:

```text
NVIDIA Jetson AGX Orin 64 GB
Linux aarch64
L4T R39.2.1
CUDA 13.2.86
CPython 3.12.3
SM87
```

## Scope

A fresh Python 3.12 virtual environment was created on the physical AGX Orin. The release-candidate set was installed using local frozen artifacts only with `pip --no-index`.

The gate bound the installation to the exact eight public candidate wheel hashes, verified the frozen Torch/SciPy base, recreated the already-qualified OpenCV media-runtime overlay, ran `pip check`, exercised all eight packages in one environment, and tested multiple fresh-process import orders for native-runtime collisions.

The exact custom-wheel set was:

1. torch-scatter
2. torch-sparse
3. torch-cluster
4. spconv
5. PointROPE
6. cumm
7. OpenCV CUDA
8. Open3D CUDA

## Qualification gates

The clean-install workflow required:

- frozen target identity;
- CUDA toolkit identity;
- exact 8-wheel candidate staging;
- exact link-only Torch and SciPy base artifacts;
- frozen OpenCV media-runtime overlay;
- fresh Python 3.12 venv;
- offline install and `pip check`;
- installed-package binding to the exact candidate wheel SHA-256 values;
- frozen Python stack identity;
- single-environment CUDA/package smoke;
- fresh-process import-order collision tests.

Final marker:

```text
SYNREX R1 CLEAN-INSTALL QUALIFICATION COMPLETE
EXACT_8_WHEEL_CLEAN_INSTALL=PASS
RELEASE_CANDIDATE_COUNT=8
```

## Evidence hashes

```text
candidate set
0eab11ceea1ca703aaf74a04a949a815b0b2caa712e911f182136cef4566819f

pip check
9261363b733079a641c2e4cc9bc46ffa1d8336945a87f807b6cf68847dbc9b09

pip freeze
7ff4c8726cf1d00b8818c1d33fe74a43523c3b1cfb4e7417543c0397bcc5e151

installed candidate binding
a68f132904d636e9c31aedc5d48e49a9caad4c7bcf51e794cd20b7344e68bfd7

runtime library path
1490e3485869038552ad3591bf9427319a82a8e87e588b1d5e5a4295c999f254

frozen stack
eab646128aa3faa0f6654a4858d3e63d463ad1dbff2f1cc8ac0b4dcee2949b78

single-environment smoke
4774251161deb9378ff91865d8956f1e2ffc1b4f251c8fe4f4fb29183bb1ace7

import-order collision
7bd6f5733d69ae2f9e6dfb40cdd2373dd010fe1b90b9abd248b0d410fc597027

clean-install receipt
ab85d9c77a1230279dedec168b333f73416d3921bb691831af87a1bb0d4075ea

AGX-generated final release manifest
5477ecb13707194157a56b0d68ee4bb0af15b1c63ce226addd5decec101c3ec2

clean-install evidence bundle
af463e20d059236da523e748fce571d640210191f7eb2549a4e907cb8907abfa
bytes 11788
```

## Off-device preservation

The final manifest, clean-install receipt and evidence bundle were copied off the AGX to the operator workstation and independently re-hashed:

```text
R1_FINAL_EVIDENCE_OFF_DEVICE=PASS
```

Verified identities:

```text
FINAL_RELEASE_MANIFEST_R1.json
5477ecb13707194157a56b0d68ee4bb0af15b1c63ce226addd5decec101c3ec2

CLEAN_INSTALL_RECEIPT_R1.json
ab85d9c77a1230279dedec168b333f73416d3921bb691831af87a1bb0d4075ea

SYNREX_R1_CLEAN_INSTALL_EVIDENCE.tar.gz
11788 bytes
af463e20d059236da523e748fce571d640210191f7eb2549a4e907cb8907abfa
```

## Claim boundary

This gate qualifies the exact eight-wheel candidate set as an installable combined environment on the frozen AGX target. It is not a blanket compatibility claim for other BSPs, Python versions, CUDA versions, Jetson models or package combinations.
