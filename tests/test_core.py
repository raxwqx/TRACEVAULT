import io
import os
import tempfile
from pathlib import Path
import hashlib
import json
import zipfile
import pytest

from tracevault import core
from tracevault.core import sha256_file

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


def test_case_bundle_contains_verified_evidence_and_manifest(tmp_path, monkeypatch):
    evidence = tmp_path / "data" / "evidence" / "evidence.bin"
    evidence.parent.mkdir(parents=True)
    evidence.write_bytes(b"case evidence")
    digest = hashlib.sha256(evidence.read_bytes()).hexdigest()
    item = {
        "id": 7, "filename": "evidence.bin", "stored_path": "data/evidence/evidence.bin",
        "sha256": digest, "size_bytes": evidence.stat().st_size,
    }
    monkeypatch.setattr(core, "APP_DIR", tmp_path)
    monkeypatch.setattr(core, "export_case_data", lambda case_id: {
        "schema_version": "1.0", "case": {"id": case_id}, "evidence": [item],
    })
    monkeypatch.setattr(core, "verify_evidence", lambda evidence_id: {
        "exists": True, "matches": evidence_id == 7,
    })

    bundle = core.export_case_bundle(3)
    with zipfile.ZipFile(io.BytesIO(bundle)) as archive:
        assert archive.namelist() == ["evidence/7_evidence.bin", "manifest.json"]
        assert archive.read("evidence/7_evidence.bin") == b"case evidence"
        manifest = json.loads(archive.read("manifest.json"))
    assert manifest["bundle_files"] == [{
        "path": "evidence/7_evidence.bin", "sha256": digest, "size_bytes": len(b"case evidence"),
    }]


def test_case_bundle_refuses_changed_or_missing_evidence(tmp_path, monkeypatch):
    item = {"id": 9, "filename": "lost.bin", "stored_path": "data/evidence/lost.bin", "sha256": "0" * 64, "size_bytes": 1}
    monkeypatch.setattr(core, "APP_DIR", tmp_path)
    monkeypatch.setattr(core, "export_case_data", lambda case_id: {"case": {"id": case_id}, "evidence": [item]})
    monkeypatch.setattr(core, "verify_evidence", lambda evidence_id: {"exists": True, "matches": False})
    with pytest.raises(ValueError, match="missing or has changed"):
        core.export_case_bundle(3)
