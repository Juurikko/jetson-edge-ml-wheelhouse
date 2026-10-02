# Reproducibility policy

The first release is built around exact identity rather than floating package names.

For each artifact we record, where applicable:

- upstream repository;
- exact commit SHA;
- local patch SHA-256;
- exact wheel filename;
- exact wheel SHA-256;
- build origin;
- target contract;
- physical qualification scope.

Corrections are versioned rather than overwriting accepted or failed evidence.

For native-AGX artifacts we do not retroactively claim GitHub Actions provenance. For GitHub-CI artifacts we separately require physical AGX qualification before making device-level claims.
