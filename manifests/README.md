# Release manifests

This directory contains machine-readable planning, freeze and publication records.

## R1 records

`release-r1-candidates.json` is the pre-publication candidate snapshot. It records the eight exact wheel candidates that passed qualification before the public GitHub Release was created.

`release-r1-freeze-receipt.json` is the pre-publication freeze receipt. Its `release_created=false` and `binary_assets_published=false` fields are intentionally preserved because they describe the state at the freeze gate.

`release-r1-publication.json` is the post-publication record. It binds the public GitHub Release ID, tag, reviewed commit, publication timestamp, exact 15-asset set, draft round-trip verification receipt and final publication receipt.

These records are complementary rather than replacements for one another.

## Identity rules

- use basenames, never private filesystem paths;
- SHA-256 identifies exact binary bytes;
- source identity uses full 40-character Git commit SHAs;
- wheel binaries live in GitHub Releases, not Git history;
- vendor/base dependencies may be hash-pinned without being rehosted;
- the final release manifest must be generated from the exact approved asset set, not inferred from package versions;
- pre-publication freeze records remain immutable after publication;
- publication state is recorded separately so historical freeze evidence is not rewritten.
