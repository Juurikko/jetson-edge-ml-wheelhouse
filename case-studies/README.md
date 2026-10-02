# Case studies

Case studies connect the wheel artifacts to real application behavior on the qualified AGX Orin target.

## Planned

### LitePT-L runtime optimization

Controlled A/B work on a real aerial-LiDAR scene:

- portable PointROPE baseline: 52.243 s;
- native SM87 CUDA PointROPE: 48.073 s;
- raw-ID changes: 0 / 468,416;
- native PointROPE + native torch-scatter: 47.509 s;
- raw-ID changes: 0.

The application audit also showed that PyTorch 2.14/CUDA 13.2 already dispatched the actual LitePT attention shapes to fused FlashAttention.

### ECLAIR density operating envelope

Four selected ECLAIR scenes were evaluated at:

```text
native -> 20 -> 10 -> 5 -> 2 -> 0.5 pts/m²
```

The study includes semantic quality, runtime, monitored AGX rail energy and a retained-native composition control.

Scope must remain explicit:

> four-scene showcase subset — not the full ECLAIR benchmark.

The case-study pages will be populated after the first release manifests and publication assets are frozen.
