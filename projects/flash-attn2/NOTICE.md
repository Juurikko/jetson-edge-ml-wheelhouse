# FlashAttention-2 candidate notices

This project adds a separate build candidate. It does not modify the public R1 release, its hashes, its qualification records, or repository-level licensing.

FlashAttention-2 is sourced from Dao-AILab/flash-attention, tag v2.8.3.post1, commit a8aa52b1ab3e9ca574c8a33b3f35afc017ffa2e2. Its upstream BSD-3-Clause license is copied verbatim into each build evidence bundle and checked for inclusion in the wheel. Copyright and attribution remain with the upstream authors.

The CUDA implementation compiles against NVIDIA CUTLASS commit dc4817921edda44a549197ff3a9dcf5df0636e7b. The CUTLASS LICENSE and any root NOTICE are copied verbatim into the evidence bundle. This notice is not a substitute for the upstream license texts.

The only initial local upstream deltas are the explicit compute_87/code=sm_87 build selection and a minimal Linux C++20 backport for PyTorch 2.14 from upstream PR 2879. The emitted unified patch, SHA-256, patched setup.py digest, pristine Git identities, and exported source-file inventory are retained. CUDA kernel source and runtime dispatch remain pristine unless a later separately recorded compatibility correction is required.

NVIDIA CUDA tools and PyTorch are external build/runtime inputs under their own terms. The wheel audit rejects bundled CUDA, driver, libtorch, or other unexpected shared libraries. CUDA build-input license texts are preserved separately from the FlashAttention binary notices. No CUDA driver is installed by this workflow.

CI_BUILD_VALIDATED describes successful cloud compilation and static/CPU evidence only. Every cloud-produced wheel remains CANDIDATE_NOT_PHYSICALLY_QUALIFIED. GitHub runners do not provide an Orin GPU. No upstream or NVIDIA endorsement, physical qualification, performance claim, or release-publication approval is implied.

The later AGX harness performs no installation or firmware changes. It verifies the installed candidate bytes, preserves existing R1 artifacts, and requires a frozen official LitePT inference anchor before reporting PHYSICAL_AGX_QUALIFIED. Physical qualification is limited to the operations and inputs explicitly recorded in that report.
