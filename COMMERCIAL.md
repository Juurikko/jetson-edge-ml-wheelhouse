# Commercial advisory

**Engineering lead & contact:** Tuomas Pietilä, SynRex Oy · [tuomas.pietila@synrex.fi](mailto:tuomas.pietila@synrex.fi) · [LinkedIn](https://www.linkedin.com/in/tuomas-pietila/)

This repository is a public engineering reference for a narrowly qualified Jetson AGX Orin stack. It demonstrates how SynRex Oy approaches unsupported edge-ML software: exact source identity, controlled ARM64/CUDA builds, physical-device qualification, application-level testing and release evidence.

It is **not** intended to turn every adjacent Jetson configuration into a community-supported target.

## SynRex Custom Wheel Foundry

SynRex offers **request-driven custom wheel builds for Jetson AGX Orin and Jetson Orin Nano**.

The requested target is defined before work begins. A target contract can include:

- Jetson module / device and carrier environment;
- JetPack and Jetson Linux / L4T release;
- CUDA toolkit and GPU architecture;
- CPython version / ABI;
- PyTorch or other framework version;
- exact upstream package release or commit;
- required optional features and native dependencies;
- requested qualification level.

Depending on scope, the deliverable can include the resulting wheel(s), source and dependency locks, build recipe, SHA-256 manifest, installation instructions and physical-device qualification evidence.

This does **not** mean every combination is already supported. The public repository qualifies only the explicitly documented targets; a custom configuration becomes a qualified SynRex deliverable only after its own agreed evidence gates pass.

Typical requests include a missing wheel for a new JetPack/Python combination, rebuilding a CUDA extension against a particular PyTorch stack, or producing a private mutually compatible wheel set for an application.

[Open a Custom Wheel Foundry / commercial advisory request](https://github.com/Juurikko/jetson-edge-ml-wheelhouse/issues/new?template=commercial-advisory.yml).

## Custom Wheel Foundry software licensing

The **proprietary SynRex Custom Wheel Foundry software platform used to build and qualify the wheel artifacts demonstrated in this repository is available for commercial licensing**.

This is separate from commissioning SynRex to build a particular wheel. Licensing can be discussed for organizations that want the foundry capability in their own engineering workflow, infrastructure or product-development environment. Commercial terms, deployment model, permitted use, deliverables and maintenance scope are agreed for the specific engagement.

The SynRex licence applies only to SynRex proprietary technology. It does not grant rights to CUDA, PyTorch, Open3D, OpenCV, PyG or other third-party software beyond the licences provided by their respective owners.

Organizations interested in licensing or acquiring the technology can contact [Tuomas Pietilä](mailto:tuomas.pietila@synrex.fi) or open a non-confidential [commercial advisory request](https://github.com/Juurikko/jetson-edge-ml-wheelhouse/issues/new?template=commercial-advisory.yml).

## Where commercial advisory fits

Commercial advisory is appropriate when you need help turning a promising build into a usable deployment, for example:

- **deployment help** — packaging, runtime closure, offline installation, service/container integration and reproducible deployment;
- **custom board bring-up** — carrier-board or platform-specific validation, BSP/runtime integration and hardware-dependent troubleshooting;
- **model porting** — moving an existing model or pipeline onto a Jetson target and proving the relevant CUDA/application path;
- **Custom Wheel Foundry** — requested AGX Orin / Orin Nano wheels for a specified dependency and software stack;
- **foundry software licensing** — commercial licensing of SynRex's proprietary Custom Wheel Foundry platform;
- **missing wheel / dependency enablement** — ARM64/CUDA/Python ports for exact target combinations;
- **private wheelhouses** — customer-specific artifact sets, source locks, hashes and installation manifests;
- **qualification** — physical HIL tests, import-order/runtime collision checks, numerical or application parity and performance evidence;
- **release engineering** — reproducible build recipes, SBOM/licence closure and auditable release bundles.

LiDAR, robotics, computer vision and other sensor-heavy edge-ML applications are particularly suitable where model code, CUDA dependencies and real device behavior all need to work together.

## Engagement boundary

The public artifacts remain self-service and are provided within their stated qualification scope. A public issue does not create a support obligation, SLA or commitment to port an unsupported environment.

Commercial work is scoped separately around a defined target, deliverable and evidence level. Depending on the task, the deliverable may be a wheel, private wheelhouse, build recipe, deployment bundle, qualification report, application port or a bounded advisory engagement.

## Starting a conversation

Open a [commercial advisory request](https://github.com/Juurikko/jetson-edge-ml-wheelhouse/issues/new?template=commercial-advisory.yml) with only **non-confidential** information, or contact Tuomas Pietilä at [tuomas.pietila@synrex.fi](mailto:tuomas.pietila@synrex.fi) or on [LinkedIn](https://www.linkedin.com/in/tuomas-pietila/).

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
