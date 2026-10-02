# Release asset policy

Binary wheels are published as **GitHub Release assets**, never committed to repository history.

## Published R1 release

Tag:

```text
agx-orin-r39.2.1-cu13.2-py312-sm87-r1
```

Release:

https://github.com/Juurikko/jetson-edge-ml-wheelhouse/releases/tag/agx-orin-r39.2.1-cu13.2-py312-sm87-r1

Release ID: `402213618`

Published commit:

```text
41f9887a4b5b94d07603a9aa09452767a0870624
```

Published at: `2026-10-02T23:40:32Z`

The exact eight-wheel set passed clean-install qualification on the physical AGX Orin before publication. The release was then uploaded to GitHub, downloaded back to the AGX, and SHA-256 round-trip verified before the draft was published.

## R1 asset set

The public release contains exactly 15 assets:

- eight exact qualified `.whl` files;
- `SYNREX_AGX_ORIN_R1_8_WHEEL_BUNDLE.tar.gz`;
- `CLEAN_INSTALL_RECEIPT_R1.json`;
- `FINAL_RELEASE_MANIFEST_R1.json`;
- `RELEASE_ASSETS_R1.json`;
- `RELEASE_README_R1.txt`;
- `SHA256SUMS_R1.txt`;
- `SYNREX_R1_CLEAN_INSTALL_EVIDENCE.tar.gz`.

Convenience bundle:

```text
SYNREX_AGX_ORIN_R1_8_WHEEL_BUNDLE.tar.gz
bytes 511233267
SHA-256 7822dc319af66b02b5fb4722707aad6c0f588f3eea22a50d2887288ee933f5d3
```

Frozen qualification evidence:

```text
FINAL_RELEASE_MANIFEST_R1.json
SHA-256 5477ecb13707194157a56b0d68ee4bb0af15b1c63ce226addd5decec101c3ec2

CLEAN_INSTALL_RECEIPT_R1.json
SHA-256 ab85d9c77a1230279dedec168b333f73416d3921bb691831af87a1bb0d4075ea

SYNREX_R1_CLEAN_INSTALL_EVIDENCE.tar.gz
bytes 11788
SHA-256 af463e20d059236da523e748fce571d640210191f7eb2549a4e907cb8907abfa
```

The machine-readable publication record is [../manifests/release-r1-publication.json](../manifests/release-r1-publication.json).

## Repository versus release

Git history contains small, reviewable text artifacts:

- manifests;
- source locks;
- build recipes and patches;
- qualification summaries;
- verification tools;
- documentation.

GitHub Releases contain large binary artifacts.

The repository-integrity CI rejects tracked wheel/archive/shared-library payloads so accidental binary commits fail before merge.

## No floating identity

Human-readable versions are useful labels, but exact SHA-256, source commit identity, target contract and the published release commit are authoritative.
