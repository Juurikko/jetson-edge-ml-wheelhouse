#!/usr/bin/env python3
"""Prepare exact source and native ARM64 compiler inputs; never access a device."""
from __future__ import annotations

import difflib
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tarfile
import tempfile
import time
import urllib.request

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def require(ok: bool, message: str) -> None:
    if not ok:
        raise RuntimeError(message)


def sha256(path: Path) -> str:
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + '\n')


def command(*args: str, cwd: Path | None = None) -> str:
    print('+ ' + ' '.join(map(str, args)), flush=True)
    return subprocess.check_output(args, cwd=cwd, text=True, stderr=subprocess.STDOUT).strip()


def download(url: str, path: Path, digest: str | None = None) -> None:
    require(url.startswith('https://'), 'Only HTTPS build inputs are allowed')
    for attempt in range(3):
        try:
            with urllib.request.urlopen(url, timeout=90) as response, path.open('wb') as target:
                shutil.copyfileobj(response, target)
            if digest is not None:
                require(sha256(path) == digest, 'Input SHA256 mismatch: ' + url)
            return
        except Exception:
            if attempt == 2:
                raise
            time.sleep(3 * (attempt + 1))


def patch_setup(pristine: str) -> str:
    """Three exact replacements. No kernel, feature, dispatch or ABI rewrites."""
    replacements = [
        ('    if "80" in cuda_archs():\n',
         '    if "87" in cuda_archs():\n'
         '        cc_flag.append("-gencode")\n'
         '        cc_flag.append("arch=compute_87,code=sm_87")\n'
         '    if "80" in cuda_archs():\n'),
        ('    nvcc_flags = [\n    "-O3",\n    "-std=c++17",\n',
         '    # Minimal Linux backport of upstream PR #2879 (corrected torch 2.14 gate).\n'
         '    cxx_standard = "c++20" if (TORCH_MAJOR, TORCH_MINOR) >= (2, 14) else "c++17"\n'
         '    nvcc_flags = [\n    "-O3",\n    f"-std={cxx_standard}",\n'),
        ('    compiler_c17_flag=["-O3", "-std=c++17"]\n',
         '    compiler_c17_flag=["-O3", f"-std={cxx_standard}"]\n'),
    ]
    result = pristine
    for old, new in replacements:
        require(result.count(old) == 1, 'Pristine patch context mismatch: ' + repr(old))
        result = result.replace(old, new, 1)
    return result


def git_checkout(repository: str, ref: str, commit: str, destination: Path) -> None:
    require(not destination.exists(), 'Refusing to reuse a source working directory')
    destination.mkdir(parents=True)
    command('git', 'init', str(destination))
    command('git', 'remote', 'add', 'origin', repository, cwd=destination)
    command('git', '-c', 'protocol.version=2', 'fetch', '--depth=1', 'origin', ref, cwd=destination)
    command('git', 'checkout', '--detach', 'FETCH_HEAD', cwd=destination)
    require(command('git', 'rev-parse', 'HEAD', cwd=destination) == commit, 'Upstream commit drift')


def install_cuda(work: Path, evidence: Path) -> None:
    lock = json.loads((HERE / 'cuda-inputs.lock.json').read_text())
    prefix = work / 'cuda-13.2'
    prefix.mkdir()
    index_file = evidence / 'cuda-redist-index.json'
    download(lock['base_url'] + 'redistrib_' + lock['release_label'] + '.json', index_file)
    index = json.loads(index_file.read_text())
    require(index['release_label'] == lock['release_label'], 'CUDA release drift')
    inputs = []
    for component, expected_sha in lock['archives'].items():
        item = index[component]
        require(item['version'] == lock['version'], 'CUDA component version drift: ' + component)
        archive = item[lock['platform']]
        require(archive['sha256'] == expected_sha, 'CUDA upstream hash drift: ' + component)
        relative = f"{component}/{lock['platform']}/{component}-{lock['platform']}-{lock['version']}-archive.tar.xz"
        require(archive['relative_path'] == relative, 'Unexpected CUDA archive path')
        url = lock['base_url'] + relative
        print('INPUT ' + component + ' ' + expected_sha, flush=True)
        with tempfile.TemporaryDirectory(dir=work) as temporary:
            temp = Path(temporary)
            payload = temp / 'payload.tar.xz'
            download(url, payload, expected_sha)
            unpack = temp / 'unpack'
            unpack.mkdir()
            with tarfile.open(payload) as tar:
                tar.extractall(unpack, filter='data')
            roots = list(unpack.iterdir())
            require(len(roots) == 1 and roots[0].is_dir(), 'Unexpected CUDA archive layout')
            src = roots[0]
            for license_file in src.glob('*LICENSE*'):
                if license_file.is_file():
                    dst = evidence / 'licenses' / 'build-inputs' / (component + '-' + license_file.name)
                    dst.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(license_file, dst)
            shutil.copytree(src, prefix, dirs_exist_ok=True, symlinks=True)
        inputs.append({'component': component, 'url': url, 'sha256': expected_sha, 'version': item['version']})
    if (prefix / 'lib').is_dir() and not (prefix / 'lib64').exists():
        (prefix / 'lib64').symlink_to('lib', target_is_directory=True)
    require((prefix / 'bin/nvcc').is_file(), 'Native nvcc missing')
    require('V13.2.86' in command(str(prefix / 'bin/nvcc'), '--version'), 'nvcc version drift')
    write_json(evidence / 'cuda-inputs.json', {'index_sha256': sha256(index_file), 'inputs': inputs})


def prepare_sources(work: Path, evidence: Path) -> None:
    lock = json.loads((HERE / 'source-lock.json').read_text())
    upstream = lock['upstream']
    repo = work / 'pristine'
    git_checkout(upstream['repository'], 'refs/tags/' + upstream['tag'], upstream['commit'], repo)
    # Fetching the annotated tag must preserve both tag object and peeled commit.
    require(command('git', 'rev-parse', 'FETCH_HEAD', cwd=repo) in
            (upstream['tag_object'], upstream['commit']), 'Unexpected fetched ref')
    tag_type = command('git', 'cat-file', '-t', upstream['tag_object'], cwd=repo)
    require(tag_type == 'tag', 'Pinned annotated tag object missing')
    require(command('git', 'rev-parse', upstream['tag_object'] + '^{}', cwd=repo) == upstream['commit'],
            'Tag does not peel to pinned commit')
    setup = repo / 'setup.py'
    require(command('git', 'hash-object', str(setup)) == upstream['setup_git_blob'], 'Pristine setup.py changed')
    cutlass = lock['cutlass']
    gitlink = command('git', 'ls-tree', 'HEAD', 'csrc/cutlass', cwd=repo)
    require(cutlass['commit'] in gitlink and gitlink.startswith('160000 '), 'CUTLASS gitlink drift')
    # Export first; upstream setup.py otherwise downloads ROCm CK even for a CUDA-only build.
    # Exporting is a packaging operation, not a source-code patch.
    exported = work / 'flash-attention'
    shutil.copytree(repo, exported, ignore=shutil.ignore_patterns('.git'))
    cutlass_dir = exported / 'csrc/cutlass'
    if cutlass_dir.exists():
        require(not list(cutlass_dir.iterdir()), 'Unexpected populated CUTLASS path')
        cutlass_dir.rmdir()
    git_checkout(cutlass['repository'], cutlass['commit'], cutlass['commit'], cutlass_dir)
    shutil.rmtree(cutlass_dir / '.git')
    pristine_text = setup.read_text()
    patched_text = patch_setup(pristine_text)
    (exported / 'setup.py').write_text(patched_text)
    patch = ''.join(difflib.unified_diff(pristine_text.splitlines(keepends=True),
                                      patched_text.splitlines(keepends=True),
                                      fromfile='a/setup.py', tofile='b/setup.py'))
    patch_file = evidence / 'upstream.patch'
    patch_file.write_text(patch)
    # Apply the emitted patch independently to the pristine checkout and compare bytes.
    command('git', 'apply', '--check', str(patch_file), cwd=repo)
    command('git', 'apply', str(patch_file), cwd=repo)
    require(setup.read_text() == patched_text, 'Recorded patch does not reproduce build source')
    require(command('git', 'diff', '--name-only', cwd=repo) == 'setup.py', 'Unapproved upstream delta')
    expected = lock['patch_policy'].get('expected_sha256')
    if expected:
        require(sha256(patch_file) == expected, 'Patch SHA256 drift')
    lock['patch_policy']['applied_patch_sha256'] = sha256(patch_file)
    lock['patch_policy']['patched_setup_sha256'] = sha256(exported / 'setup.py')
    lock['cuda']['components'] = list(json.loads((HERE / 'cuda-inputs.lock.json').read_text())['archives'])
    lock['factory_commit'] = command('git', 'rev-parse', 'HEAD', cwd=ROOT)
    lock['target_contract_sha256'] = sha256(ROOT / lock['target_contract'])
    write_json(evidence / 'source-lock.resolved.json', lock)
    print('APPLIED_PATCH_SHA256=' + sha256(patch_file), flush=True)
    for label, directory in [('flash-attention', exported), ('cutlass', cutlass_dir)]:
        licenses = [p for p in directory.iterdir() if p.is_file() and ('LICENSE' in p.name or 'NOTICE' in p.name)]
        require(bool(licenses), 'Missing upstream license: ' + label)
        for license_file in licenses:
            dest = evidence / 'licenses' / label / license_file.name
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(license_file, dest)
    inventory = [{'path': str(p.relative_to(exported)), 'sha256': sha256(p), 'bytes': p.stat().st_size}
                 for p in sorted(exported.rglob('*')) if p.is_file()]
    write_json(evidence / 'source-file-inventory.json', inventory)
    shutil.copy2(ROOT / lock['target_contract'], evidence / 'target-contract.json')
    shutil.copytree(HERE, evidence / 'factory', ignore=shutil.ignore_patterns('__pycache__'))


def main() -> None:
    work = Path(os.environ['FA_WORK']).resolve()
    evidence = Path(os.environ['FA_OUT']).resolve() / 'evidence'
    work.mkdir(parents=True, exist_ok=True)
    evidence.mkdir(parents=True, exist_ok=True)
    prepare_sources(work, evidence)
    install_cuda(work, evidence)


if __name__ == '__main__':
    main()
