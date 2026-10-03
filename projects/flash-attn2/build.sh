#!/usr/bin/env bash
set -Eeuo pipefail
umask 022
PROJECT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
: "${FA_WORK:?FA_WORK is required}"
: "${FA_OUT:?FA_OUT is required}"
export CUDA_HOME="$FA_WORK/cuda-13.2"
export PATH="$CUDA_HOME/bin:$PATH"
export CC=gcc-13 CXX=g++-13 CUDAHOSTCXX=g++-13
export CUDACXX="$CUDA_HOME/bin/nvcc"
export MAX_JOBS=2 NVCC_THREADS=1
export FLASH_ATTN_CUDA_ARCHS=87 TORCH_CUDA_ARCH_LIST=8.7
export FLASH_ATTENTION_FORCE_BUILD=TRUE
export FLASH_ATTENTION_FORCE_CXX11_ABI=FALSE
export FLASH_ATTN_LOCAL_VERSION=cu132torch214.sm87.synrex0
export BUILD_TARGET=cuda
export PIP_NO_CACHE_DIR=1 PIP_DISABLE_PIP_VERSION_CHECK=1
export PYTHONHASHSEED=0
export TMPDIR="$FA_WORK/tmp"
mkdir -p "$TMPDIR" "$FA_OUT/wheel" "$FA_OUT/evidence"
/usr/bin/python3.12 -m venv "$FA_WORK/venv"
source "$FA_WORK/venv/bin/activate"
python -m pip install --no-cache-dir 'pip==25.3'
python -m pip install --no-cache-dir --only-binary=:all: \
  --report "$FA_OUT/evidence/build-tools-install-report.json" \
  'setuptools==80.9.0' 'wheel==0.45.1' 'packaging==25.0' \
  'ninja==1.13.0' 'psutil==7.0.0' 'einops==0.8.1' 'numpy==2.5.2'
python -m pip install --no-cache-dir --only-binary=:all: \
  --index-url https://download.pytorch.org/whl/cu132 \
  --report "$FA_OUT/evidence/torch-install-report.json" 'torch==2.14.0+cu132'
export LD_LIBRARY_PATH="$(python - <<'PY'
import pathlib, site
paths = []
for root in map(pathlib.Path, site.getsitepackages()):
    paths.append(root / 'torch/lib')
    paths.extend(root.glob('nvidia/*/lib'))
print(':'.join(str(p) for p in paths if p.is_dir()))
PY
):$CUDA_HOME/lib64:$CUDA_HOME/lib${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
python "$PROJECT/validate.py" preflight
python -m pip check | tee "$FA_OUT/evidence/pip-check.txt"
python -m pip freeze --all > "$FA_OUT/evidence/pip-freeze.txt"
python -m pip inspect > "$FA_OUT/evidence/pip-inspect.json"
dpkg-query -W -f='${binary:Package}\t${Version}\n' > "$FA_OUT/evidence/runner-packages.tsv"
df -h "$FA_WORK" | tee "$FA_OUT/evidence/disk-before-build.txt"
free -h | tee "$FA_OUT/evidence/memory-before-build.txt"
python - <<'PY'
import os, shutil
from pathlib import Path
mem = int(next(line.split()[1] for line in Path('/proc/meminfo').read_text().splitlines() if line.startswith('MemTotal:')))
if mem < 12 * 1024 * 1024:
    raise SystemExit('Expected public ARM64 runner memory allocation (at least 12 GiB)')
if shutil.disk_usage(os.environ['FA_WORK']).free < 12 * 1024**3:
    raise SystemExit('Less than 12 GiB free before FlashAttention compilation')
PY
cat > "$FA_WORK/sm87-probe.cu" <<'CUDA'
#include <cuda_runtime.h>
#include <cuda_fp16.h>
#include <cuda_bf16.h>
__global__ void sm87_types(__half *h, __nv_bfloat16 *b) {
    h[0] = __float2half(1.0f);
    b[0] = __float2bfloat16(1.0f);
}
CUDA
nvcc -std=c++20 -ccbin g++-13 --threads 1 \
  -gencode arch=compute_87,code=sm_87 -c "$FA_WORK/sm87-probe.cu" -o "$FA_WORK/sm87-probe.o" \
  2>&1 | tee "$FA_OUT/evidence/sm87-compiler-probe.log"
cuobjdump --list-elf "$FA_WORK/sm87-probe.o" | tee "$FA_OUT/evidence/sm87-compiler-probe-device-code.txt"
# Local setuptools build only: no build isolation, dependency rebuilding or prebuilt FA fallback.
cd "$FA_WORK/flash-attention"
python setup.py bdist_wheel --dist-dir "$FA_OUT/wheel" 2>&1 | tee "$FA_OUT/evidence/build.log"
cd "$PROJECT"
python "$PROJECT/validate.py" audit
