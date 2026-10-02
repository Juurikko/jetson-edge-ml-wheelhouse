# R1 licence and notice index

This index records the release-hygiene state established by the public-release audit. It does not replace licence text carried by individual release artifacts.

| Artifact | Source licence | R1 notice state |
|---|---|---|
| torch-scatter | MIT | embedded MIT licence; release candidate |
| torch-sparse | MIT | MIT plus parallel-hashmap Apache-2.0 notice material; release candidate |
| torch-cluster | MIT | MIT plus nanoflann/KDTree BSD notice material; release candidate |
| spconv | Apache-2.0 | embedded Apache-2.0 licence; release candidate |
| PointROPE | MIT via LitePT | public `.2` rebuild embeds upstream MIT licence/build notice; release candidate |
| OpenCV + contrib | Apache-2.0 plus third-party components | exact wheel carries its third-party notice tree; external multimedia/CUDA runtimes documented separately |
| cumm | Apache-2.0 | public rebuild corrects stale package metadata before release |
| Open3D | MIT plus substantial third-party closure | release-friendly replacement and notice closure pending |

## External runtimes

The initial wheelhouse does not automatically rehost PyTorch, SciPy, CUDA/cuDNN/NPP, NVIDIA cuSPARSELt, FFmpeg or GStreamer runtime binaries.

## OpenCV

The audited OpenCV wheel contains the `cv2` ELF payload and an extensive embedded licence tree. FFmpeg, GStreamer, CUDA/cuDNN/NPP and image-codec runtime libraries were observed as external dynamic dependencies rather than copied release assets.

## Open3D

The accepted internal Open3D wheel is not yet a public-release asset. The release audit found bundled GCC/TBB runtime libraries and a large third-party notice inventory, so replacement bytes require a cleaner dependency-closure review and full device requalification.
