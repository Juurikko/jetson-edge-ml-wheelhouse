# Supported targets

## Qualified

### Jetson AGX Orin — JetPack 7.2.1 / Jetson Linux R39.2.1 / CUDA 13.2 / Python 3.12 / SM87

Target ID:

`agx-orin-r39.2.1-cu13.2-py312-sm87`

This is the only target qualified for the first release channel. NVIDIA maps JetPack 7.2.1 to Jetson Linux 39.2.1; this repository uses the exact R39.2.1 target contract rather than treating nearby JetPack/Jetson Linux combinations as equivalent.

## Planned / not yet qualified

- Jetson Orin NX
- Jetson Orin Nano
- Jetson Thor / SM110

A wheel may import on a nearby target without that target being qualified. Compatibility claims are only made where physical evidence exists.
