# Public release process

The repository is populated and reviewed before any binary release is published.

## R1 sequence

1. Freeze the exact target contract. **PASS**
2. Audit redistribution, bundled libraries and public redaction. **PASS**
3. Create the public repository and protect `main`. **PASS**
4. Record exact release-candidate wheel identities and qualification evidence. **PASS**
5. Rebuild any artifact requiring release-hygiene corrections. **PASS**
6. Requalify the exact replacement bytes on the physical AGX Orin. **PASS**
7. Verify clean installation from the proposed public artifact set. **PASS**
8. Create the GitHub Release and upload approved wheel assets. **PASS**
9. Download the draft release back to the AGX and SHA-256 verify all 15 assets. **PASS**
10. Publish the verified draft and bind the named Git tag to the reviewed release commit. **PASS**
11. Keep CI verification, documentation and case-study material current after publication.

## Published R1 identity

```text
tag
agx-orin-r39.2.1-cu13.2-py312-sm87-r1

release id
402213618

release commit
41f9887a4b5b94d07603a9aa09452767a0870624

published at
2026-10-02T23:40:32Z

asset count
15
```

Release:

https://github.com/Juurikko/jetson-edge-ml-wheelhouse/releases/tag/agx-orin-r39.2.1-cu13.2-py312-sm87-r1

## Current status

- repository bootstrap: complete
- `main` protection: active
- repository-integrity CI: PASS on the bootstrap publication commit path
- PointROPE public-release rebuild: PASS
- cumm public-release replacement: PASS; exact R1P2 bytes physically qualified in R1P3
- Open3D public-release replacement: PASS; full physical AGX CUDA/geometry/Torch requalification complete
- intended custom-wheel set: 8/8 exact published wheels
- exact eight-wheel clean-install on physical AGX: PASS
- AGX-generated final release manifest frozen by SHA-256
- final manifest / clean-install receipt / evidence bundle preserved and independently verified off-device: PASS
- GitHub draft upload: 15/15 assets uploaded
- AGX round-trip download / SHA-256 verification: PASS
- named release tag bound to the exact reviewed commit: PASS
- binary GitHub Release: **published**
- R1 machine-readable publication record: [../manifests/release-r1-publication.json](../manifests/release-r1-publication.json)

The R1 publication workflow therefore distinguishes four separate gates: build success, physical qualification, release-asset byte identity, and final publication state.
