# Verification

The wheelhouse is evidence-first.

Each public release pins:

- target contract;
- wheel filename and SHA-256;
- upstream source commit;
- patch SHA-256 where relevant;
- build origin;
- licence/notice closure;
- physical qualification level and scope;
- published GitHub release identity.

## Core rules

- Build success is not physical GPU qualification.
- Physical GPU execution is not application correctness.
- Cross-device output parity is not semantic accuracy.
- A test-harness failure is not automatically an artifact failure.
- Previously accepted evidence is never overwritten by a correction.
- Publication is a separate gate from qualification.

## R1 publication verification

R1 is published at:

https://github.com/Juurikko/jetson-edge-ml-wheelhouse/releases/tag/agx-orin-r39.2.1-cu13.2-py312-sm87-r1

The public release is bound to:

```text
release id
402213618

tag
agx-orin-r39.2.1-cu13.2-py312-sm87-r1

commit
41f9887a4b5b94d07603a9aa09452767a0870624

asset count
15
```

Before publication, all 15 draft assets were downloaded back to the physical AGX and verified against the frozen local SHA-256 identities.

The frozen draft round-trip receipt has SHA-256:

```text
da43a52caf950f5248f08c7f2f1293ce0919b6f79d67357b0ba30be47a580c55
```

The local final publication receipt has SHA-256:

```text
6b540a94342c654c23a74599142cf3391db70c51f8cc588b572a224440196291
```

See [../manifests/release-r1-publication.json](../manifests/release-r1-publication.json), [../qualification/r1-clean-install.md](../qualification/r1-clean-install.md), and [release-assets.md](release-assets.md).

## User-side verification

When all R1 release assets are downloaded into one directory:

```bash
sha256sum -c SHA256SUMS_R1.txt
```

Every listed asset should report `OK`. Exact wheel hashes are also listed in [../wheels/README.md](../wheels/README.md).
