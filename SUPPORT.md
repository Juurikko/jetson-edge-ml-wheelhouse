# Support policy

The public wheelhouse is intentionally **self-service**.

## Public bug reports

A bug report is in scope when it is reproducible with the exact published wheel bytes on the exact documented target contract and appears to contradict the published qualification claim.

A useful public bug report includes:

- exact wheel filename and SHA-256;
- target-contract details;
- minimal reproduction;
- observed output or traceback;
- expected behavior based on this repository's documented scope.

Use the [qualified-target bug report](https://github.com/Juurikko/jetson-edge-ml-wheelhouse/issues/new?template=qualified-target-bug.yml).

## Out of scope for free support

The following are not treated as general community-support obligations:

- different Jetson models or compute capabilities;
- different BSP, JetPack/L4T, CUDA, Python or PyTorch versions;
- custom carrier-board or peripheral bring-up;
- Docker, service or production deployment integration;
- private dependency conflicts;
- adapting a customer's application or model;
- model conversion / porting;
- performance tuning for a different workload;
- custom wheel builds for another target;
- environment-specific debugging that cannot be reproduced against the published target.

Questions may still be useful signals for future public work, but there is no commitment to investigate, port, maintain or provide timelines through public issues.

## Commercial advisory

**Deployment help, custom board bring-up and model porting are offered via commercial advisory.**

Commercial work can also cover missing ARM64/CUDA wheels, private wheelhouses, HIL qualification, reproducible deployment, runtime closure, release evidence and related edge-ML integration.

See [COMMERCIAL.md](COMMERCIAL.md) or open a [commercial advisory request](https://github.com/Juurikko/jetson-edge-ml-wheelhouse/issues/new?template=commercial-advisory.yml).

## Security and confidential information

Do not post credentials, proprietary source code, private datasets, customer information or confidential hardware details in a public issue.
