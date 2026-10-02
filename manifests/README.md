# Release manifests

This directory contains machine-readable release planning and lock data.

## Current manifest

`release-r1-candidates.json` records the intended R1 artifact set and each artifact's current release state.

The candidate manifest is deliberately separate from the eventual immutable release manifest. While an artifact is being rebuilt or requalified, it remains `release_pending_rebuild`. Only exact qualified bytes may move to `release_candidate`.

## Identity rules

- use basenames, never private filesystem paths;
- SHA-256 identifies exact binary bytes;
- source identity uses full 40-character Git commit SHAs;
- wheel binaries live in GitHub Releases, not Git history;
- vendor/base dependencies may be hash-pinned without being rehosted;
- the final release manifest must be generated from the exact approved asset set, not inferred from package versions.
