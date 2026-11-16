from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
from .db import get_conn, APP_DIR


def now_utc():
    return datetime.now(timezone.utc).isoformat()


def sha256_file(path, chunk_size=1024 * 1024):
    digest = hashlib.sha256()
    with open(path, "rb") as stream:
        for chunk in iter(lambda: stream.read(chunk_size), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _required(value, label):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{label} zorunludur.")
    return value.strip()


def _require_case(case_id):
    if case_id is None or not get_case(case_id):
        raise ValueError("Vaka bulunamadı.")


def add_case(name, description="", status="Açık"):
    name = _required(name, "Vaka adı")
    with get_conn() as con:
        cur = con.execute("INSERT INTO cases(name,description,status,created_at) VALUES(?,?,?,?)",
                          (name, description, status, now_utc()))
        return cur.lastrowid


def list_cases():
    with get_conn() as con:
        return [dict(r) for r in con.execute("SELECT * FROM cases ORDER BY id DESC")]


def get_case(case_id):
    with get_conn() as con:
        row = con.execute("SELECT * FROM cases WHERE id=?", (case_id,)).fetchone()
        return dict(row) if row else None


def add_evidence(case_id, filename, stored_path, digest, size_bytes, note=""):
    _require_case(case_id)
    filename = _required(filename, "Dosya adı")
    with get_conn() as con:
        cur = con.execute("""INSERT INTO evidence(case_id,filename,stored_path,sha256,size_bytes,note,created_at)
            VALUES(?,?,?,?,?,?,?)""",
            (case_id, filename, stored_path, digest, size_bytes, note, now_utc()))
        return cur.lastrowid


def list_evidence(case_id):
    with get_conn() as con:
        return [dict(r) for r in con.execute("SELECT * FROM evidence WHERE case_id=? ORDER BY id DESC", (case_id,))]


def _resolve_evidence_path(stored_path):
    """Resolve a stored evidence path and keep it inside data/evidence/."""
    raw = Path(stored_path)
    path = raw if raw.is_absolute() else APP_DIR / raw
    return path.resolve()


def _evidence_root():
    return (APP_DIR / "data" / "evidence").resolve()


def _check_evidence_file(stored_path, expected_sha256):
    """Return the verification state of one stored evidence file."""
    try:
        path = _resolve_evidence_path(stored_path)
    except (OSError, ValueError):
        return {"exists": False, "matches": False, "current_sha256": None, "status": "missing"}

    if not path.is_relative_to(_evidence_root()) or not path.is_file():
        return {"exists": False, "matches": False, "current_sha256": None, "status": "missing"}

    try:
        current = sha256_file(path)
    except OSError:
        return {"exists": True, "matches": False, "current_sha256": None, "status": "unreadable"}

    matches = current == expected_sha256
    return {
        "exists": True,
        "matches": matches,
        "current_sha256": current,
        "status": "verified" if matches else "mismatched",
    }


def verify_evidence(evidence_id):
    with get_conn() as con:
        row = con.execute("SELECT * FROM evidence WHERE id=?", (evidence_id,)).fetchone()
        if not row:
            raise ValueError("Kanıt kaydı bulunamadı.")
        item = dict(row)
    return _check_evidence_file(item["stored_path"], item["sha256"])


def verify_all_evidence(case_id=None):
    """Verify every stored evidence file, optionally limited to one case.

    Returns a dict with a ``summary`` block and one result per evidence item.
    The sweep never modifies files; it only reads their SHA-256 digests.
    """
    if case_id is not None:
        _require_case(case_id)

    with get_conn() as con:
        sql = """SELECT e.*, c.name AS case_name
                 FROM evidence e JOIN cases c ON c.id = e.case_id"""
        args = ()
        if case_id is not None:
            sql += " WHERE e.case_id = ?"
            args = (case_id,)
        sql += " ORDER BY e.case_id ASC, e.id ASC"
        records = [dict(r) for r in con.execute(sql, args)]

    items = []
    for record in records:
        check = _check_evidence_file(record["stored_path"], record["sha256"])
        items.append({
            "evidence_id": record["id"],
            "case_id": record["case_id"],
            "case_name": record["case_name"],
            "filename": record["filename"],
            "sha256": record["sha256"],
            "size_bytes": record["size_bytes"],
            "created_at": record["created_at"],
            **check,
        })

    summary = {"total": len(items), "verified": 0, "mismatched": 0, "missing": 0, "unreadable": 0}
    for item in items:
        summary[item["status"]] += 1

    return {
        "generated_at_utc": now_utc(),
        "case_id": case_id,
        "summary": summary,
        "items": items,
    }


def export_integrity_data(case_id=None, result=None):
    data = result if result is not None else verify_all_evidence(case_id)
    return {
        "schema_version": "1.0",
        "generated_at_utc": data["generated_at_utc"],
        "scope": {"case_id": case_id},
        "summary": data["summary"],
        "items": data["items"],
        "limitations": [
            "SHA-256 eşleşmesi yalnızca dosyanın kayıtlı özetle aynı olduğunu gösterir.",
            "Eksik veya uyuşmayan kayıtlar kötü niyet kanıtı değildir; taşınma, kopyalama veya disk hatası da olabilir.",
            "Bu rapor hukuki veya adli geçerlilik garantisi vermez.",
        ],
    }


def export_integrity_json(case_id=None, result=None):
    return json.dumps(export_integrity_data(case_id, result), ensure_ascii=False, indent=2)


def export_integrity_markdown(case_id=None, result=None):
    data = export_integrity_data(case_id, result)
    summary = data["summary"]
    scope = f"Vaka #{case_id}" if case_id is not None else "Tüm vakalar"
    status_labels = {
        "verified": "DOĞRULANDI",
        "mismatched": "UYUŞMUYOR",
        "missing": "DOSYA YOK",
        "unreadable": "OKUNAMADI",
    }
    lines = [
        "# TRACEVAULT Bütünlük Taraması",
        "",
        f"- **Kapsam:** {scope}",
        f"- **Tarama (UTC):** {data['generated_at_utc']}",
        f"- **Toplam kayıt:** {summary['total']}",
        f"- **Doğrulanan:** {summary['verified']}",
        f"- **Uyuşmayan:** {summary['mismatched']}",
        f"- **Eksik dosya:** {summary['missing']}",
        f"- **Okunamayan dosya:** {summary['unreadable']}",
        "",
        "## Kanıt Durumu",
        "",
    ]
    if data["items"]:
        for item in data["items"]:
            lines += [
                f"### #{item['evidence_id']} · {item['filename']}",
                f"- **Durum:** {status_labels[item['status']]}",
                f"- **Vaka:** #{item['case_id']} · {item['case_name']}",
                f"- **Kayıtlı SHA-256:** `{item['sha256']}`",
                f"- **Güncel SHA-256:** `{item['current_sha256'] or '—'}`",
                f"- **Boyut:** {item['size_bytes']} bayt",
                f"- **Kayıt:** {item['created_at']}",
                "",
            ]
    else:
        lines += ["Kanıt kaydı yok.", ""]
    lines += ["## Sınırlamalar", ""]
    lines += [f"- {item}" for item in data["limitations"]]
    lines += ["", "---", "TRACEVAULT tarafından oluşturuldu."]
    return "\n".join(lines)


def validate_topology_payload(payload):
    """Validate an imported topology JSON payload before it reaches the UI."""
    if not isinstance(payload, dict):
        raise ValueError("Topoloji bir JSON nesnesi olmalıdır.")
    devices = payload.get("devices")
    links = payload.get("links", [])
    if not isinstance(devices, list) or not devices:
        raise ValueError("'devices' boş olmayan bir liste olmalıdır.")
    if not isinstance(links, list):
        raise ValueError("'links' bir liste olmalıdır.")

    clean_devices = []
    names = set()
    for item in devices:
        if not isinstance(item, dict):
            raise ValueError("Her cihaz bir JSON nesnesi olmalıdır.")
        name = str(item.get("name", "")).strip()
        if not name:
            raise ValueError("Cihaz adı boş olamaz.")
        if name in names:
            raise ValueError(f"Tekrarlanan cihaz adı: {name}")
        names.add(name)
        device_type = str(item.get("type", "PC")).strip() or "PC"
        clean_devices.append({
            "name": name,
            "type": device_type,
            "ip": str(item.get("ip", "")).strip(),
            "gateway": str(item.get("gateway", "")).strip(),
        })

    clean_links = []
    seen_pairs = set()
    for item in links:
        if not isinstance(item, dict):
            raise ValueError("Her bağlantı bir JSON nesnesi olmalıdır.")
        left = str(item.get("from", "")).strip()
        right = str(item.get("to", "")).strip()
        if not left or not right:
            raise ValueError("Her bağlantı 'from' ve 'to' alanlarını içermelidir.")
        if left not in names or right not in names:
            raise ValueError("Bağlantı bilinmeyen bir cihaza işaret ediyor.")
        if left == right:
            raise ValueError("Cihaz kendisine bağlanamaz.")
        pair = frozenset((left, right))
        if pair in seen_pairs:
            continue
        seen_pairs.add(pair)
        clean_links.append((left, right))

    return clean_devices, clean_links


def add_source(case_id, title, url="", source_type="Diğer", accessed_at="", notes=""):
    _require_case(case_id)
    title = _required(title, "Kaynak başlığı")
    with get_conn() as con:
        cur = con.execute("""INSERT INTO sources(case_id,title,url,source_type,accessed_at,notes,created_at)
            VALUES(?,?,?,?,?,?,?)""", (case_id, title, url, source_type, accessed_at, notes, now_utc()))
        return cur.lastrowid


def list_sources(case_id):
    with get_conn() as con:
        return [dict(r) for r in con.execute("SELECT * FROM sources WHERE case_id=? ORDER BY id DESC", (case_id,))]


def add_finding(case_id, title, details, confidence="Orta", source_id=None):
    _require_case(case_id)
    title = _required(title, "Bulgu başlığı")
    details = _required(details, "Bulgu açıklaması")
    with get_conn() as con:
        if source_id is not None:
            valid = con.execute("SELECT id FROM sources WHERE id=? AND case_id=?", (source_id, case_id)).fetchone()
            if not valid:
                raise ValueError("Kaynak aynı vakaya ait olmalıdır.")
        cur = con.execute("""INSERT INTO findings(case_id,title,details,confidence,source_id,created_at)
            VALUES(?,?,?,?,?,?)""", (case_id, title, details, confidence, source_id, now_utc()))
        return cur.lastrowid


def list_findings(case_id):
    with get_conn() as con:
        return [dict(r) for r in con.execute("SELECT * FROM findings WHERE case_id=? ORDER BY id DESC", (case_id,))]


def add_event(case_id, title, event_time_utc, description="", timezone_note=""):
    _require_case(case_id)
    title = _required(title, "Olay adı")
    with get_conn() as con:
        cur = con.execute("""INSERT INTO events(case_id,title,event_time_utc,timezone_note,description,created_at)
            VALUES(?,?,?,?,?,?)""", (case_id, title, event_time_utc, timezone_note, description, now_utc()))
        return cur.lastrowid


def list_events(case_id):
    with get_conn() as con:
        return [dict(r) for r in con.execute("SELECT * FROM events WHERE case_id=? ORDER BY event_time_utc ASC, id ASC", (case_id,))]


def add_relationship(case_id, left_node, right_node, label="ilişkili"):
    _require_case(case_id)
    left_node = _required(left_node, "Sol düğüm")
    right_node = _required(right_node, "Sağ düğüm")
    if left_node == right_node:
        raise ValueError("Bir kayıt kendisiyle ilişkilendirilemez.")
    with get_conn() as con:
        con.execute("""INSERT OR IGNORE INTO relationships(case_id,left_node,right_node,label,created_at)
            VALUES(?,?,?,?,?)""", (case_id, left_node, right_node, label, now_utc()))
        row = con.execute("""SELECT id FROM relationships
            WHERE case_id=? AND left_node=? AND right_node=? AND label=?""",
            (case_id, left_node, right_node, label)).fetchone()
        return row["id"] if row else None


def list_relationships(case_id):
    with get_conn() as con:
        return [dict(r) for r in con.execute("SELECT * FROM relationships WHERE case_id=? ORDER BY id", (case_id,))]


def export_case_data(case_id):
    case = get_case(case_id)
    if not case:
        raise ValueError("Vaka bulunamadı.")
    return {
        "schema_version": "1.0",
        "generated_at_utc": now_utc(),
        "case": case,
        "evidence": list_evidence(case_id),
        "sources": list_sources(case_id),
        "findings": list_findings(case_id),
        "events": list_events(case_id),
        "relationships": list_relationships(case_id),
        "limitations": [
            "SHA-256 eşleşmesi tek başına kaynağı veya gerçekliği kanıtlamaz.",
            "Bu rapor uygulama tarafından oluşturulmuştur; hukuki veya adli geçerlilik garantisi vermez."
        ]
    }


def export_case_json(case_id):
    return json.dumps(export_case_data(case_id), ensure_ascii=False, indent=2)


def export_case_markdown(case_id):
    data = export_case_data(case_id)
    c = data["case"]
    lines = [
        f"# TRACEVAULT Vaka Raporu: {c['name']}",
        "",
        f"- **Vaka ID:** {c['id']}",
        f"- **Durum:** {c['status']}",
        f"- **Oluşturulma:** {c['created_at']}",
        f"- **Rapor oluşturulma (UTC):** {data['generated_at_utc']}",
        "",
        "## Açıklama", "", c["description"] or "Açıklama girilmemiş.", "",
        "## Kanıtlar", ""
    ]
    if data["evidence"]:
        for e in data["evidence"]:
            lines += [f"### Kanıt #{e['id']}: {e['filename']}", f"- SHA-256: `{e['sha256']}`",
                      f"- Boyut: {e['size_bytes']} bayt", f"- Kayıt: {e['created_at']}",
                      f"- Not: {e['note'] or '—'}", ""]
    else:
        lines += ["Kanıt kaydı yok.", ""]
    lines += ["## Kaynaklar", ""]
    if data["sources"]:
        for s in data["sources"]:
            lines += [f"### Kaynak #{s['id']}: {s['title']}", f"- Tür: {s['source_type']}",
                      f"- URL: {s['url'] or '—'}", f"- Erişim tarihi: {s['accessed_at'] or '—'}",
                      f"- Not: {s['notes'] or '—'}", ""]
    else:
        lines += ["Kaynak kaydı yok.", ""]
    lines += ["## Bulgular", ""]
    if data["findings"]:
        for f in data["findings"]:
            lines += [f"### Bulgu #{f['id']}: {f['title']}", f"- Güven düzeyi: {f['confidence']}",
                      f"- Kaynak ID: {f['source_id'] or 'atanmamış'}", "", f["details"], ""]
    else:
        lines += ["Bulgu kaydı yok.", ""]
    lines += ["## Olay Zaman Çizelgesi", ""]
    if data["events"]:
        for e in data["events"]:
            lines += [f"- **{e['event_time_utc']}** · {e['title']} ({e['timezone_note']})",
                      f"  - {e['description'] or 'Açıklama yok.'}"]
    else:
        lines += ["Olay kaydı yok."]
    lines += ["", "## İlişkiler", ""]
    if data["relationships"]:
        for r in data["relationships"]:
            lines.append(f"- {r['left_node']} — **{r['label']}** — {r['right_node']}")
    else:
        lines.append("İlişki kaydı yok.")
    lines += ["", "## Sınırlamalar", ""]
    lines += [f"- {item}" for item in data["limitations"]]
    lines += ["", "---", "TRACEVAULT tarafından oluşturuldu."]
    return "\n".join(lines)
