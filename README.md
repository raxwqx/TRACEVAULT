# TRACEVAULT v0.2.0 — Retro Research Desk

Türkçe, yerel çalışan araştırma masası: Obsidian'dan ilham alan Markdown bilgi kasası, notlar arası `[[wikilink]]`, not grafiği, vaka/kanıt yönetimi, Wi-Fi gözlem ekranı ve Cisco Packet Tracer'dan ilham alan eğitim amaçlı ağ topolojisi simülatörü.

## Özellikler

- **Bilgi Kasası:** notlar, klasörler, etiketler, arama, Markdown önizleme, `[[Not Başlığı]]` bağlantıları ve JSON dışa aktarma.
- **Graf Bağlantıları:** notlar arası bağlantıların görsel grafiği.
- **Vaka / Kanıt / OSINT:** kaynaklar, bulgular, zaman çizelgesi, dosya kaydı, SHA-256 kontrolü ve Markdown/JSON raporları.
- **Wi-Fi Radarı:** Kali Linux'ta NetworkManager `nmcli` ile yakındaki SSID, BSSID, kanal, frekans, güvenlik ve sinyal seviyesini gösterir. Yerel, salt gözlem amaçlıdır.
- **Ağ Laboratuvarı:** PC, laptop, server, router, switch, access point ve firewall ekleme; sanal bağlantılar; IP/CIDR ve gateway kontrolleri; eğitim konsolu; topoloji JSON içe/dışa aktarma.
- **Retro terminal teması:** yerel ve koyu, eski okul araştırma konsolu görünümü.

## Kurulum (Kali Linux)

```bash
sudo apt update
sudo apt install -y python3-venv python3-pip network-manager
cd ~/İndirilenler/TRACEVAULT
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
PYTHONPATH=. python -m pytest -q
streamlit run app.py
```

Tarayıcıda `http://127.0.0.1:8501` açılır.

## Wi-Fi Radar notları

- Wi-Fi adaptörü, sürücü ve NetworkManager açık olmalıdır.
- `nmcli device status` ve `nmcli dev wifi list` ile kontrol edebilirsin.
- Bu bölüm yalnızca yerel ağ tarama listesini gösterir. Ağlara bağlanma, parola deneme, paket yakalama veya bağlantıyı kesme özelliği içermez.

## Ağ Laboratuvarı sınırları

Bu, Packet Tracer'ın birebir kopyası değildir. Gerçek cihaz işletim sistemi, gerçek paket aktarımı veya Cisco IOS emülasyonu sağlamaz. Konsol komutları ve ping yalnızca uygulama içindeki sanal topoloji üzerinde çalışır.

## Veri güvenliği

Tüm uygulama verileri `data/` altında yerel olarak tutulur. Bu klasör kanıtlar ve veritabanı içerebilir; herkese açık GitHub deposuna yükleme. SHA-256 eşleşmesi tek başına dosyanın kaynağını veya adli/hukuki geçerliliğini kanıtlamaz.

## Testler

```bash
PYTHONPATH=. python -m pytest -q
```

Lisans: MIT.
