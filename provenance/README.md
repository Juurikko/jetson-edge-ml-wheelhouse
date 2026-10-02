# Provenance

The wheelhouse separates **source provenance**, **build provenance**, and **physical qualification**.

A GitHub Actions build proves neither Jetson GPU execution nor model correctness. Conversely, a native Jetson rebuild does not become a CI-built artifact retroactively.

## First-release provenance

| Artifact | Source identity | Build origin | Device qualification |
|---|---|---|---|
| torch-scatter | exact commit | native AGX Orin | Q2 + Q3; LitePT integration |
| torch-sparse | exact commit | native AGX Orin | Q2 + Q3 |
| torch-cluster | exact commit | native AGX Orin | Q2 + Q3 |
| spconv | exact commit | native AGX Orin | Q2 + Q4 LitePT path |
| PointROPE | exact LitePT commit/component | native AGX Orin | physical CUDA + C08 exact parity |
| OpenCV | exact OpenCV + contrib commits | GitHub CI | physical AGX CUDA/DNN qualification |
| cumm | exact commit | native AGX Orin | replacement release bytes pending |
| Open3D | exact commit | GitHub CI | replacement release bytes pending |

Machine-readable source identities are in [source-locks.json](source-locks.json).

## Future CI attestations

Where an artifact is genuinely produced by GitHub Actions, a future release may add GitHub artifact attestations. Those describe build provenance; they do not replace physical AGX qualification evidence.
