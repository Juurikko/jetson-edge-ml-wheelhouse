# Release asset policy

Binary wheels are published as **GitHub Release assets**, never committed to repository history.

## Planned R1 release

Planned tag:

```text
agx-orin-r39.2.1-cu13.2-py312-sm87-r1
```

The exact eight-wheel candidate set has now passed clean-install qualification on the physical AGX. The release should contain:

- each approved exact `.whl`;
- `SHA256SUMS`;
- frozen target contract;
- final wheelhouse lock;
- qualification summary;
- source/patch provenance;
- licence / third-party notice bundle;
- SBOM or equivalent package inventory where practical;
- clean-install verification receipt.

The AGX-generated final release manifest is frozen at SHA-256 `5477ecb13707194157a56b0d68ee4bb0af15b1c63ce226addd5decec101c3ec2`. The clean-install receipt is SHA-256 `ab85d9c77a1230279dedec168b333f73416d3921bb691831af87a1bb0d4075ea`.

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

Human-readable versions are useful labels, but exact SHA-256 and source commit identity are authoritative.
