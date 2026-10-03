#!/usr/bin/env python3
"""Explicit, offline device-phase official LitePT anchor. No installs or downloads."""
from __future__ import annotations

import copy
import json
from pathlib import Path
import random
import runpy
import subprocess
import sys
from unittest.mock import patch

from prepare import require, sha256

LITEPT_COMMIT = '436d04801c8151faebe66a1b2d368a9711e7e6aa'
CONFIG = 'configs/scannet/semseg-litept-small-v1m1.py'


def checked_input(spec: dict, key: str, base: Path) -> Path:
    entry = spec[key]
    path = (base / entry['file']).resolve()
    require(path.is_file(), 'Missing frozen anchor input: ' + key)
    require(sha256(path) == entry['sha256'], 'Anchor input digest mismatch: ' + key)
    return path


def run_anchor(repo: Path, specification: Path) -> dict:
    import numpy as np
    import torch
    import flash_attn
    import spconv.pytorch as spconv

    spec = json.loads(specification.read_text())
    require(spec.get('schema') == 'synrex.litept.flash_attn_anchor.v1', 'Unknown anchor specification')
    require(spec.get('litept_commit') == LITEPT_COMMIT, 'Unapproved LitePT source')
    require(spec.get('config') == CONFIG, 'Unapproved official inference configuration')
    require(spec.get('synthetic_input') is False, 'A synthetic input is not a real application anchor')
    require(bool(spec.get('dataset_description')) and bool(spec.get('checkpoint_origin')), 'Application input provenance missing')
    head = subprocess.check_output(['git', '-C', str(repo), 'rev-parse', 'HEAD'], text=True).strip()
    require(head == LITEPT_COMMIT, 'LitePT checkout drift')
    changed = subprocess.check_output(['git', '-C', str(repo), 'status', '--porcelain', '--untracked-files=all'], text=True)
    require(not changed.strip(), 'LitePT source tree is not pristine; keep inputs and evidence outside it')
    config = repo / CONFIG
    require(sha256(config) == spec['config_sha256'], 'Official config digest mismatch')
    checkpoint = checked_input(spec, 'checkpoint', specification.parent)
    sample = checked_input(spec, 'sample', specification.parent)
    sys.path.insert(0, str(repo))
    # No source rewrite, no fake pointops/PointROPE modules, no eager-attention fallback.
    from models import build_model
    from models.litept.litept import PointROPEAttention
    from libs.pointrope import PointROPE

    config_values = runpy.run_path(str(config))
    model = build_model(config_values['model']).cuda().eval()
    state = torch.load(checkpoint, map_location='cpu', weights_only=True)
    if isinstance(state, dict) and 'state_dict' in state:
        state = state['state_dict']
    require(isinstance(state, dict) and bool(state), 'Checkpoint has no state dictionary')
    if all(k.startswith('module.') for k in state):
        state = {k[len('module.'):]: v for k, v in state.items()}
    require(all(isinstance(v, torch.Tensor) for v in state.values()), 'Unexpected checkpoint objects')
    model.load_state_dict(state, strict=True)
    data = torch.load(sample, map_location='cpu', weights_only=True)
    require(isinstance(data, dict) and {'feat', 'grid_coord', 'offset'} <= data.keys(), 'Expected frozen post-transform official model input')
    require(all(isinstance(v, torch.Tensor) for v in data.values()), 'Sample must contain tensors only')
    require(data['feat'].ndim == 2 and data['feat'].shape[0] > 0, 'Empty or invalid input features')
    require(data['grid_coord'].shape == (data['feat'].shape[0], 3), 'Grid coordinate shape mismatch')
    # Avoid evaluating semantic losses; this anchor checks deployment fidelity, not dataset accuracy.
    data = {k: v for k, v in data.items() if k != 'segment'}
    counts = {'flash_attn_varlen_qkvpacked': 0, 'pointrope': 0, 'spconv': 0, 'attention_modules': 0}
    hooks = []

    def count(name):
        def hook(module, args, output):
            counts[name] += 1
        return hook

    for module in model.modules():
        if isinstance(module, PointROPE):
            hooks.append(module.register_forward_hook(count('pointrope')))
        if isinstance(module, spconv.SparseConvolution):
            hooks.append(module.register_forward_hook(count('spconv')))
        if isinstance(module, PointROPEAttention):
            hooks.append(module.register_forward_hook(count('attention_modules')))
    original = flash_attn.flash_attn_varlen_qkvpacked_func

    def counted(*args, **kwargs):
        counts['flash_attn_varlen_qkvpacked'] += 1
        return original(*args, **kwargs)

    def reference(qkv, cu_seqlens, max_seqlen, dropout_p=0.0, softmax_scale=None, causal=False, **kwargs):
        require(dropout_p == 0 and not causal and not kwargs, 'Unexpected official attention invocation')
        ends = cu_seqlens.cpu().tolist()
        chunks = []
        scale = softmax_scale if softmax_scale is not None else qkv.shape[-1] ** -0.5
        for left, right in zip(ends[:-1], ends[1:]):
            q, k, v = qkv[left:right].unbind(dim=1)
            q, k, v = (x.float().transpose(0, 1) for x in (q, k, v))
            output = ((q @ k.transpose(-1, -2) * scale).softmax(dim=-1) @ v).transpose(0, 1)
            chunks.append(output.to(qkv.dtype))
        return torch.cat(chunks, dim=0)

    def infer():
        random.seed(20261003)
        np.random.seed(20261003)
        torch.manual_seed(20261003)
        torch.cuda.manual_seed_all(20261003)
        torch.backends.cuda.matmul.allow_tf32 = False
        torch.backends.cudnn.allow_tf32 = False
        inputs = {k: v.clone().cuda() for k, v in data.items()}
        with torch.inference_mode():
            result = model(inputs)
        torch.cuda.synchronize()
        require(isinstance(result, dict) and 'seg_logits' in result, 'Official segmentor output missing')
        logits = result['seg_logits'].detach().float()
        require(logits.ndim == 2 and logits.shape[0] == data['feat'].shape[0], 'Unexpected logits shape')
        require(bool(torch.isfinite(logits).all()), 'Non-finite official model output')
        return logits

    try:
        with patch.object(flash_attn, 'flash_attn_varlen_qkvpacked_func', counted):
            actual = infer()
        observed = copy.deepcopy(counts)
        require(all(value > 0 for value in observed.values()), 'Official stack path was not exercised: ' + repr(observed))
        with patch.object(flash_attn, 'flash_attn_varlen_qkvpacked_func', reference):
            expected = infer()
        # Frozen gates; no automatic tolerance relaxation and no post-failure reranking.
        torch.testing.assert_close(actual, expected, rtol=0.02, atol=0.02)
        mismatches = int((actual.argmax(dim=-1) != expected.argmax(dim=-1)).sum().item())
        require(mismatches == 0, 'LitePT class-ID mismatch against math-attention anchor')
        return {
            'status': 'PASS', 'source_commit': head, 'config': CONFIG,
            'config_sha256': sha256(config), 'checkpoint_sha256': sha256(checkpoint),
            'sample_sha256': sha256(sample), 'specification_sha256': sha256(specification),
            'checkpoint_origin': spec['checkpoint_origin'], 'dataset_description': spec['dataset_description'],
            'executed_path_counts': observed, 'shape': list(actual.shape),
            'max_abs_logit_error': float((actual - expected).abs().max().item()),
            'rtol': 0.02, 'atol': 0.02, 'class_id_mismatches': mismatches,
            'reference': 'Same official model/weights/input; only packed attention replaced by FP32 math reference',
            'scope': 'Post-transform official LitePT inference deployment fidelity; not semantic accuracy or performance',
        }
    finally:
        for hook in hooks:
            hook.remove()
        torch.cuda.empty_cache()
