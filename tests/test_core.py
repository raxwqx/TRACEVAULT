import json
import sqlite3

import pytest

import tracevault.core as core
import tracevault.db as db
from tracevault.core import (
    add_case,
    add_evidence,
    add_relationship,
    export_integrity_json,
    export_integrity_markdown,
    list_relationships,
    sha256_file,
    verify_all_evidence,
    verify_evidence,
)
from tracevault.db import get_conn


@pytest.fixture
def vault(tmp_path, monkeypatch):
    """Isolate the database and evidence root inside a temporary directory."""
    monkeypatch.setattr(db, "DB_PATH", tmp_path / "data" / "tracevault.db")
    monkeypatch.setattr(core, "APP_DIR", tmp_path)
    db.init_db()
    return tmp_path


def test_sha256_known_content(tmp_path):
    sample = tmp_path / "sample.txt"
    sample.write_bytes(b"abc")
    assert sha256_file(sample) == "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"


def test_sha256_changes_when_content_changes(tmp_path):
    sample = tmp_path / "sample.bin"
    sample.write_bytes(b"first")
    before = sha256_file(sample)
    sample.write_bytes(b"second")
    after = sha256_file(sample)
    assert before != after


def test_get_conn_closes_connection(vault):
    with get_conn() as con:
        assert con.execute("SELECT 1").fetchone()[0] == 1
    with pytest.raises(sqlite3.ProgrammingError):
        con.execute("SELECT 1")


def test_blank_values_are_rejected(vault):
    with pytest.raises(ValueError):
        add_case("   ")
    with pytest.raises(ValueError):
        add_evidence(999, "file.bin", "data/evidence/file.bin", "digest", 0)


def test_add_relationship_returns_stable_id(vault):
    case_id = add_case("Relation case")
    first = add_relationship(case_id, "Alpha", "Beta")
    second = add_relationship(case_id, "Alpha", "Beta")
    assert first == second
    assert len(list_relationships(case_id)) == 1


def test_integrity_sweep_reports_all_states(vault):
    case_id = add_case("Integrity case")
    evidence_dir = vault / "data" / "evidence"
    evidence_dir.mkdir(parents=True)

    good = evidence_dir / "good.bin"
    bad = evidence_dir / "bad.bin"
    gone = evidence_dir / "gone.bin"
    for path, payload in ((good, b"good"), (bad, b"bad"), (gone, b"gone")):
        path.write_bytes(payload)
        add_evidence(case_id, path.name, f"data/evidence/{path.name}", sha256_file(path), len(payload))

    bad.write_bytes(b"tampered")
    gone.unlink()

    report = verify_all_evidence()
    assert report["summary"] == {"total": 3, "verified": 1, "mismatched": 1, "missing": 1, "unreadable": 0}
    assert {item["filename"]: item["status"] for item in report["items"]} == {
        "good.bin": "verified",
        "bad.bin": "mismatched",
        "gone.bin": "missing",
    }

    scoped = verify_all_evidence(case_id)
    assert scoped["summary"] == report["summary"]


def test_integrity_rejects_files_outside_evidence_root(vault):
    case_id = add_case("Path case")
    outside = vault / "outside.txt"
    outside.write_bytes(b"not evidence")
    evidence_id = add_evidence(case_id, "outside.txt", str(outside), sha256_file(outside), len(b"not evidence"))

    result = verify_evidence(evidence_id)
    assert result["exists"] is False
    assert result["status"] == "missing"


def test_integrity_exports_include_summary_and_items(vault):
    case_id = add_case("Report case")
    evidence_dir = vault / "data" / "evidence"
    evidence_dir.mkdir(parents=True)
    sample = evidence_dir / "sample.txt"
    sample.write_bytes(b"abc")
    add_evidence(case_id, "sample.txt", "data/evidence/sample.txt", sha256_file(sample), 3)

    markdown = export_integrity_markdown(case_id)
    assert f"Vaka #{case_id}" in markdown
    assert "DOĞRULANDI" in markdown
    assert "sample.txt" in markdown

    payload = json.loads(export_integrity_json(case_id))
    assert payload["summary"] == {"total": 1, "verified": 1, "mismatched": 0, "missing": 0, "unreadable": 0}
    assert payload["items"][0]["filename"] == "sample.txt"


def test_integrity_sweep_marks_unreadable_files(vault, monkeypatch):
    case_id = add_case("Unreadable case")
    evidence_dir = vault / "data" / "evidence"
    evidence_dir.mkdir(parents=True)
    sample = evidence_dir / "locked.bin"
    sample.write_bytes(b"locked")
    add_evidence(case_id, "locked.bin", "data/evidence/locked.bin", sha256_file(sample), 6)

    def fail_hash(path, chunk_size=1024 * 1024):
        raise PermissionError("permission denied")

    monkeypatch.setattr(core, "sha256_file", fail_hash)
    report = verify_all_evidence()
    assert report["summary"]["unreadable"] == 1
    assert report["items"][0]["status"] == "unreadable"
    assert "OKUNAMADI" in export_integrity_markdown(case_id)


def test_validate_topology_payload_normalizes_and_deduplicates():
    devices, links = core.validate_topology_payload({
        "devices": [
            {"name": " PC-01 ", "type": "PC", "ip": "192.168.10.10/24", "gateway": "192.168.10.1"},
            {"name": "R1", "type": "Router", "ip": "192.168.10.1/24"},
        ],
        "links": [
            {"from": "PC-01", "to": "R1"},
            {"from": "R1", "to": "PC-01"},
        ],
    })
    assert devices[0]["name"] == "PC-01"
    assert devices[1]["gateway"] == ""
    assert links == [("PC-01", "R1")]


@pytest.mark.parametrize(
    "payload",
    [
        [],
        {},
        {"devices": []},
        {"devices": [{"name": ""}]},
        {"devices": [{"name": "A"}, {"name": "A"}]},
        {"devices": [{"name": "A"}], "links": [{"from": "A", "to": "B"}]},
        {"devices": [{"name": "A"}], "links": [{"from": "A", "to": "A"}]},
        {"devices": [{"name": "A"}], "links": ["A-B"]},
    ],
)
def test_validate_topology_payload_rejects_malformed_input(payload):
    with pytest.raises(ValueError):
        core.validate_topology_payload(payload)

