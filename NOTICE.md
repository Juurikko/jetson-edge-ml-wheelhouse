# Notices and redistribution policy

This repository is a distribution and qualification index for multiple upstream projects.

There is no single blanket licence that replaces the licences of the individual upstream components.

For every published binary we intend to provide:

- exact upstream project and source commit;
- exact binary SHA-256;
- build-origin statement;
- qualification scope;
- required upstream licence and attribution notices;
- bundled third-party notices where applicable;
- external runtime dependencies where applicable.

## Vendor and base runtime policy

The initial release is expected to **pin and link**, rather than automatically rehost:

- PyTorch 2.14.0+cu132;
- SciPy 1.18.1;
- NVIDIA CUDA/cuDNN/NPP runtimes;
- NVIDIA cuSPARSELt;
- FFmpeg/GStreamer system runtime libraries used by OpenCV.

No NVIDIA vendor wheel is repacked merely to change its platform metadata.

## Disclaimer

These are unofficial community builds. NVIDIA, PyTorch, PyG, OpenCV, Open3D, LitePT and other upstream projects do not endorse these binaries.
