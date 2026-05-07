"""Tests for Slice 001 proof-package writer/materialization."""

from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path

import pytest

from zovark.slice001 import ZovarkValidationError
from zovark.slice001.audit import attach_audit_entry, compute_this_entry_hash, derive_audit_entry
from zovark.slice001.findings import attach_findings, derive_findings
from zovark.slice001.handoff import attach_handoff, derive_handoff
from zovark.slice001.hashing import sha256_of_obj, sha256_of_string
from zovark.slice001.ingest import load_sample, normalize_evidence
from zovark.slice001.replay import attach_replay_report, derive_replay_report
from zovark.slice001.tape import create_tape
from zovark.slice001.verdict import attach_verdict, derive_verdict
from zovark.slice001.writer import (
    EXPECTED_OUTPUT_FILES,
    JSON_OUTPUT_FILES,
    build_proof_package,
    render_customer_report,
    validate_proof_package,
    write_artifacts,
    write_proof_package,
)


DEMO_ROOT = Path("demo/zovark-proof-package")
DEMO_SAMPLE_PATH = DEMO_ROOT / "samples/edr/phishing-powershell.json"
DEMO_OUT_DIR = DEMO_ROOT / "out/tape-001"
DEMO_TAPE_PATH = DEMO_OUT_DIR / "investigation-tape.json"
DEMO_TIMELINE_PATH = DEMO_OUT_DIR / "timeline.json"


def _demo_complete_tape() -> dict:
    raw = load_sample(DEMO_SAMPLE_PATH)
    evidence = normalize_evidence(raw)
    committed_tape = json.loads(DEMO_TAPE_PATH.read_text(encoding="utf-8"))
    committed_timeline = json.loads(DEMO_TIMELINE_PATH.read_text(encoding="utf-8"))
    tape = create_tape(raw, evidence, tenant_id=committed_tape["tenant_id"])
    tape["tape_id"] = committed_tape["tape_id"]
    tape["audit_ref"] = committed_tape["audit_ref"]
    tape["timeline"] = committed_timeline
    findings, no_findings_flag = derive_findings(tape)
    tape = attach_findings(tape, findings, no_findings_flag)
    verdict = derive_verdict(tape)
    tape = attach_verdict(tape, verdict)
    handoff = derive_handoff(tape)
    tape = attach_handoff(tape, handoff)
    audit_entry = derive_audit_entry(tape)
    tape = attach_audit_entry(tape, audit_entry)
    replay_report = derive_replay_report(tape)
    return attach_replay_report(tape, replay_report)


def _read_output_texts(output_dir: Path) -> dict[str, str]:
    return {
        path.name: path.read_text(encoding="utf-8")
        for path in sorted(output_dir.iterdir())
        if path.is_file()
    }


def _with_forged_verdict(tape: dict, value: str) -> dict:
    forged = deepcopy(tape)
    forged["verdict"] = deepcopy(tape["verdict"])
    forged["verdict"]["value"] = value
    snapshot = {
        "findings": forged["findings"],
        "raw_evidence": forged["raw_evidence"],
        "schema_version": forged["schema_version"],
        "source_alert_ref": forged["source_alert_ref"],
        "tape_id": forged["tape_id"],
        "tenant_id": forged["tenant_id"],
        "verdict_value": value,
    }
    forged["verdict"]["signing_tag"] = "sig-" + sha256_of_obj(snapshot)
    return forged


def test_demo_pipeline_writer_matches_committed_proof_package(tmp_path):
    tape = _demo_complete_tape()

    write_proof_package(tape, tmp_path)

    assert sorted(path.name for path in tmp_path.iterdir()) == sorted(
        EXPECTED_OUTPUT_FILES
    )
    for filename in EXPECTED_OUTPUT_FILES:
        expected = (DEMO_OUT_DIR / filename).read_text(encoding="utf-8")
        actual = (tmp_path / filename).read_text(encoding="utf-8")
        assert actual == expected


def test_file_set_is_exact_and_input_sample_is_not_copied(tmp_path):
    tape = _demo_complete_tape()

    manifest = write_proof_package(tape, tmp_path)

    assert set(manifest) == set(EXPECTED_OUTPUT_FILES)
    assert sorted(path.name for path in tmp_path.iterdir()) == sorted(
        EXPECTED_OUTPUT_FILES
    )
    assert "phishing-powershell.json" not in {path.name for path in tmp_path.iterdir()}
    assert len(list(tmp_path.iterdir())) == 9
    assert len(JSON_OUTPUT_FILES) == 8


def test_all_json_outputs_parse_and_match_tape_fields(tmp_path):
    tape = _demo_complete_tape()

    write_proof_package(tape, tmp_path)

    loaded = {
        filename: json.loads((tmp_path / filename).read_text(encoding="utf-8"))
        for filename in JSON_OUTPUT_FILES
    }
    assert loaded["evidence-ledger.json"] == loaded["investigation-tape.json"][
        "raw_evidence"
    ]
    assert loaded["timeline.json"] == loaded["investigation-tape.json"]["timeline"]
    assert loaded["findings.json"] == loaded["investigation-tape.json"]["findings"]
    assert loaded["verdict.json"] == loaded["investigation-tape.json"]["verdict"]
    assert loaded["edr-handoff.json"] == tape["handoff"]
    assert loaded["audit-chain-entry.json"] == tape["audit_entry"]
    assert loaded["replay-report.json"] == tape["replay_report"]


def test_repeated_writes_are_byte_identical(tmp_path):
    tape = _demo_complete_tape()

    write_proof_package(tape, tmp_path)
    first = _read_output_texts(tmp_path)
    write_proof_package(tape, tmp_path)
    second = _read_output_texts(tmp_path)

    assert first == second


def test_build_proof_package_is_deterministic_and_copy_safe():
    tape = _demo_complete_tape()

    first = build_proof_package(tape)
    second = build_proof_package(tape)
    first["verdict.json"]["value"] = "changed"
    first["customer-report.md"] = "changed"

    assert second == build_proof_package(tape)
    assert tape["verdict"]["value"] == "confirmed_malicious"


def test_render_customer_report_matches_committed_contract():
    tape = _demo_complete_tape()
    expected_report = (DEMO_OUT_DIR / "customer-report.md").read_text(
        encoding="utf-8"
    )

    assert render_customer_report(tape) == expected_report


def test_customer_report_opens_with_recommended_action_before_internal_substrate():
    report = render_customer_report(_demo_complete_tape())

    recommended = report.index("## Recommended Action (EDR Action Card)")
    internal = report.index("## Internal Proof Substrate")

    assert recommended < internal
    assert "**Action:** ISOLATE_HOST" in report[:internal]
    assert "**Approval required:** YES" in report[:internal]
    assert "**Evidence basis:** 5 evidence items" in report[:internal]
    assert "**Verdict:** CONFIRMED_MALICIOUS" in report[:internal]
    assert "**Reversibility:** automatic" in report[:internal]
    assert "**Yes. Replay result: succeeded.**" in report[:internal]


def test_outputs_do_not_include_local_paths_or_machine_metadata(tmp_path):
    tape = _demo_complete_tape()

    write_proof_package(tape, tmp_path)
    combined = "\n".join(_read_output_texts(tmp_path).values())

    forbidden = [
        str(tmp_path),
        "/home/",
        "Codex-zov",
        "Zovark-Kiro",
        ".vscode",
        "zovark-yc-demo.zip",
    ]
    for token in forbidden:
        assert token not in combined


@pytest.mark.parametrize(
    "missing_key",
    [
        "raw_evidence",
        "timeline",
        "findings",
        "verdict",
        "handoff",
        "audit_entry",
        "replay_report",
    ],
)
def test_missing_required_tape_fields_are_rejected(missing_key):
    tape = _demo_complete_tape()
    tape.pop(missing_key)

    with pytest.raises(ZovarkValidationError):
        build_proof_package(tape)


def test_malformed_raw_evidence_entries_are_rejected():
    tape = _demo_complete_tape()
    tape["raw_evidence"][0].pop("raw_content")

    with pytest.raises(ZovarkValidationError):
        build_proof_package(tape)


def test_timeline_refs_absent_from_raw_evidence_are_rejected():
    tape = _demo_complete_tape()
    tape["timeline"][0]["evidence_refs"] = ["ev-not-present"]

    with pytest.raises(ZovarkValidationError):
        build_proof_package(tape)


def test_finding_refs_absent_from_raw_evidence_are_rejected():
    tape = _demo_complete_tape()
    tape["findings"][0]["evidence_refs"] = ["ev-not-present"]

    with pytest.raises(ZovarkValidationError):
        build_proof_package(tape)


def test_forged_verdict_is_rejected():
    tape = _demo_complete_tape()
    forged = _with_forged_verdict(tape, "benign")

    with pytest.raises(ZovarkValidationError):
        build_proof_package(forged)


def test_forged_handoff_is_rejected():
    tape = _demo_complete_tape()
    tape["handoff"]["execution_result"]["status"] = "succeeded"

    with pytest.raises(ZovarkValidationError):
        build_proof_package(tape)


def test_forged_audit_entry_is_rejected():
    tape = _demo_complete_tape()
    tape["audit_entry"]["prev_entry_hash"] = sha256_of_string("not-genesis")
    tape["audit_entry"]["this_entry_hash"] = compute_this_entry_hash(
        tape["audit_entry"]
    )

    with pytest.raises(ZovarkValidationError):
        build_proof_package(tape)


def test_forged_replay_report_is_rejected():
    tape = _demo_complete_tape()
    tape["replay_report"]["replay_state"]["state"] = "failed"
    tape["replay_report"]["audit_chain_entry"]["payload"]["replay_state"] = "failed"
    tape["replay_report"]["audit_chain_entry"][
        "this_entry_hash"
    ] = compute_this_entry_hash(tape["replay_report"]["audit_chain_entry"])

    with pytest.raises(ZovarkValidationError):
        build_proof_package(tape)


def test_validation_failure_writes_no_partial_package(tmp_path):
    tape = _demo_complete_tape()
    tape["replay_report"]["replay_state"]["state"] = "failed"

    with pytest.raises(ZovarkValidationError):
        write_proof_package(tape, tmp_path)

    assert not tmp_path.exists() or list(tmp_path.iterdir()) == []


def test_output_directory_with_unexpected_file_is_rejected(tmp_path):
    tape = _demo_complete_tape()
    (tmp_path / "unexpected.txt").write_text("do not mix", encoding="utf-8")

    with pytest.raises(ZovarkValidationError):
        write_proof_package(tape, tmp_path)

    assert (tmp_path / "unexpected.txt").read_text(encoding="utf-8") == "do not mix"


def test_writer_does_not_mutate_input_tape(tmp_path):
    tape = _demo_complete_tape()
    original = deepcopy(tape)

    write_proof_package(tape, tmp_path)

    assert tape == original


def test_write_artifacts_wrapper_accepts_explicit_artifacts(tmp_path):
    tape = _demo_complete_tape()
    base = deepcopy(tape)
    handoff = base.pop("handoff")
    audit_entry = base.pop("audit_entry")
    replay_report = base.pop("replay_report")

    manifest = write_artifacts(tmp_path, base, handoff, audit_entry, replay_report)

    assert set(manifest) == set(EXPECTED_OUTPUT_FILES)
    assert json.loads((tmp_path / "edr-handoff.json").read_text(encoding="utf-8")) == handoff
    assert (
        json.loads((tmp_path / "audit-chain-entry.json").read_text(encoding="utf-8"))
        == audit_entry
    )
    assert (
        json.loads((tmp_path / "replay-report.json").read_text(encoding="utf-8"))
        == replay_report
    )


def test_validate_proof_package_rejects_extra_or_missing_files():
    tape = _demo_complete_tape()
    package = build_proof_package(tape)
    package["extra.json"] = {}

    with pytest.raises(ZovarkValidationError):
        validate_proof_package(package, tape=tape)

    package.pop("extra.json")
    package.pop("verdict.json")
    with pytest.raises(ZovarkValidationError):
        validate_proof_package(package, tape=tape)


def test_no_forbidden_imports_or_scope_creep_in_writer_module():
    source = Path("zovark/slice001/writer.py").read_text(encoding="utf-8")

    forbidden = [
        "requests",
        "httpx",
        "socket",
        "subprocess",
        "openai",
        "ramalama",
        "temporalio",
        "redis",
        "psycopg2",
        "sqlalchemy",
        "boto3",
        "datetime.now",
        "datetime.utcnow",
        "time.time",
        "uuid.uuid4",
        "cli.py",
        "__main__",
        "sentry",
    ]
    for token in forbidden:
        assert token not in source
