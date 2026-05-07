"""Tests for Slice 001 audit close entry construction."""

from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path

import pytest

from zovark.slice001 import ZovarkValidationError
from zovark.slice001.audit import (
    GENESIS_HASH,
    attach_audit_entry,
    build_audit_entry,
    build_close_entry,
    compute_this_entry_hash,
    derive_audit_entry,
    set_audit_entry,
)
from zovark.slice001.findings import attach_findings, derive_findings
from zovark.slice001.handoff import attach_handoff, derive_handoff
from zovark.slice001.hashing import sha256_of_obj, sha256_of_string
from zovark.slice001.ingest import load_sample, normalize_evidence
from zovark.slice001.tape import create_tape
from zovark.slice001.timeline import attach_timeline, build_initial_timeline
from zovark.slice001.verdict import attach_verdict, derive_verdict


SAMPLE_PATH = Path("samples/edr-sample-001.json")
DEMO_SAMPLE_PATH = Path("demo/zovark-proof-package/samples/edr/phishing-powershell.json")
DEMO_TAPE_PATH = Path("demo/zovark-proof-package/out/tape-001/investigation-tape.json")
DEMO_TIMELINE_PATH = Path("demo/zovark-proof-package/out/tape-001/timeline.json")
DEMO_AUDIT_PATH = Path("demo/zovark-proof-package/out/tape-001/audit-chain-entry.json")
AUDIT_FIELDS = {
    "created_at",
    "entry_id",
    "event_type",
    "payload",
    "prev_entry_hash",
    "sequence",
    "signed_root",
    "tenant_id",
    "this_entry_hash",
}
PAYLOAD_FIELDS = {"fields_hash", "tape_id", "verdict_value"}


def _sample_tape_with_handoff() -> dict:
    raw = load_sample(SAMPLE_PATH)
    evidence = normalize_evidence(raw)
    tape = create_tape(raw, evidence)
    timeline = build_initial_timeline(tape)
    tape = attach_timeline(tape, timeline)
    findings, no_findings_flag = derive_findings(tape)
    tape = attach_findings(tape, findings, no_findings_flag)
    verdict = derive_verdict(tape)
    tape = attach_verdict(tape, verdict)
    handoff = derive_handoff(tape)
    return attach_handoff(tape, handoff)


def _demo_pipeline_tape() -> dict:
    raw = load_sample(DEMO_SAMPLE_PATH)
    evidence = normalize_evidence(raw)
    committed_tape = json.loads(DEMO_TAPE_PATH.read_text(encoding="utf-8"))
    committed_timeline = json.loads(DEMO_TIMELINE_PATH.read_text(encoding="utf-8"))
    tape = create_tape(raw, evidence, tenant_id=committed_tape["tenant_id"])
    tape["tape_id"] = committed_tape["tape_id"]
    tape["audit_ref"] = "audit-entry-1"
    tape["timeline"] = committed_timeline
    findings, no_findings_flag = derive_findings(tape)
    tape = attach_findings(tape, findings, no_findings_flag)
    verdict = derive_verdict(tape)
    tape = attach_verdict(tape, verdict)
    handoff = derive_handoff(tape)
    return attach_handoff(tape, handoff)


def _fields_hash_snapshot(tape: dict) -> dict:
    return {
        "findings": tape["findings"],
        "raw_evidence": tape["raw_evidence"],
        "schema_version": tape["schema_version"],
        "source_alert_ref": tape["source_alert_ref"],
        "tape_id": tape["tape_id"],
        "tenant_id": tape["tenant_id"],
        "verdict_value": tape["verdict"]["value"],
    }


def _with_forged_verdict(tape: dict, value: str) -> dict:
    forged = deepcopy(tape)
    forged["verdict"] = deepcopy(tape["verdict"])
    forged["verdict"]["value"] = value
    snapshot = _fields_hash_snapshot(forged)
    forged["verdict"]["signing_tag"] = "sig-" + sha256_of_obj(snapshot)
    return forged


def _self_consistent_wrong_audit_entry(tape: dict) -> dict:
    entry = derive_audit_entry(tape)
    entry["payload"]["verdict_value"] = "benign"
    entry["this_entry_hash"] = compute_this_entry_hash(entry)
    return entry


def test_demo_pipeline_audit_entry_matches_committed_contract():
    committed_audit = json.loads(DEMO_AUDIT_PATH.read_text(encoding="utf-8"))

    audit_entry = derive_audit_entry(_demo_pipeline_tape())

    assert audit_entry == committed_audit


def test_audit_entry_is_deterministic_across_repeated_runs():
    tape = _sample_tape_with_handoff()

    first = derive_audit_entry(tape)
    second = derive_audit_entry(tape)

    assert first == second
    assert first["this_entry_hash"] == second["this_entry_hash"]


def test_audit_schema_is_exact():
    audit_entry = derive_audit_entry(_sample_tape_with_handoff())

    assert set(audit_entry) == AUDIT_FIELDS
    assert set(audit_entry["payload"]) == PAYLOAD_FIELDS


def test_close_entry_core_fields_are_deterministic():
    tape = _sample_tape_with_handoff()

    audit_entry = build_close_entry(tape, sequence=1, prev_hash=GENESIS_HASH)

    assert audit_entry["entry_id"] == "audit-entry-1"
    assert audit_entry["event_type"] == "tape_recording_closed"
    assert audit_entry["sequence"] == 1
    assert audit_entry["prev_entry_hash"] == sha256_of_string("genesis")
    assert audit_entry["signed_root"] is None
    assert audit_entry["tenant_id"] == tape["tenant_id"]
    assert audit_entry["payload"] == {
        "fields_hash": sha256_of_obj(_fields_hash_snapshot(tape)),
        "tape_id": tape["tape_id"],
        "verdict_value": tape["verdict"]["value"],
    }


def test_first_audit_entry_must_anchor_to_genesis():
    tape = _sample_tape_with_handoff()

    with pytest.raises(ZovarkValidationError):
        build_close_entry(
            tape,
            sequence=1,
            prev_hash=sha256_of_string("not-genesis"),
        )


def test_build_audit_entry_alias_matches_derive_audit_entry():
    tape = _sample_tape_with_handoff()

    assert build_audit_entry(tape) == derive_audit_entry(tape)


def test_this_entry_hash_is_recomputable_with_blank_hash_field():
    audit_entry = derive_audit_entry(_sample_tape_with_handoff())
    entry_for_hash = deepcopy(audit_entry)
    entry_for_hash["this_entry_hash"] = ""

    assert audit_entry["this_entry_hash"] == sha256_of_obj(entry_for_hash)
    assert audit_entry["this_entry_hash"] == compute_this_entry_hash(audit_entry)


@pytest.mark.parametrize("missing_key", ["raw_evidence", "timeline", "findings", "verdict", "handoff"])
def test_missing_required_tape_fields_are_rejected(missing_key):
    tape = _sample_tape_with_handoff()
    tape.pop(missing_key)

    with pytest.raises(ZovarkValidationError):
        derive_audit_entry(tape)


def test_malformed_raw_evidence_entries_are_rejected():
    tape = _sample_tape_with_handoff()
    tape["raw_evidence"][0].pop("raw_content")

    with pytest.raises(ZovarkValidationError):
        derive_audit_entry(tape)


def test_timeline_refs_absent_from_raw_evidence_are_rejected():
    tape = _sample_tape_with_handoff()
    tape["timeline"][0]["evidence_refs"] = ["ev-not-present"]

    with pytest.raises(ZovarkValidationError):
        derive_audit_entry(tape)


def test_finding_refs_absent_from_raw_evidence_are_rejected():
    tape = _sample_tape_with_handoff()
    tape["findings"][0]["evidence_refs"] = ["ev-not-present"]

    with pytest.raises(ZovarkValidationError):
        derive_audit_entry(tape)


def test_forged_verdict_is_rejected_before_audit_entry():
    tape = _sample_tape_with_handoff()
    forged = _with_forged_verdict(tape, "benign")

    with pytest.raises(ZovarkValidationError):
        derive_audit_entry(forged)


def test_forged_handoff_is_rejected_before_audit_entry():
    tape = _sample_tape_with_handoff()
    tape["handoff"]["execution_result"]["status"] = "succeeded"

    with pytest.raises(ZovarkValidationError):
        derive_audit_entry(tape)


def test_attach_rejects_self_consistent_but_non_derived_audit_entry():
    tape = _sample_tape_with_handoff()
    forged_entry = _self_consistent_wrong_audit_entry(tape)

    with pytest.raises(ZovarkValidationError):
        attach_audit_entry(tape, forged_entry)


def test_attach_rejects_malformed_audit_entry_shape():
    tape = _sample_tape_with_handoff()
    audit_entry = derive_audit_entry(tape)
    audit_entry["unexpected"] = "extra"

    with pytest.raises(ZovarkValidationError):
        attach_audit_entry(tape, audit_entry)


def test_attach_audit_entry_returns_copied_sealed_tape():
    tape = _sample_tape_with_handoff()
    original = deepcopy(tape)
    audit_entry = derive_audit_entry(tape)

    updated = attach_audit_entry(tape, audit_entry)

    assert updated is not tape
    assert tape == original
    assert updated["audit_entry"] == audit_entry
    assert updated["audit_ref"] == audit_entry["entry_id"]
    assert updated["state"] == "closed"
    assert updated["raw_evidence"] == original["raw_evidence"]
    assert updated["timeline"] == original["timeline"]
    assert updated["findings"] == original["findings"]
    assert updated["verdict"] == original["verdict"]
    assert updated["handoff"] == original["handoff"]


def test_set_audit_entry_alias_matches_attach_audit_entry():
    tape = _sample_tape_with_handoff()
    audit_entry = derive_audit_entry(tape)

    assert set_audit_entry(tape, audit_entry) == attach_audit_entry(tape, audit_entry)


def test_mutating_caller_audit_entry_after_attach_does_not_mutate_tape_audit():
    tape = _sample_tape_with_handoff()
    audit_entry = derive_audit_entry(tape)

    updated = attach_audit_entry(tape, audit_entry)
    audit_entry["payload"]["verdict_value"] = "benign"
    audit_entry["this_entry_hash"] = "0" * 64

    assert updated["audit_entry"] == derive_audit_entry(tape)


def test_mutating_original_tape_after_derivation_does_not_change_audit_entry():
    tape = _sample_tape_with_handoff()

    audit_entry = derive_audit_entry(tape)
    tape["raw_evidence"][0]["raw_content"]["host"] = "CHANGED"
    tape["findings"][0]["title"] = "changed"
    tape["verdict"]["value"] = "benign"
    tape["handoff"]["action_type"] = "notify_only"

    assert audit_entry == derive_audit_entry(_sample_tape_with_handoff())


def test_non_genesis_prev_hash_can_be_supplied_deterministically():
    tape = _sample_tape_with_handoff()
    prev_hash = sha256_of_string("previous-entry")

    audit_entry = build_close_entry(tape, sequence=2, prev_hash=prev_hash)

    assert audit_entry["entry_id"] == "audit-entry-2"
    assert audit_entry["sequence"] == 2
    assert audit_entry["prev_entry_hash"] == prev_hash
    assert audit_entry["this_entry_hash"] == compute_this_entry_hash(audit_entry)


def test_no_forbidden_imports_or_scope_creep_in_audit_module():
    source = Path("zovark/slice001/audit.py").read_text(encoding="utf-8")

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
        "random",
        "replay.py",
        "writer.py",
        "cli.py",
        "__main__",
    ]
    for token in forbidden:
        assert token not in source
