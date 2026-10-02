# Release asset policy

Binary wheels are published as **GitHub Release assets**, never committed to repository history.

## Planned R1 release

Planned tag:

```text
agx-orin-r39.2.1-cu13.2-py312-sm87-r1
```

The release should contain:

- each approved exact `.whl`;
- `SHA256SUMS`;
- frozen target contract;
- final wheelhouse lock;
- qualification summary;
- source/patch provenance;
- licence / third-party notice bundle;
- SBOM or equivalent package inventory where practical;
- clean-install verification receipt.

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
