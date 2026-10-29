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

def add_case(name, description="", status="Açık"):
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
    with get_conn() as con:
        cur = con.execute("""INSERT INTO evidence(case_id,filename,stored_path,sha256,size_bytes,note,created_at)
            VALUES(?,?,?,?,?,?,?)""",
            (case_id, filename, stored_path, digest, size_bytes, note, now_utc()))
        return cur.lastrowid

def list_evidence(case_id):
    with get_conn() as con:
        return [dict(r) for r in con.execute("SELECT * FROM evidence WHERE case_id=? ORDER BY id DESC", (case_id,))]

def verify_evidence(evidence_id):
    with get_conn() as con:
        row = con.execute("SELECT * FROM evidence WHERE id=?", (evidence_id,)).fetchone()
        if not row:
            raise ValueError("Kanıt kaydı bulunamadı.")
        item = dict(row)
    path = (APP_DIR / item["stored_path"]).resolve()
    evidence_root = (APP_DIR / "data" / "evidence").resolve()
    if evidence_root not in path.parents or not path.is_file():
        return {"exists": False, "matches": False, "current_sha256": None}
    current = sha256_file(path)
    return {"exists": True, "matches": current == item["sha256"], "current_sha256": current}

def add_source(case_id, title, url="", source_type="Diğer", accessed_at="", notes=""):
    with get_conn() as con:
        cur = con.execute("""INSERT INTO sources(case_id,title,url,source_type,accessed_at,notes,created_at)
            VALUES(?,?,?,?,?,?,?)""", (case_id,title,url,source_type,accessed_at,notes,now_utc()))
        return cur.lastrowid

def list_sources(case_id):
    with get_conn() as con:
        return [dict(r) for r in con.execute("SELECT * FROM sources WHERE case_id=? ORDER BY id DESC", (case_id,))]

def add_finding(case_id, title, details, confidence="Orta", source_id=None):
    with get_conn() as con:
        if source_id is not None:
            valid = con.execute("SELECT id FROM sources WHERE id=? AND case_id=?", (source_id, case_id)).fetchone()
            if not valid:
                raise ValueError("Kaynak aynı vakaya ait olmalıdır.")
        cur = con.execute("""INSERT INTO findings(case_id,title,details,confidence,source_id,created_at)
            VALUES(?,?,?,?,?,?)""", (case_id,title,details,confidence,source_id,now_utc()))
        return cur.lastrowid

def list_findings(case_id):
    with get_conn() as con:
        return [dict(r) for r in con.execute("SELECT * FROM findings WHERE case_id=? ORDER BY id DESC", (case_id,))]

def add_event(case_id, title, event_time_utc, description="", timezone_note=""):
    with get_conn() as con:
        cur = con.execute("""INSERT INTO events(case_id,title,event_time_utc,timezone_note,description,created_at)
            VALUES(?,?,?,?,?,?)""", (case_id,title,event_time_utc,timezone_note,description,now_utc()))
        return cur.lastrowid

def list_events(case_id):
    with get_conn() as con:
        return [dict(r) for r in con.execute("SELECT * FROM events WHERE case_id=? ORDER BY event_time_utc ASC, id ASC", (case_id,))]

def add_relationship(case_id, left_node, right_node, label="ilişkili"):
    if left_node == right_node:
        raise ValueError("Bir kayıt kendisiyle ilişkilendirilemez.")
    with get_conn() as con:
        cur = con.execute("""INSERT OR IGNORE INTO relationships(case_id,left_node,right_node,label,created_at)
            VALUES(?,?,?,?,?)""", (case_id,left_node,right_node,label,now_utc()))
        return cur.lastrowid

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
