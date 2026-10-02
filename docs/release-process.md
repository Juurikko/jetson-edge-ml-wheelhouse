# Public release process

The repository is populated and reviewed before any binary release is published.

## R1 sequence

1. Freeze the exact target contract.
2. Audit redistribution, bundled libraries and public redaction.
3. Create the public repository and protect `main`.
4. Record exact release-candidate wheel identities and qualification evidence.
5. Rebuild any artifact requiring release-hygiene corrections.
6. Requalify the exact replacement bytes on the physical AGX Orin.
7. Verify clean installation from the proposed public artifact set.
8. Create the GitHub Release and upload approved wheel assets.
9. Publish SHA-256 manifests, notices and machine-readable lock data.
10. Add CI verification/attestation and case-study documentation.

## Current status

- repository bootstrap: in progress
- `main` protection: active
- repository-integrity CI: PASS on the bootstrap PR
- PointROPE public-release rebuild: PASS
- cumm public-release replacement: PASS; exact R1P2 bytes physically qualified in R1P3
- Open3D public-release replacement: PASS; full physical AGX CUDA/geometry/Torch requalification complete
- intended custom-wheel set: 8/8 release candidates
- binary GitHub Release: not yet created

No unreleased binary should be referenced by an installation command.
