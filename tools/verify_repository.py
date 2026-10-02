#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

TARGET = ROOT / "targets/agx-orin-r39.2.1-cu13.2-py312-sm87/target-contract.json"
CANDIDATES = ROOT / "manifests/release-r1-candidates.json"
SOURCE_LOCKS = ROOT / "provenance/source-locks.json"

REQUIRED = [
    ROOT / "README.md",
    ROOT / "SUPPORTED_TARGETS.md",
    ROOT / "NOTICE.md",
    ROOT / "COMMERCIAL.md",
    ROOT / "SUPPORT.md",
    ROOT / "wheels/README.md",
    ROOT / "manifests/README.md",
    CANDIDATES,
    SOURCE_LOCKS,
    ROOT / "provenance/README.md",
    ROOT / "notices/README.md",
    ROOT / "docs/installation.md",
    ROOT / "docs/verification.md",
    ROOT / "docs/reproducibility.md",
    ROOT / "docs/release-process.md",
    ROOT / "docs/release-assets.md",
    ROOT / "qualification/qualification-levels.md",
    ROOT / "qualification/pointrope-public-release-r1.md",
    ROOT / "qualification/cumm-public-release-r1.md",
    ROOT / "qualification/open3d-public-release-r1.md",
    ROOT / "qualification/r1-clean-install.md",
    ROOT / "manifests/release-r1-freeze-receipt.json",
    ROOT / ".github/ISSUE_TEMPLATE/commercial-advisory.yml",
    ROOT / ".github/ISSUE_TEMPLATE/qualified-target-bug.yml",
    ROOT / ".github/ISSUE_TEMPLATE/config.yml",
    TARGET,
]

SHA256 = re.compile(r"^[0-9a-f]{64}$")
GIT_SHA = re.compile(r"^[0-9a-f]{40}$")
SAFE_FILENAME = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._+\\-]*$")

BANNED_BINARY_SUFFIXES = (
    ".whl", ".so", ".zip", ".tar.gz", ".tgz", ".deb", ".rpm", ".ipk"
)

TEXT_SUFFIXES = {
    ".md", ".json", ".yml", ".yaml", ".py", ".txt", ".toml",
    ".ini", ".cfg", ".csv", ".tsv", ".sh",
}

PRIVATE_HOME = "/home/" + "tuomas"
PRIVATE_HOSTS = [
    "tp" + "samsung15",
    "rtx4090" + "-wsl",
    "i5" + "radeon",
    "hermes" + "lab",
    "ylane" + "-gw01",
]

SENSITIVE_PATTERNS = {
    "tailscale_or_cgnat_ip": re.compile(
        r"\b100\.(?:6[4-9]|[78]\d|9\d|1[01]\d|12[0-7])"
        r"\.(?:\d{1,3})\.(?:\d{1,3})\b"
    ),
    "rfc1918_10": re.compile(r"\b10\.(?:\d{1,3}\.){2}\d{1,3}\b"),
    "rfc1918_172": re.compile(
        r"\b172\.(?:1[6-9]|2\d|3[01])\.(?:\d{1,3})\.(?:\d{1,3})\b"
    ),
    "rfc1918_192_168": re.compile(
        r"\b192\.168\.(?:\d{1,3})\.(?:\d{1,3})\b"
    ),
    "windows_user_path": re.compile(r"(?i)\b[A-Z]:\\Users\\[^\\\s]+"),
    "github_pat": re.compile(r"\bgithub_pat_[A-Za-z0-9_]+\b"),
    "github_classic_pat": re.compile(r"\bgh[pousr]_[A-Za-z0-9]+\b"),
    "openai_key": re.compile(r"\bsk-[A-Za-z0-9_-]{16,}\b"),
    "private_key": re.compile(
        r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"
    ),
}


class VerifyError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise VerifyError(message)


def load_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise VerifyError(
            f"invalid JSON: {path.relative_to(ROOT)}: {exc}"
        ) from exc


def validate_sha256(value, label: str) -> None:
    require(
        isinstance(value, str) and bool(SHA256.fullmatch(value)),
        f"{label}: expected lowercase 64-hex SHA-256",
    )


def validate_git_sha(value, label: str) -> None:
    require(
        isinstance(value, str) and bool(GIT_SHA.fullmatch(value)),
        f"{label}: expected lowercase 40-hex Git SHA",
    )


def validate_filename(value, label: str) -> None:
    require(
        isinstance(value, str) and bool(SAFE_FILENAME.fullmatch(value)),
        f"{label}: expected a safe basename",
    )
    require("/" not in value and "\\" not in value, f"{label}: path not allowed")


def tracked_files() -> list[Path]:
    data = subprocess.check_output(
        ["git", "-C", str(ROOT), "ls-files", "-z"]
    )
    return [
        ROOT / raw.decode("utf-8")
        for raw in data.split(b"\0")
        if raw
    ]


def verify_required_files() -> None:
    missing = [
        p.relative_to(ROOT).as_posix()
        for p in REQUIRED
        if not p.is_file()
    ]
    require(not missing, "missing required files: " + ", ".join(missing))
    print(f"required_files={len(REQUIRED)} PASS")


def verify_public_positioning() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    first_line = readme.splitlines()[0]
    require("JetPack 7.2.1" in first_line, "README title must name JetPack 7.2.1")
    require("SynRex Oy" in readme, "README must identify SynRex Oy")
    require("commercial advisory" in readme.lower(), "commercial advisory path missing")
    require(
        "custom board bring-up" in readme.lower(),
        "custom board bring-up commercial scope missing",
    )
    require("model porting" in readme.lower(), "model porting commercial scope missing")
    require(
        "https://www.linkedin.com/in/tuomas-pietila/" in readme,
        "engineering lead LinkedIn contact missing from README",
    )
    print("public_positioning=PASS")


def verify_target() -> dict:
    target = load_json(TARGET)
    require(
        target.get("schema") == "synrex.jetson_wheelhouse_target_contract.v1",
        "target schema mismatch",
    )
    require(
        target.get("target_id") == "agx-orin-r39.2.1-cu13.2-py312-sm87",
        "target_id mismatch",
    )
    require(target.get("qualification_status") == "qualified", "target not qualified")

    hw = target.get("hardware", {})
    require(hw.get("architecture") == "aarch64", "architecture mismatch")
    require(hw.get("gpu") == "Orin", "GPU mismatch")
    require(hw.get("compute_capability") == [8, 7], "compute capability mismatch")
    require(hw.get("cuda_arch") == "sm_87", "CUDA arch mismatch")

    os_data = target.get("os", {})
    require(os_data.get("jetpack") == "7.2.1", "JetPack mismatch")
    require(os_data.get("l4t") == "R39.2.1", "L4T mismatch")
    require(os_data.get("kernel") == "6.8.12-1021-tegra", "kernel mismatch")
    require(os_data.get("glibc") == "2.39", "glibc mismatch")

    toolchain = target.get("toolchain", {})
    require(toolchain.get("python") == "3.12.3", "Python mismatch")
    require(toolchain.get("cuda") == "13.2.86", "CUDA toolkit mismatch")

    stack = target.get("python_stack", {})
    require(stack.get("torch") == "2.14.0+cu132", "torch mismatch")
    validate_git_sha(stack.get("torch_git"), "target torch_git")

    print("target_contract=PASS")
    return target


def verify_manifest(target: dict) -> dict:
    manifest = load_json(CANDIDATES)
    require(
        manifest.get("schema")
        == "synrex.jetson_edge_ml_wheelhouse.release_candidates.v1",
        "candidate manifest schema mismatch",
    )
    require(manifest.get("target_id") == target["target_id"], "manifest target mismatch")
    require(
        manifest.get("planned_release_tag")
        == "agx-orin-r39.2.1-cu13.2-py312-sm87-r1",
        "planned release tag mismatch",
    )
    require(manifest.get("release_created") is False, "bootstrap cannot claim release exists")
    require(
        manifest.get("binary_assets_published") is False,
        "bootstrap cannot claim binary assets are published",
    )

    artifacts = manifest.get("artifacts")
    require(isinstance(artifacts, list) and artifacts, "artifacts must be non-empty")

    expected_ids = {
        "torch-scatter", "torch-sparse", "torch-cluster", "spconv",
        "pointrope", "opencv", "cumm", "open3d",
    }
    ids = set()
    filenames = set()
    candidates = 0
    pending = 0

    for i, artifact in enumerate(artifacts):
        label = f"artifacts[{i}]"
        artifact_id = artifact.get("id")
        require(isinstance(artifact_id, str) and artifact_id, f"{label}.id missing")
        require(artifact_id not in ids, f"duplicate artifact id: {artifact_id}")
        ids.add(artifact_id)

        validate_git_sha(artifact.get("source_commit"), f"{label}.source_commit")
        extra = artifact.get("additional_source_commit")
        if extra is not None:
            validate_git_sha(extra, f"{label}.additional_source_commit")

        status = artifact.get("status")
        require(
            status in {"release_candidate", "release_pending_rebuild"},
            f"{label}.status invalid: {status!r}",
        )

        if status == "release_candidate":
            candidates += 1
            filename = artifact.get("filename")
            validate_filename(filename, f"{label}.filename")
            require(filename.endswith(".whl"), f"{label}.filename must be a wheel")
            require(filename not in filenames, f"duplicate filename: {filename}")
            filenames.add(filename)
            validate_sha256(artifact.get("sha256"), f"{label}.sha256")
        else:
            pending += 1
            filename = artifact.get("accepted_internal_filename")
            validate_filename(filename, f"{label}.accepted_internal_filename")
            require(filename.endswith(".whl"), f"{label}: pending artifact must name prior wheel")
            validate_sha256(
                artifact.get("accepted_internal_sha256"),
                f"{label}.accepted_internal_sha256",
            )

    require(ids == expected_ids, f"artifact set mismatch: {sorted(ids)}")
    require(candidates == 8, f"expected 8 release candidates, got {candidates}")
    require(pending == 0, f"expected 0 release-pending artifacts, got {pending}")
    print(f"release_candidates={candidates} release_pending={pending} PASS")
    return manifest


def verify_source_locks(manifest: dict) -> None:
    locks = load_json(SOURCE_LOCKS)
    require(
        locks.get("schema") == "synrex.jetson_edge_ml_wheelhouse.source_locks.v1",
        "source-lock schema mismatch",
    )
    require(locks.get("target_id") == manifest["target_id"], "source-lock target mismatch")

    sources = locks.get("sources")
    require(isinstance(sources, list) and sources, "source locks empty")
    by_id = {}
    for i, source in enumerate(sources):
        artifact_id = source.get("id")
        require(isinstance(artifact_id, str) and artifact_id, f"sources[{i}].id missing")
        require(artifact_id not in by_id, f"duplicate source lock: {artifact_id}")
        validate_git_sha(source.get("source_commit"), f"sources[{i}].source_commit")
        validate_git_sha(source.get("license_blob_sha"), f"sources[{i}].license_blob_sha")
        by_id[artifact_id] = source

    manifest_by_id = {x["id"]: x for x in manifest["artifacts"]}
    require(set(by_id) == set(manifest_by_id), "source-lock artifact set mismatch")

    for artifact_id, artifact in manifest_by_id.items():
        require(
            by_id[artifact_id]["source_commit"] == artifact["source_commit"],
            f"{artifact_id}: source lock != release manifest",
        )

    print(f"source_locks={len(by_id)} PASS")


def verify_no_binary_payloads(files: list[Path]) -> None:
    bad = []
    for path in files:
        rel = path.relative_to(ROOT).as_posix().lower()
        if any(rel.endswith(suffix) for suffix in BANNED_BINARY_SUFFIXES):
            bad.append(rel)
    require(not bad, "binary release payload tracked in Git: " + ", ".join(bad))
    print("tracked_binary_payloads=0 PASS")


def verify_redaction(files: list[Path]) -> None:
    findings = []
    private_host_re = re.compile(
        r"(?i)\b(?:" + "|".join(re.escape(x) for x in PRIVATE_HOSTS) + r")\b"
    )

    for path in files:
        if not path.is_file():
            continue
        if path.suffix.lower() not in TEXT_SUFFIXES and path.name not in {
            ".gitignore", ".gitattributes"
        }:
            continue
        try:
            content = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue

        rel = path.relative_to(ROOT).as_posix()

        if PRIVATE_HOME in content:
            findings.append((rel, "private_linux_home", PRIVATE_HOME))
        for match in private_host_re.finditer(content):
            findings.append((rel, "private_hostname", match.group(0)))
        for label, pattern in SENSITIVE_PATTERNS.items():
            for match in pattern.finditer(content):
                findings.append((rel, label, match.group(0)))

    if findings:
        rendered = "; ".join(
            f"{path}:{label}:{value}"
            for path, label, value in findings[:20]
        )
        raise VerifyError(f"public redaction scan failed: {rendered}")

    print("public_redaction_findings=0 PASS")


def verify_pointrope_receipt(manifest: dict) -> None:
    pointrope = next(x for x in manifest["artifacts"] if x["id"] == "pointrope")
    require(pointrope["status"] == "release_candidate", "PointROPE not release_candidate")
    content = (ROOT / "qualification/pointrope-public-release-r1.md").read_text(
        encoding="utf-8"
    )
    require(pointrope["filename"] in content, "PointROPE qualification missing filename")
    require(pointrope["sha256"] in content, "PointROPE qualification missing SHA-256")
    require("0 changed raw predictions" in content, "PointROPE exact-parity statement missing")
    print("pointrope_receipt=PASS")


def verify_cumm_receipt(manifest: dict) -> None:
    cumm = next(x for x in manifest["artifacts"] if x["id"] == "cumm")
    require(cumm["status"] == "release_candidate", "cumm not release_candidate")
    content = (ROOT / "qualification/cumm-public-release-r1.md").read_text(
        encoding="utf-8"
    )
    require(cumm["filename"] in content, "cumm qualification missing filename")
    require(cumm["sha256"] in content, "cumm qualification missing SHA-256")
    require(
        "CUMM_PHYSICAL_TENSORVIEW_SMOKE=PASS" in content,
        "cumm physical TensorView PASS marker missing",
    )
    require(
        "SPCONV_COMPATIBILITY_CUDA_SMOKE=PASS" in content,
        "cumm/spconv compatibility PASS marker missing",
    )
    print("cumm_receipt=PASS")


def verify_open3d_receipt(manifest: dict) -> None:
    open3d = next(x for x in manifest["artifacts"] if x["id"] == "open3d")
    require(open3d["status"] == "release_candidate", "Open3D not release_candidate")
    content = (ROOT / "qualification/open3d-public-release-r1.md").read_text(
        encoding="utf-8"
    )
    require(open3d["filename"] in content, "Open3D qualification missing filename")
    require(open3d["sha256"] in content, "Open3D qualification missing SHA-256")
    require(
        "OPEN3D_PUBLIC_RELEASE_PHYSICAL_GATE=PASS" in content,
        "Open3D physical PASS marker missing",
    )
    require(
        "computational ELF bytes" in content,
        "Open3D computational-ELF preservation statement missing",
    )
    print("open3d_receipt=PASS")


def verify_clean_install_receipt() -> None:
    content = (ROOT / "qualification/r1-clean-install.md").read_text(
        encoding="utf-8"
    )
    require(
        "EXACT_8_WHEEL_CLEAN_INSTALL=PASS" in content,
        "clean-install PASS marker missing",
    )
    require(
        "5477ecb13707194157a56b0d68ee4bb0af15b1c63ce226addd5decec101c3ec2"
        in content,
        "final release manifest hash missing from clean-install record",
    )
    require(
        "R1_FINAL_EVIDENCE_OFF_DEVICE=PASS" in content,
        "off-device release evidence PASS marker missing",
    )

    receipt = load_json(ROOT / "manifests/release-r1-freeze-receipt.json")
    require(
        receipt.get("schema")
        == "synrex.jetson_edge_ml_wheelhouse.release_freeze_receipt.v1",
        "release freeze receipt schema mismatch",
    )
    require(receipt.get("release_candidate_count") == 8, "freeze receipt candidate count mismatch")
    require(receipt.get("clean_install_status") == "PASS", "clean install not PASS")
    validate_sha256(
        receipt.get("clean_install_receipt_sha256"),
        "clean_install_receipt_sha256",
    )
    validate_sha256(
        receipt.get("agx_generated_final_release_manifest_sha256"),
        "agx_generated_final_release_manifest_sha256",
    )
    bundle = receipt.get("evidence_bundle", {})
    validate_sha256(bundle.get("sha256"), "clean-install evidence bundle sha256")
    require(bundle.get("bytes") == 11788, "clean-install evidence bundle size mismatch")
    require(receipt.get("release_created") is False, "freeze receipt cannot claim release exists")
    require(
        receipt.get("binary_assets_published") is False,
        "freeze receipt cannot claim binary assets are published",
    )
    print("clean_install_receipt=PASS")


def main() -> int:
    try:
        verify_required_files()
        verify_public_positioning()
        target = verify_target()
        manifest = verify_manifest(target)
        verify_source_locks(manifest)
        files = tracked_files()
        verify_no_binary_payloads(files)
        verify_redaction(files)
        verify_pointrope_receipt(manifest)
        verify_cumm_receipt(manifest)
        verify_open3d_receipt(manifest)
        verify_clean_install_receipt()
    except VerifyError as exc:
        print(f"REPOSITORY_INTEGRITY=FAIL: {exc}")
        return 1

    print("REPOSITORY_INTEGRITY=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
