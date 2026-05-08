"""Task 14 README and sample contract checks."""

from __future__ import annotations

import json
from pathlib import Path


README_PATH = Path("README.md")
SAMPLE_PATH = Path("samples/edr-sample-001.json")
EXPECTED_OUTPUT_FILES = (
    "edr-handoff.json",
    "replay-report.json",
    "customer-report.md",
    "investigation-tape.json",
    "evidence-ledger.json",
    "timeline.json",
    "findings.json",
    "verdict.json",
    "audit-chain-entry.json",
)


def _readme() -> str:
    return README_PATH.read_text(encoding="utf-8")


def test_root_readme_documents_task14_required_workflow():
    content = _readme()

    assert (
        "Zovark is the audit-grade evidence layer for AI-assisted SOC response."
        in content
    )
    assert "Python 3.11+" in content
    assert "No runtime dependencies beyond the Python standard library" in content
    assert (
        "python -m zovark.slice001 --input samples/edr-sample-001.json "
        "--output out/ --tenant-id tenant-001"
    ) in content
    assert "pytest tests/" in content


def test_root_readme_lists_exact_nine_output_files_with_hero_artifacts_first():
    content = _readme()

    assert "exactly 9 proof-package files" in content
    assert "8 JSON files and 1 Markdown" in content
    for filename in EXPECTED_OUTPUT_FILES:
        assert filename in content

    assert content.index("edr-handoff.json") < content.index(
        "investigation-tape.json"
    )
    assert content.index("replay-report.json") < content.index(
        "investigation-tape.json"
    )
    assert content.index("customer-report.md") < content.index(
        "investigation-tape.json"
    )
    assert "phishing-powershell.json" not in content


def test_root_readme_keeps_claims_bounded():
    content = _readme().lower()
    normalized = " ".join(content.split())

    assert "no live edr" in normalized
    assert "no llm calls" in normalized
    assert "no network calls" in normalized
    for forbidden in (
        "legally admissible",
        "sec-ready",
        "soc 2 certified",
        "slsa-compliant",
        "forensically complete",
        "forensic completeness",
        "proves all relevant evidence",
    ):
        assert forbidden not in content


def test_sample_matches_design_section_1_1_shape():
    sample = json.loads(SAMPLE_PATH.read_text(encoding="utf-8"))

    assert sample["alert_id"] == "alert-20260501-001"
    assert sample["alert_type"] == "edr_alert"
    assert sample["host"] == "workstation-42.corp.example"
    assert sample["timestamp"] == "2026-05-01T10:00:00Z"
    assert sample["severity"] == "high"
    assert sample["description"] == "Suspicious PowerShell execution detected"

    assert isinstance(sample["process_events"], list)
    assert len(sample["process_events"]) == 1
    process_event = sample["process_events"][0]
    assert process_event == {
        "event_id": "pe-001",
        "event_type": "process_event",
        "process_name": "powershell.exe",
        "command_line": "powershell.exe -EncodedCommand <base64>",
        "pid": 4812,
        "parent_pid": 1024,
        "timestamp": "2026-05-01T10:00:01Z",
    }

    assert isinstance(sample["network_events"], list)
    assert len(sample["network_events"]) == 1
    network_event = sample["network_events"][0]
    assert network_event == {
        "event_id": "ne-001",
        "event_type": "network_event",
        "process_name": "powershell.exe",
        "pid": 4812,
        "destination_ip": "203.0.113.50",
        "destination_port": 443,
        "protocol": "HTTPS",
        "timestamp": "2026-05-01T10:00:02Z",
    }
