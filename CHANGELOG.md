# Changelog

## [0.3.0] - 2026-11-16

### Added

- **Integrity Sweep** (`Bütünlük Taraması`): re-hash all stored evidence across
  every case or a single case, classify results as verified / mismatched /
  missing, and export Markdown or JSON reports. The sweep is read-only.
- Core helpers: `verify_all_evidence`, `export_integrity_data`,
  `export_integrity_json`, `export_integrity_markdown`.
- Topology payload validation (`validate_topology_payload`) with clear errors.
- SECURITY.md and this changelog.
- Test coverage for evidence integrity, connection lifecycle, relationship IDs,
  input validation, and topology import.

### Fixed

- The “＋ New note / Yeni not” button now opens a blank editor instead of
  reloading the first note.
- SQLite connections are committed/rolled back and then closed. Previously the
  connection object leaked a file descriptor on every operation.
- Removing a Network Lab link or device now clears its stale link metadata.
- `add_relationship` returns the correct ID for both new and existing rows.
- Malformed topology JSON no longer crashes the app.
- Incomplete MIT license text; GitHub now detects the MIT license correctly.
- `pyproject.toml` version mismatch (0.1.0 vs the 0.2.0 UI build) and missing
  dependencies.

### Changed

- Evidence path verification uses `Path.is_relative_to` and rejects absolute
  paths outside `data/evidence/`.
- Database indexes added for case-scoped tables and note sorting.
- Runtime and development dependencies split into `requirements.txt` and
  `requirements-dev.txt`.
- CI runs on Python 3.11–3.13 with pip caching, read-only permissions, and a
  compile check.
