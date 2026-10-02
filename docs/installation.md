# Installation

> No binary GitHub Release is published yet.

The first release will provide:

1. individual approved wheel assets;
2. a complete offline wheelhouse bundle;
3. SHA-256 manifests;
4. a machine-readable target contract;
5. deterministic install ordering;
6. target and artifact verification tools.

The release flow will require verification **before** installation.

Planned flow:

```bash
gh release download <release-tag> --repo Juurikko/jetson-edge-ml-wheelhouse
sha256sum -c SHA256SUMS
python tools/doctor.py
```

Do not use unreleased hashes or internal development paths as install instructions.
