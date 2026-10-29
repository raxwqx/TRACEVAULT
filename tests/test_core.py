import os
import tempfile
from pathlib import Path
import pytest

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
