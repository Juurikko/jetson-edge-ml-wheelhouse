# Verification

The wheelhouse is evidence-first.

Each public release will pin:

- target contract;
- wheel filename and SHA-256;
- upstream source commit;
- patch SHA-256 where relevant;
- build origin;
- licence/notice closure;
- physical qualification level and scope.

## Core rules

- Build success is not physical GPU qualification.
- Physical GPU execution is not application correctness.
- Cross-device output parity is not semantic accuracy.
- A test-harness failure is not automatically an artifact failure.
- Previously accepted evidence is never overwritten by a correction.

The first release will add automated target comparison and release-manifest verification tools.
