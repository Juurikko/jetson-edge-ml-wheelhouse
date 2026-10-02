# Native LitePT PointROPE — public release R1

## Result

**PASS — public-release candidate**

```text
synrex_pointrope_cu132_sm87-0.0.0+pt214cu132sm87.2-cp312-cp312-linux_aarch64.whl
SHA-256 273fe321b79e51dd19b2c96f12080d4f945de58c13be51082428f61c64ceab1b
```

Upstream LitePT commit:

```text
436d04801c8151faebe66a1b2d368a9711e7e6aa
```

## Why this rebuild exists

The previously qualified internal `.1` wheel lacked a complete public-release licence/build-notice package. The `.2` wheel adds release metadata/notices while preserving the accepted SM87 build adaptation.

The upstream computational sources `pointrope.cpp` and `kernels.cu` were required to remain byte-identical to the frozen upstream commit.

## Qualification gates

- static wheel/licence audit: PASS
- AArch64 native-extension audit: PASS
- SM87 cubin gate: PASS
- physical CUDA FP32/FP16 smoke on AGX Orin: PASS
- full C08 LitePT A3 requalification: PASS
- exact raw-ID parity against accepted A3 output: PASS

C08 contains 468,416 points. The public-release rebuild produced **0 changed raw predictions** against the accepted A3 baseline.

## Evidence hashes

```text
wheel
273fe321b79e51dd19b2c96f12080d4f945de58c13be51082428f61c64ceab1b

SM87/release setup patch
6226f935604ddbbfa22fc273ebb56b27d7d93419a42bba8b4151de596222176f

source + patch hash record
34cddced7d54d81310c6e51e59cc6943fc6bcd51f5e02df8b192b7583601f96f

static wheel audit
d08837b1f607307b1b8b2ef043bc198d7a122b7fdb9d45b79a98f155b29cde0d

physical CUDA smoke
7aaeff40232c976f6ce1b5ab8a629c53912c41ac5f44b8d692e7f5da409a7760

C08 A3 exact-parity record
bf7ca138c37a745a7bff51f758108c6e20b7af47ec19de6062469263a5b5f60d

release-candidate record
d20de81d4e7dd56a8b236920dbeadb75c35b37ade1b70838f8d02ed25a02e4c2

evidence bundle
c85672f256eb08e668fcd459d6c68c38a5524bc2120d3c4dc9f7db096581d89f
```

## Claim boundary

This qualification establishes the exact public wheel on the frozen AGX Orin target and its LitePT C08 application path. It does not assert correctness for every tensor shape, GPU architecture, Jetson model, or model family.
