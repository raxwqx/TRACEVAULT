from datetime import datetime, timezone
from pathlib import Path
import json
import re
import subprocess
import shutil

import streamlit as st
import pandas as pd
import networkx as nx
import plotly.graph_objects as go

from tracevault.db import init_db, get_conn
from tracevault.core import (
    sha256_file, add_case, list_cases, add_evidence, list_evidence,
    verify_evidence, add_source, list_sources, add_finding, list_findings,
    add_event, list_events, add_relationship, list_relationships,
    export_case_markdown, export_case_json
)

APP_DIR = Path(__file__).resolve().parent
DATA_DIR = APP_DIR / "data"
EVIDENCE_DIR = DATA_DIR / "evidence"
DATA_DIR.mkdir(exist_ok=True)
EVIDENCE_DIR.mkdir(exist_ok=True)

st.set_page_config(page_title="TRACEVAULT // FIELD DESK", page_icon="⌘", layout="wide", initial_sidebar_state="expanded")
init_db()

# Retro terminal / old-school research desk aesthetic.
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600&family=IBM+Plex+Sans:wght@400;500;600&display=swap');
:root { --bg:#11130f; --panel:#191d17; --line:#414a35; --ink:#d5dfc3; --muted:#98a58a; --accent:#c2d879; --amber:#d6aa65; }
.stApp { background: radial-gradient(ellipse at top left,#20281b 0%,#11130f 58%,#0c0e0b 100%); color:var(--ink); font-family:'IBM Plex Sans',sans-serif; }
[data-testid="stSidebar"] { background:#0d100c; border-right:1px solid #37402f; }
[data-testid="stSidebar"] * { font-family:'IBM Plex Mono',monospace; }
h1,h2,h3,h4,p,span,label,div { } h1,h2,h3 { font-family:'IBM Plex Mono',monospace!important; letter-spacing:-.04em; }
h1 { color:#d9e6b9!important; } h2,h3 { color:#c2d879!important; }
[data-testid="stMetric"] { background:#191d17; border:1px solid #414a35; padding:12px 15px; border-radius:3px; }
[data-testid="stMetricLabel"] { color:#98a58a!important; font-family:'IBM Plex Mono',monospace; }
[data-testid="stMetricValue"] { color:#d9e6b9!important; font-family:'IBM Plex Mono',monospace; }
.stButton>button, .stDownloadButton>button, [data-testid="stFormSubmitButton"] button { border-radius:2px; border:1px solid #69794b; background:#252d1c; color:#e1edc7; font-family:'IBM Plex Mono',monospace; }
.stButton>button:hover, .stDownloadButton>button:hover { border-color:#c2d879; color:#fff; }
input,textarea,[data-baseweb="select"]>div { border-radius:2px!important; }
.tv-banner { border:1px solid #414a35; background:rgba(25,29,23,.82); padding:14px 16px; font-family:'IBM Plex Mono',monospace; color:#aab99a; }
.tv-kicker { color:#c2d879; font-family:'IBM Plex Mono',monospace; font-size:12px; letter-spacing:.12em; }
.tv-rule { border-top:1px dashed #414a35; margin:12px 0; }
[data-testid="stExpander"] { border-radius:2px!important; border:1px solid #414a35!important; }
footer { visibility:hidden; }
</style>
""", unsafe_allow_html=True)

PAGES = [
    "Desk / Genel Bakış", "Bilgi Kasası", "Graf Bağlantıları", "Vakalar", "Kanıt Kasası",
    "Kaynaklar ve Bulgular", "Zaman Çizelgesi", "Rapor Merkezi", "Wi-Fi Radarı", "Ağ Laboratuvarı", "Ayarlar"
]

def now_iso():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")

def db_notes(search="", folder=None):
    with get_conn() as con:
        sql = "SELECT * FROM notes WHERE 1=1"
        args = []
        if search:
            sql += " AND (title LIKE ? OR content LIKE ? OR tags LIKE ?)"
            q = f"%{search}%"
            args.extend([q, q, q])
        if folder and folder != "Tüm klasörler":
            sql += " AND folder=?"
            args.append(folder)
        sql += " ORDER BY updated_at DESC, id DESC"
        return [dict(r) for r in con.execute(sql, args)]

def save_note(note_id, title, content, folder, tags):
    stamp = now_iso()
    with get_conn() as con:
        if note_id:
            con.execute("UPDATE notes SET title=?,content=?,folder=?,tags=?,updated_at=? WHERE id=?",
                        (title, content, folder, tags, stamp, note_id))
        else:
            con.execute("INSERT INTO notes(title,content,folder,tags,created_at,updated_at) VALUES(?,?,?,?,?,?)",
                        (title, content, folder, tags, stamp, stamp))

def delete_note(note_id):
    with get_conn() as con:
        con.execute("DELETE FROM notes WHERE id=?", (note_id,))

def wifi_scan():
    if not shutil.which("nmcli"):
        return None, "nmcli bulunamadı. NetworkManager kurulu ve çalışır durumda olmalı."
    try:
        result = subprocess.run(
            ["nmcli", "-t", "-f", "IN-USE,SSID,BSSID,CHAN,FREQ,RATE,SIGNAL,SECURITY", "dev", "wifi", "list", "--rescan", "yes"],
            capture_output=True, text=True, timeout=20, check=False
        )
        if result.returncode != 0:
            return None, (result.stderr.strip() or "Wi-Fi taraması başarısız oldu.")
        rows = []
        for line in result.stdout.splitlines():
            # nmcli escapes colons/backslashes in terse mode; split only the known fields.
            parts = re.split(r"(?<!\\):", line)
            if len(parts) < 8:
                continue
            parts = [p.replace(r"\:", ":").replace(r"\\", "\\") for p in parts]
            rows.append({"Bağlı": "Evet" if parts[0] == "*" else "", "SSID": parts[1] or "(gizli ağ)",
                         "BSSID": parts[2], "Kanal": parts[3], "Frekans": parts[4],
                         "Hız": parts[5], "Sinyal (%)": int(parts[6]) if parts[6].isdigit() else 0,
                         "Güvenlik": parts[7]})
        return rows, None
    except subprocess.TimeoutExpired:
        return None, "Wi-Fi taraması zaman aşımına uğradı."
    except Exception as exc:
        return None, f"Tarama hatası: {exc}"

def parse_ip(ip):
    import ipaddress
    return ipaddress.ip_interface(ip)

with st.sidebar:
    st.markdown("# ⌘ TRACEVAULT")
    st.caption("FIELD DESK  /  LOCAL RESEARCH SYSTEM")
    st.markdown('<div class="tv-rule"></div>', unsafe_allow_html=True)
    page = st.radio("NAVIGASYON", PAGES, label_visibility="collapsed")
    st.markdown('<div class="tv-rule"></div>', unsafe_allow_html=True)
    st.caption("MODE: LOCAL-FIRST")
    st.caption("BUILD: 0.2.0 // RETRO DESK")
    st.caption("VERİLER: BU BİLGİSAYARDA")

st.markdown('<div class="tv-kicker">STYX LABS  /  RESEARCH CONSOLE  /  TR</div>', unsafe_allow_html=True)
st.title("TRACEVAULT")
st.markdown('<div class="tv-banner">[ READY ]  Kişisel bilgi kasası · OSINT notları · dijital inceleme · Wi-Fi gözlemi · ağ simülatörü</div>', unsafe_allow_html=True)
st.write("")

cases = list_cases()
case_options = {f'#{c["id"]} · {c["name"]}': c["id"] for c in cases}
with st.sidebar:
    st.subheader("AKTİF VAKA")
    if case_options:
        chosen_label = st.selectbox("Vaka seç", list(case_options.keys()), label_visibility="collapsed")
        active_case = case_options[chosen_label]
    else:
        active_case = None
        st.caption("Henüz vaka yok")

if page == "Desk / Genel Bakış":
    total_evidence = sum(len(list_evidence(c["id"])) for c in cases)
    total_findings = sum(len(list_findings(c["id"])) for c in cases)
    notes = db_notes()
    a,b,c,d = st.columns(4)
    a.metric("VAKA DOSYALARI", len(cases))
    b.metric("BİLGİ NOTLARI", len(notes))
    c.metric("KANIT KAYITLARI", total_evidence)
    d.metric("BULGULAR", total_findings)
    st.subheader("Çalışma masası")
    left, right = st.columns([1.25, 1])
    with left:
        st.markdown("#### Hızlı erişim")
        st.markdown("""
        <div class="tv-banner">
        01 / <b>Bilgi Kasası</b> · Markdown notları, klasörler, etiketler, wikilink bağlantıları<br><br>
        02 / <b>Wi-Fi Radarı</b> · Yakındaki SSID ve sinyal bilgilerini yerel olarak görüntüle<br><br>
        03 / <b>Ağ Laboratuvarı</b> · Router, switch, PC, server ve firewall ile sanal topoloji kur<br><br>
        04 / <b>Kanıt Kasası</b> · Dosya kaydı ve SHA-256 bütünlük kontrolü
        </div>
        """, unsafe_allow_html=True)
    with right:
        st.markdown("#### Son notlar")
        if notes:
            for note in notes[:5]:
                st.markdown(f"**{note['title']}**  ·  `{note['folder']}`")
                st.caption(f"Güncelleme: {note['updated_at']}")
        else:
            st.info("Bilgi Kasası'nda ilk notunu oluştur.")
    st.warning("Wi-Fi bölümü yalnızca yakındaki ağların yayınlanan temel bilgilerini görüntüler. Bağlanma, paket yakalama, parola deneme veya başka ağlara müdahale yapmaz.")

elif page == "Bilgi Kasası":
    st.subheader("Bilgi Kasası / Markdown Vault")
    st.caption("Notları yerel SQLite veritabanında tutar. İçerikte [[Not Başlığı]] kullanarak diğer notlara bağlantı verebilirsin.")
    all_notes = db_notes()
    folders = sorted(set(n["folder"] for n in all_notes))
    top1, top2, top3 = st.columns([1.5, 1, 1])
    with top1: search = st.text_input("Notlarda ara", placeholder="başlık, içerik veya etiket...")
    with top2: folder_filter = st.selectbox("Klasör", ["Tüm klasörler"] + folders)
    with top3: st.write(""); new_note = st.button("＋ Yeni not", use_container_width=True)
    filtered = db_notes(search, folder_filter)
    left, right = st.columns([0.85, 1.5])
    with left:
        st.markdown("#### Not defteri")
        if filtered:
            selected = st.radio("Not seç", [f"{n['id']} · {n['title']}" for n in filtered], label_visibility="collapsed")
            selected_id = int(selected.split(" · ", 1)[0])
            selected_note = next(n for n in filtered if n["id"] == selected_id)
        else:
            selected_note = None
            st.info("Bu filtrede not yok.")
        if new_note:
            st.session_state["editing_note_id"] = None
            st.session_state["note_title"] = ""
            st.session_state["note_content"] = ""
            st.session_state["note_folder"] = "Gelen Kutusu"
            st.session_state["note_tags"] = ""
            st.rerun()
        elif selected_note and st.session_state.get("editing_note_id", "unset") == "unset":
            st.session_state["editing_note_id"] = selected_note["id"]
            st.session_state["note_title"] = selected_note["title"]
            st.session_state["note_content"] = selected_note["content"]
            st.session_state["note_folder"] = selected_note["folder"]
            st.session_state["note_tags"] = selected_note["tags"]
        elif selected_note and st.session_state.get("editing_note_id") != selected_note["id"] and not st.session_state.get("manual_edit", False):
            st.session_state["editing_note_id"] = selected_note["id"]
            st.session_state["note_title"] = selected_note["title"]
            st.session_state["note_content"] = selected_note["content"]
            st.session_state["note_folder"] = selected_note["folder"]
            st.session_state["note_tags"] = selected_note["tags"]
    with right:
        st.markdown("#### Düzenleyici")
        with st.form("note_editor", clear_on_submit=False):
            title = st.text_input("Başlık", key="note_title")
            folder = st.text_input("Klasör", key="note_folder")
            tags = st.text_input("Etiketler (virgülle ayır)", key="note_tags", placeholder="osint, araştırma, ağ")
            content = st.text_area("Markdown içeriği", key="note_content", height=300, placeholder="# Başlık\n\nAraştırma notların...\n\nİlgili: [[Başka bir not]]")
            saved = st.form_submit_button("Notu kaydet", type="primary")
            if saved:
                if not title.strip():
                    st.error("Not başlığı gerekli.")
                else:
                    save_note(st.session_state.get("editing_note_id"), title.strip(), content, folder.strip() or "Gelen Kutusu", tags.strip())
                    st.session_state["manual_edit"] = False
                    st.success("Not kaydedildi.")
                    st.rerun()
        if selected_note and st.session_state.get("editing_note_id") == selected_note["id"]:
            with st.expander("Önizleme / Markdown"):
                st.markdown(st.session_state.get("note_content", selected_note["content"]))
            if st.button("Seçili notu sil", key=f"delete_note_{selected_note['id']}"):
                delete_note(selected_note["id"])
                st.session_state["editing_note_id"] = None
                st.rerun()
    # Wiki links / orphan overview
    all_titles = {n["title"] for n in all_notes}
    if all_notes:
        st.markdown("#### Bağlantı denetimi")
        links = []
        for n in all_notes:
            targets = re.findall(r"\[\[([^\]]+)\]\]", n["content"])
            for target in targets:
                links.append({"Kaynak not": n["title"], "Hedef not": target.strip(), "Durum": "Bağlı" if target.strip() in all_titles else "Hedef eksik"})
        if links:
            st.dataframe(pd.DataFrame(links), use_container_width=True, hide_index=True)
        else:
            st.caption("Henüz [[not bağlantısı]] bulunmuyor.")
    st.download_button("Notları JSON olarak dışa aktar", data=json.dumps(all_notes, ensure_ascii=False, indent=2), file_name="tracevault-notes.json", mime="application/json")

elif page == "Graf Bağlantıları":
    st.subheader("Bilgi grafiği")
    notes = db_notes()
    G = nx.Graph()
    title_set = {n["title"] for n in notes}
    for n in notes:
        G.add_node(n["title"], folder=n["folder"])
        for target in re.findall(r"\[\[([^\]]+)\]\]", n["content"]):
            target = target.strip()
            if target in title_set:
                G.add_edge(n["title"], target)
    if G.number_of_nodes():
        pos = nx.spring_layout(G, seed=17, k=0.9)
        edge_x, edge_y = [], []
        for u, v in G.edges():
            edge_x += [pos[u][0], pos[v][0], None]
            edge_y += [pos[u][1], pos[v][1], None]
        node_x = [pos[n][0] for n in G.nodes()]
        node_y = [pos[n][1] for n in G.nodes()]
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=edge_x, y=edge_y, mode="lines", line=dict(width=1, color="#65734b"), hoverinfo="none"))
        fig.add_trace(go.Scatter(x=node_x, y=node_y, mode="markers+text", text=list(G.nodes()), textposition="top center",
                                 marker=dict(size=18, color="#c2d879", line=dict(width=1, color="#11130f")), hovertext=[G.nodes[n].get("folder", "") for n in G.nodes()], hoverinfo="text+name"))
        fig.update_layout(paper_bgcolor="#11130f", plot_bgcolor="#11130f", font=dict(color="#d5dfc3", family="IBM Plex Mono"),
                          margin=dict(l=10,r=10,t=20,b=10), showlegend=False, xaxis=dict(visible=False), yaxis=dict(visible=False), height=550)
        st.plotly_chart(fig, use_container_width=True)
        st.caption(f"{G.number_of_nodes()} not · {G.number_of_edges()} bağlantı. Bağlantılar [[Not Başlığı]] biçiminden çıkarılır.")
    else:
        st.info("Grafiği oluşturmak için önce Bilgi Kasası'na birkaç not ekle.")

elif page == "Vakalar":
    st.subheader("Vaka dosyaları")
    with st.form("new_case", clear_on_submit=True):
        name = st.text_input("Vaka adı *", placeholder="Örn. OSINT araştırması 001")
        description = st.text_area("Kapsam / açıklama")
        status = st.selectbox("Durum", ["Açık", "İncelemede", "Tamamlandı", "Arşivlendi"])
        submitted = st.form_submit_button("Vaka oluştur", type="primary")
        if submitted:
            if not name.strip(): st.error("Vaka adı zorunludur.")
            else:
                add_case(name.strip(), description.strip(), status)
                st.success("Vaka oluşturuldu.")
                st.rerun()
    if cases: st.dataframe(pd.DataFrame(cases)[["id","name","status","description","created_at"]], use_container_width=True, hide_index=True)
    else: st.info("Henüz vaka yok.")

elif page == "Kanıt Kasası":
    st.subheader("Kanıt kasası / SHA-256")
    if not active_case: st.info("Önce Vakalar bölümünden bir vaka oluşturup seç.")
    else:
        upload = st.file_uploader("Dosya seç", key="evidence_upload")
        note = st.text_area("Dosyanın kaynağı ve bağlamı")
        if st.button("Kanıtı kaydet", disabled=upload is None, type="primary"):
            safe_name = Path(upload.name).name
            stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
            dest = EVIDENCE_DIR / f"case_{active_case}_{stamp}_{safe_name}"
            dest.write_bytes(upload.getvalue())
            digest = sha256_file(dest)
            add_evidence(active_case, safe_name, str(dest.relative_to(APP_DIR)), digest, dest.stat().st_size, note.strip())
            st.success(f"Kaydedildi. SHA-256: {digest}")
            st.rerun()
        records = list_evidence(active_case)
        for item in records:
            with st.expander(f"#{item['id']} · {item['filename']}"):
                st.code(item["sha256"])
                st.write(f"Boyut: {item['size_bytes']:,} bayt · Kayıt: {item['created_at']}")
                st.write(item["note"] or "Not yok")
                result = verify_evidence(item["id"])
                if result["exists"] and result["matches"]: st.success("SHA-256 eşleşiyor.")
                elif result["exists"]: st.error("SHA-256 uyuşmuyor.")
                else: st.error("Dosya bulunamadı.")

elif page == "Kaynaklar ve Bulgular":
    st.subheader("Kaynaklar ve bulgular")
    if not active_case: st.info("Önce bir vaka oluşturup seç.")
    else:
        tab1, tab2 = st.tabs(["Kaynak ekle", "Bulgu ekle"])
        with tab1:
            with st.form("source_form", clear_on_submit=True):
                title = st.text_input("Kaynak başlığı *")
                url = st.text_input("URL", placeholder="https://...")
                source_type = st.selectbox("Tür", ["Web sayfası", "Belge", "Görsel", "Görüşme notu", "Diğer"])
                accessed = st.date_input("Erişim tarihi")
                notes = st.text_area("Notlar")
                if st.form_submit_button("Kaydet"):
                    if not title.strip(): st.error("Başlık zorunlu.")
                    elif url and not url.startswith(("http://", "https://")): st.error("URL http:// veya https:// ile başlamalı.")
                    else:
                        add_source(active_case, title.strip(), url.strip(), source_type, accessed.isoformat(), notes.strip())
                        st.success("Kaynak eklendi."); st.rerun()
        with tab2:
            sources = list_sources(active_case)
            with st.form("finding_form", clear_on_submit=True):
                ftitle = st.text_input("Bulgu başlığı *")
                details = st.text_area("Açıklama *")
                confidence = st.select_slider("Güven", options=["Düşük", "Orta", "Yüksek"], value="Orta")
                source_label = st.selectbox("Kaynak", ["Kaynak yok"] + [f"#{s['id']} · {s['title']}" for s in sources])
                if st.form_submit_button("Bulguyu kaydet"):
                    if not ftitle.strip() or not details.strip(): st.error("Başlık ve açıklama gerekli.")
                    else:
                        sid = int(source_label.split(" · ")[0][1:]) if source_label != "Kaynak yok" else None
                        add_finding(active_case, ftitle.strip(), details.strip(), confidence, sid)
                        st.success("Bulgu eklendi."); st.rerun()
        st.markdown("#### Kaynak listesi")
        src = list_sources(active_case)
        if src: st.dataframe(pd.DataFrame(src)[["id","title","url","source_type","accessed_at"]], use_container_width=True, hide_index=True)
        st.markdown("#### Bulgu listesi")
        findings = list_findings(active_case)
        if findings:
            for f in findings:
                with st.expander(f"#{f['id']} · {f['title']} · Güven: {f['confidence']}"):
                    st.write(f["details"])
                    st.caption(f"Kaynak ID: {f['source_id'] or 'atanmamış'}")

elif page == "Zaman Çizelgesi":
    st.subheader("Olay zaman çizelgesi")
    if not active_case: st.info("Önce bir vaka oluşturup seç.")
    else:
        with st.form("event_form", clear_on_submit=True):
            title = st.text_input("Olay adı *")
            event_date = st.date_input("Tarih")
            event_time = st.time_input("Saat (yerel)")
            tz_note = st.text_input("Saat dilimi notu", value="Europe/Istanbul (UTC+03:00)")
            description = st.text_area("Açıklama")
            if st.form_submit_button("Olay ekle"):
                if not title.strip(): st.error("Olay adı gerekli.")
                else:
                    from datetime import datetime as dt, timezone as tz
                    local = dt.combine(event_date, event_time).astimezone()
                    utc = local.astimezone(tz.utc).isoformat()
                    add_event(active_case, title.strip(), utc, description.strip(), tz_note.strip())
                    st.success("Olay eklendi."); st.rerun()
        events = list_events(active_case)
        if events:
            for e in events:
                st.markdown(f"**{e['event_time_utc']}**  ·  {e['title']}")
                st.write(e["description"] or "Açıklama yok")
                st.divider()
        else: st.info("Zaman çizelgesinde olay yok.")

elif page == "Rapor Merkezi":
    st.subheader("Rapor merkezi")
    if not active_case: st.info("Önce bir vaka oluşturup seç.")
    else:
        case = next(c for c in cases if c["id"] == active_case)
        st.markdown(f"#### {case['name']}")
        st.download_button("Markdown raporu indir", export_case_markdown(active_case), file_name=f"tracevault-vaka-{active_case}.md", mime="text/markdown")
        st.download_button("JSON raporu indir", export_case_json(active_case), file_name=f"tracevault-vaka-{active_case}.json", mime="application/json")

elif page == "Wi-Fi Radarı":
    st.subheader("Wi-Fi Radarı / Yakındaki ağlar")
    st.markdown('<div class="tv-banner">PASSIVE VIEW · Yalnızca yerel kablosuz ağ listesini okur. Ağlara bağlanmaz, trafik yakalamaz ve parolaları denemez.</div>', unsafe_allow_html=True)
    st.write("")
    if st.button("↻ Şimdi tara", type="primary"):
        with st.spinner("Yakındaki ağlar listeleniyor..."):
            rows, error = wifi_scan()
        st.session_state["wifi_rows"] = rows
        st.session_state["wifi_error"] = error
        st.session_state["wifi_scan_at"] = now_iso()
    rows = st.session_state.get("wifi_rows")
    error = st.session_state.get("wifi_error")
    if error: st.error(error)
    elif rows is None:
        st.info("Taramayı başlatmak için 'Şimdi tara' düğmesine bas. Kali'de NetworkManager/nmcli gerekli.")
    elif not rows: st.info("Ağ bulunamadı veya kablosuz adaptör kapalı.")
    else:
        st.caption(f"Son tarama: {st.session_state.get('wifi_scan_at', '—')} · {len(rows)} ağ")
        df = pd.DataFrame(rows).sort_values("Sinyal (%)", ascending=False)
        st.dataframe(df, use_container_width=True, hide_index=True)
        chart = go.Figure(go.Bar(x=df["Sinyal (%)"], y=df["SSID"], orientation="h", marker_color="#a9c36a"))
        chart.update_layout(paper_bgcolor="#11130f", plot_bgcolor="#11130f", font=dict(color="#d5dfc3", family="IBM Plex Mono"),
                           xaxis_title="Sinyal (%)", yaxis_title="SSID", height=max(280, min(650, 32*len(df)+100)), margin=dict(l=10,r=10,t=10,b=10))
        st.plotly_chart(chart, use_container_width=True)
        st.download_button("CSV dışa aktar", df.to_csv(index=False).encode("utf-8-sig"), file_name="tracevault-wifi-observation.csv", mime="text/csv")
    with st.expander("Kali Linux'ta çalışmazsa"):
        st.code("nmcli device status\nnmcli radio wifi on\nnmcli dev wifi list")
        st.caption("Wi-Fi donanımı, sürücü ve NetworkManager durumuna göre sonuçlar değişebilir. Gizli SSID'ler yalnızca '(gizli ağ)' olarak görünebilir.")

elif page == "Ağ Laboratuvarı":
    st.subheader("Ağ Laboratuvarı / Topology Workbench")
    st.caption("Cisco Packet Tracer'dan ilham alan eğitim amaçlı simülatör. Gerçek ağlara paket göndermez; topoloji ve temel yapılandırmayı uygulama içinde simüle eder.")
    if "lab_nodes" not in st.session_state:
        st.session_state["lab_nodes"] = [
            {"name":"PC-01","type":"PC","ip":"192.168.10.10/24","gateway":"192.168.10.1"},
            {"name":"SW-01","type":"Switch","ip":"","gateway":""},
            {"name":"R1","type":"Router","ip":"192.168.10.1/24","gateway":""},
        ]
        st.session_state["lab_links"] = [("PC-01","SW-01"),("SW-01","R1")]
    nodes = st.session_state["lab_nodes"]
    links = st.session_state["lab_links"]
    tab_devices, tab_links, tab_cli, tab_checks = st.tabs(["Cihaz kataloğu", "Bağlantılar", "Komut konsolu", "Doğrulama"])
    with tab_devices:
        st.markdown("#### Kategori kataloğu")
        categories = {
            "Son cihazlar": ["PC", "Laptop", "Server", "Printer", "IoT"],
            "Ağ cihazları": ["Router", "Switch", "Access Point", "Firewall"],
            "Bağlantı ortamları": ["Ethernet", "Fiber", "Serial", "Wireless"],
            "Servisler": ["DHCP", "DNS", "HTTP", "NTP"]
        }
        for cat, items in categories.items():
            with st.expander(cat, expanded=(cat == "Ağ cihazları")):
                st.write(" · ".join(items))
        with st.form("add_device_form", clear_on_submit=True):
            c1,c2,c3 = st.columns([1,1,1.3])
            with c1: device_name = st.text_input("Cihaz adı", placeholder="Örn. PC-02")
            with c2: device_type = st.selectbox("Kategori / tür", ["PC","Laptop","Server","Printer","IoT","Router","Switch","Access Point","Firewall"])
            with c3: device_ip = st.text_input("IPv4/CIDR (isteğe bağlı)", placeholder="192.168.10.20/24")
            device_gw = st.text_input("Varsayılan ağ geçidi (isteğe bağlı)", placeholder="192.168.10.1")
            if st.form_submit_button("Cihaz ekle"):
                if not device_name.strip(): st.error("Cihaz adı gerekli.")
                elif any(n["name"] == device_name.strip() for n in nodes): st.error("Bu isimde cihaz var.")
                else:
                    nodes.append({"name":device_name.strip(),"type":device_type,"ip":device_ip.strip(),"gateway":device_gw.strip()})
                    st.session_state["lab_nodes"] = nodes
                    st.success("Sanal cihaz eklendi."); st.rerun()
        if nodes:
            st.dataframe(pd.DataFrame(nodes), use_container_width=True, hide_index=True)
            remove_name = st.selectbox("Cihaz kaldır", [n["name"] for n in nodes], key="remove_device")
            if st.button("Seçili cihazı kaldır"):
                st.session_state["lab_nodes"] = [n for n in nodes if n["name"] != remove_name]
                st.session_state["lab_links"] = [(a,b) for a,b in links if a != remove_name and b != remove_name]
                st.rerun()
    with tab_links:
        names = [n["name"] for n in nodes]
        if len(names) >= 2:
            with st.form("add_link_form", clear_on_submit=True):
                a,b = st.columns(2)
                with a: left_node = st.selectbox("Uç A", names)
                with b: right_node = st.selectbox("Uç B", names, index=1 if len(names)>1 else 0)
                medium = st.selectbox("Bağlantı", ["Ethernet", "Fiber", "Serial", "Wireless"])
                if st.form_submit_button("Bağlantı ekle"):
                    if left_node == right_node: st.error("Cihaz kendisine bağlanamaz.")
                    elif any({x,y} == {left_node,right_node} for x,y in links): st.warning("Bu cihazlar zaten bağlı.")
                    else:
                        links.append((left_node,right_node))
                        st.session_state["lab_links"] = links
                        st.session_state.setdefault("lab_link_types", {})[f"{left_node}|{right_node}"] = medium
                        st.success(f"Bağlantı eklendi: {left_node} ↔ {right_node}"); st.rerun()
        else: st.info("Bağlantı kurmak için en az iki cihaz ekle.")
        if links:
            st.dataframe(pd.DataFrame([{"Uç A":a,"Uç B":b,"Ortam":st.session_state.get("lab_link_types",{}).get(f"{a}|{b}","Ethernet")} for a,b in links]), use_container_width=True, hide_index=True)
            remove_link = st.selectbox("Kaldırılacak bağlantı", [f"{a} ↔ {b}" for a,b in links])
            if st.button("Bağlantıyı kaldır"):
                idx = [f"{a} ↔ {b}" for a,b in links].index(remove_link)
                links.pop(idx); st.session_state["lab_links"] = links; st.rerun()
        # Topology view
        if nodes:
            G = nx.Graph()
            for n in nodes: G.add_node(n["name"], kind=n["type"])
            G.add_edges_from(links)
            pos = nx.spring_layout(G, seed=7)
            ex,ey=[],[]
            for u,v in G.edges(): ex += [pos[u][0],pos[v][0],None]; ey += [pos[u][1],pos[v][1],None]
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=ex,y=ey,mode="lines",line=dict(color="#64734a",width=2),hoverinfo="none"))
            fig.add_trace(go.Scatter(x=[pos[n][0] for n in G.nodes()],y=[pos[n][1] for n in G.nodes()],mode="markers+text",
                text=[f"{n}<br>{G.nodes[n]['kind']}" for n in G.nodes()],textposition="bottom center",
                marker=dict(size=24,color="#c2d879",line=dict(color="#11130f",width=2)),hovertext=[G.nodes[n]["kind"] for n in G.nodes()],hoverinfo="text+name"))
            fig.update_layout(paper_bgcolor="#11130f",plot_bgcolor="#11130f",font=dict(color="#d5dfc3",family="IBM Plex Mono"),height=430,margin=dict(l=10,r=10,t=10,b=10),xaxis=dict(visible=False),yaxis=dict(visible=False),showlegend=False)
            st.plotly_chart(fig,use_container_width=True)
    with tab_cli:
        st.markdown("#### Eğitim konsolu")
        st.caption("Komutlar yalnızca bu sanal topoloji üzerinde çalışır.")
        device_for_cli = st.selectbox("Aktif cihaz", [n["name"] for n in nodes] or ["(cihaz yok)"], key="cli_device")
        command = st.selectbox("Komut", ["show devices", "show ip interface brief", "show running-config", "show topology", "ping <IP> (simülasyon)"])
        ping_target = st.text_input("Ping hedef IPv4/CIDR", key="sim_ping_target", placeholder="192.168.10.10/24") if command == "ping <IP> (simülasyon)" else ""
        if st.button("Komutu çalıştır", disabled=not nodes):
            selected_node = next(n for n in nodes if n["name"] == device_for_cli)
            if command == "show devices": output = "\n".join(f"{n['name']:<14} {n['type']:<14} {n['ip'] or 'IP atanmadı'}" for n in nodes)
            elif command == "show ip interface brief": output = f"Device: {selected_node['name']}\nType: {selected_node['type']}\nIP/CIDR: {selected_node['ip'] or 'unassigned'}\nGateway: {selected_node['gateway'] or 'unassigned'}"
            elif command == "show running-config": output = f"hostname {selected_node['name']}\n! type {selected_node['type']}\n! ip address {selected_node['ip'] or 'not-set'}\n! default-gateway {selected_node['gateway'] or 'not-set'}\n! simulated configuration only"
            elif command == "show topology": output = "\n".join([f"{a} <--> {b}" for a,b in links]) or "Bağlantı yok."
            else:
                try:
                    target = str(parse_ip(ping_target).ip)
                    matches = [n for n in nodes if n["ip"] and str(parse_ip(n["ip"]).ip) == target]
                    source_component = G if 'G' in locals() else nx.Graph()
                    for n in nodes: source_component.add_node(n["name"])
                    source_component.add_edges_from(links)
                    reachable = False
                    if matches:
                        target_name = matches[0]["name"]
                        reachable = nx.has_path(source_component, device_for_cli, target_name)
                    output = f"SIMULATED ping {target}\n" + ("Success: hedef topolojide bağlantılı görünüyor.\nNot: Gerçek ICMP paketi gönderilmedi." if reachable else "Unreachable / hedef bulunamadı.\nNot: Bu yalnızca basit topoloji simülasyonudur.")
                except Exception:
                    output = "Hedef IPv4/CIDR geçerli değil. Örnek: 192.168.10.10/24"
            st.code(output, language="text")
    with tab_checks:
        st.markdown("#### Yapılandırma kontrolleri")
        issues = []
        seen_ips = {}
        for n in nodes:
            if n["ip"]:
                try:
                    parsed = parse_ip(n["ip"])
                    ip = str(parsed.ip)
                    if ip in seen_ips: issues.append(f"IP çakışması: {ip} ({seen_ips[ip]} ve {n['name']})")
                    seen_ips[ip] = n["name"]
                except Exception: issues.append(f"{n['name']}: geçersiz IP/CIDR: {n['ip']}")
        for n in nodes:
            if n["type"] in ("PC","Laptop","Server","Printer") and n["ip"] and n["gateway"]:
                try:
                    nic = parse_ip(n["ip"])
                    import ipaddress
                    gw = ipaddress.ip_address(n["gateway"])
                    if gw not in nic.network: issues.append(f"{n['name']}: ağ geçidi {gw}, {nic.network} ağı dışında.")
                except Exception: issues.append(f"{n['name']}: ağ geçidi biçimi kontrol edilmeli.")
        disconnected = [n["name"] for n in nodes if n["name"] not in {x for edge in links for x in edge} and len(nodes)>1]
        if disconnected: issues.append("Bağlantısız cihazlar: " + ", ".join(disconnected))
        if issues:
            for issue in issues: st.warning(issue)
        else: st.success("Basit IP ve bağlantı kontrollerinde sorun bulunmadı.")
        st.download_button("Topolojiyi JSON olarak dışa aktar", data=json.dumps({"devices":nodes,"links":[{"from":a,"to":b} for a,b in links]},ensure_ascii=False,indent=2), file_name="tracevault-topology.json", mime="application/json")
        uploaded_topology = st.file_uploader("Önceden dışa aktarılan topolojiyi içe aktar", type=["json"], key="topology_import")
        if uploaded_topology and st.button("Topolojiyi yükle"):
            try:
                payload = json.loads(uploaded_topology.getvalue().decode("utf-8"))
                new_nodes = payload["devices"]
                new_links = [(item["from"],item["to"]) for item in payload["links"]]
                valid_names = {n["name"] for n in new_nodes}
                if any(a not in valid_names or b not in valid_names for a,b in new_links): raise ValueError("Bağlantı bilinmeyen cihaza işaret ediyor.")
                st.session_state["lab_nodes"] = new_nodes; st.session_state["lab_links"] = new_links
                st.success("Topoloji yüklendi."); st.rerun()
            except Exception as exc: st.error(f"Topoloji yüklenemedi: {exc}")

elif page == "Ayarlar":
    st.subheader("Ayarlar / Sistem bilgisi")
    st.write(f"**Proje klasörü:** `{APP_DIR}`")
    st.write(f"**Veritabanı:** `{APP_DIR / 'data' / 'tracevault.db'}`")
    st.write(f"**Kanıt klasörü:** `{EVIDENCE_DIR}`")
    st.info("Notlar, vakalar ve kanıt kayıtları yerel diskte tutulur. data/ klasörünü herkese açık GitHub deposuna yükleme.")
    st.markdown("#### Güvenlik ve kapsam")
    st.markdown("- Wi-Fi Radarı, NetworkManager üzerinden görünen ağ listesini okur.\n- Ağ Laboratuvarı sanaldır; gerçek ağlara trafik göndermez.\n- Kanıt SHA-256 eşleşmesi yalnızca dosyanın kaydedildiği hash ile aynı olduğunu gösterir.\n- Yedekleme için Bilgi Kasası JSON dışa aktarımını ve vaka raporlarını kullan.")
