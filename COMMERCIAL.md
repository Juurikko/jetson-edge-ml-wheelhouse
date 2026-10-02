# Commercial advisory

**Engineering lead & contact:** [Tuomas Pietilä on LinkedIn](https://www.linkedin.com/in/tuomas-pietila/)

This repository is a public engineering reference for a narrowly qualified Jetson AGX Orin stack. It demonstrates how SynRex Oy approaches unsupported edge-ML software: exact source identity, controlled ARM64/CUDA builds, physical-device qualification, application-level testing and release evidence.

It is **not** intended to turn every adjacent Jetson configuration into a community-supported target.

## Where commercial advisory fits

Commercial advisory is appropriate when you need help turning a promising build into a usable deployment, for example:

- **deployment help** — packaging, runtime closure, offline installation, service/container integration and reproducible deployment;
- **custom board bring-up** — carrier-board or platform-specific validation, BSP/runtime integration and hardware-dependent troubleshooting;
- **model porting** — moving an existing model or pipeline onto a Jetson target and proving the relevant CUDA/application path;
- **missing wheel / dependency enablement** — ARM64/CUDA/Python ports for exact target combinations;
- **private wheelhouses** — customer-specific artifact sets, source locks, hashes and installation manifests;
- **qualification** — physical HIL tests, import-order/runtime collision checks, numerical or application parity and performance evidence;
- **release engineering** — reproducible build recipes, SBOM/licence closure and auditable release bundles.

LiDAR, robotics, computer vision and other sensor-heavy edge-ML applications are particularly suitable where model code, CUDA dependencies and real device behavior all need to work together.

## Engagement boundary

The public artifacts remain self-service and are provided within their stated qualification scope. A public issue does not create a support obligation, SLA or commitment to port an unsupported environment.

Commercial work is scoped separately around a defined target, deliverable and evidence level. Depending on the task, the deliverable may be a wheel, private wheelhouse, build recipe, deployment bundle, qualification report, application port or a bounded advisory engagement.

## Starting a conversation

Open a [commercial advisory request](https://github.com/Juurikko/jetson-edge-ml-wheelhouse/issues/new?template=commercial-advisory.yml) with only **non-confidential** information, or connect with [Tuomas Pietilä on LinkedIn](https://www.linkedin.com/in/tuomas-pietila/).

Useful initial details are:

- Jetson / board model and carrier board;
- JetPack/L4T or BSP version;
- CUDA version;
- Python and framework versions;
- package, model or application that currently blocks deployment;
- whether you need a build artifact, deployment help, board bring-up, model port, qualification or all of these;
- required timeframe.

Do not post proprietary source code, credentials, customer data or other confidential material in a public issue. A private follow-up channel can be arranged after initial scoping.

## Licensing

Commercial advisory is separate from the licences of upstream software. Engagement with SynRex does not replace or override third-party licence terms attached to Open3D, OpenCV, PyTorch, PyG, NVIDIA software or other dependencies.
