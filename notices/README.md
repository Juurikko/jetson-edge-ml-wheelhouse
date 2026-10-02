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
| cumm | Apache-2.0 | public `2agxrelease1` rebuild corrects stale package metadata; exact wheel physically qualified; release candidate |
| Open3D | MIT plus third-party notices | public thin-repack closes CuTeDSL build-notice provenance, externalizes target runtimes, preserves computational ELF bytes; release candidate |

## External runtimes

The initial wheelhouse does not automatically rehost PyTorch, SciPy, CUDA/cuDNN/NPP, NVIDIA cuSPARSELt, FFmpeg or GStreamer runtime binaries.

## OpenCV

The audited OpenCV wheel contains the `cv2` ELF payload and an extensive embedded licence tree. FFmpeg, GStreamer, CUDA/cuDNN/NPP and image-codec runtime libraries were observed as external dynamic dependencies rather than copied release assets.

## Open3D

The public Open3D R1 wheel externalizes libgfortran/libtbb to the frozen target OS, removes an unreferenced bundled libgomp, and removes the stale build-tree CuTeDSL EULA notice only after a provenance gate showed no CuTeDSL payload outside the generated licence tree. The accepted libOpen3D and pybind computational ELF bytes are preserved byte-for-byte and the resulting wheel passed full physical AGX requalification.
