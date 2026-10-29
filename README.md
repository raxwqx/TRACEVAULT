<div align="center">

<pre>
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║                  ✦  TRACEVAULT RESEARCH FLEET  ✦                 ║
║                                                                  ║
║                         |\                      _                ║
║                        /| \                    /|                ║
║                       /_|__\                  /_|                ║
║                         |                     / |                ║
║                    _____|____________________/__|____            ║
║                   \_________________________________/            ║
║                    ~~~~~~ ~~~~~ ~~~~~ ~~~~~ ~~~~~~~              ║
║                                                                  ║
║             LOCAL-FIRST RESEARCH DESK · OSINT · FORENSICS        ║
╚══════════════════════════════════════════════════════════════════╝
</pre>

# TRACEVAULT

### YOUR RESEARCH. YOUR RECORDS. YOUR LOCAL VAULT.
### ARAŞTIRMAN. KAYITLARIN. KENDİ BİLGİ KASAN.

[![Python](https://img.shields.io/badge/Python-3.11%2B-c2d879?style=for-the-badge&logo=python&logoColor=11130f)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-Local%20App-9bb86a?style=for-the-badge&logo=streamlit&logoColor=11130f)](https://streamlit.io/)
[![Linux](https://img.shields.io/badge/Linux-Kali%20%7C%20Debian-242820?style=for-the-badge&logo=linux&logoColor=d9e6b9)](https://www.kali.org/)
[![License](https://img.shields.io/badge/License-MIT-c2d879?style=for-the-badge)](LICENSE)

**EN** · A local-first workspace for research notes, case records, evidence metadata, source tracking, Wi-Fi observations, and virtual network-topology learning.

**TR** · Araştırma notları, vaka kayıtları, kanıt metaverileri, kaynak takibi, Wi-Fi gözlemleri ve sanal ağ topolojisi çalışmaları için yerel çalışan bir çalışma alanı.

[English](#-english) · [Türkçe](#-türkçe) · [Quick Start](#-quick-start--hızlı-başlangıç) · [Privacy & Safety](#-privacy-safety--güvenlik)

</div>

---

## At a glance / Bir bakışta

| | English | Türkçe |
|---|---|---|
| **Purpose / Amaç** | A structured personal research desk | Düzenli bir kişisel araştırma masası |
| **Interface / Arayüz** | Dark, retro terminal-inspired UI | Koyu, retro terminal esintili arayüz |
| **Storage / Depolama** | Local SQLite and local files | Yerel SQLite veritabanı ve dosyalar |
| **Notes / Notlar** | Markdown-style notes and `[[wikilinks]]` | Markdown tarzı notlar ve `[[not bağlantıları]]` |
| **Evidence / Kanıt** | File records and SHA-256 checks | Dosya kayıtları ve SHA-256 kontrolleri |
| **Network Lab / Ağ Laboratuvarı** | Virtual topology for learning | Öğrenme amaçlı sanal topoloji |

## Interface preview / Arayüz önizlemesi

The interface uses a focused, dark research-console look with muted green accents and a navigation sidebar. The following is a **text illustration**, not a screenshot from the running application.

Arayüz, yumuşak yeşil vurgulara ve sol gezinme menüsüne sahip koyu bir araştırma konsolu görünümündedir. Aşağıdaki görsel **metinsel bir çizimdir**; çalışan uygulamadan alınmış ekran görüntüsü değildir.

```text
┌────────────────────────────────────────────────────────────────────────┐
│  TRACEVAULT // FIELD DESK                           LOCAL-FIRST / TR   │
├───────────────────┬────────────────────────────────────────────────────┤
│  NAVIGATION       │  TRACEVAULT                                         │
│                   │  [ READY ] Research · Notes · Cases · Evidence       │
│  > Desk           │                                                     │
│    Knowledge      │  ┌────────────┐ ┌────────────┐ ┌────────────┐       │
│    Graph          │  │ CASE FILES │ │   NOTES    │ │  EVIDENCE  │       │
│    Case Files     │  └────────────┘ └────────────┘ └────────────┘       │
│    Evidence       │                                                     │
│    Sources        │  QUICK ACCESS                                       │
│    Timeline       │  01 / Knowledge Vault     Markdown · tags · links    │
│    Reports        │  02 / Evidence Vault      File record · SHA-256      │
│    Wi-Fi Radar    │  03 / Network Lab        Virtual devices · links    │
│    Network Lab    │  04 / Reports            Markdown · JSON             │
│                   │                                                     │
│  MODE: LOCAL      │  DATA: STORED ON THIS MACHINE BY DEFAULT             │
└───────────────────┴────────────────────────────────────────────────────┘
```

---

# 🇬🇧 English

## What is TRACEVAULT?

TRACEVAULT is a **local-first research desk** built to help organize research activity in one workspace. It brings together a personal notes vault, note-to-note links, case records, evidence metadata, source and finding logs, event timelines, case-report exports, a local Wi-Fi information view, and a virtual network-topology learning area.

The visual style borrows from classic research terminals: dark panels, restrained green highlights, monospaced labels, and a calm, information-dense layout.

### Feature deck

| Module | Description |
|---|---|
| **Research Desk** | Overview of cases, notes, evidence records, and findings. |
| **Knowledge Vault** | Create, edit, search, tag, and organize notes by folder. Write Markdown and link notes with `[[Exact Note Title]]`. |
| **Knowledge Graph** | Visualize links between notes when a `[[wikilink]]` points to an existing note. |
| **Case Files** | Create case records with a name, description, and status. |
| **Evidence Vault** | Save uploaded files under the local data directory, record metadata, calculate SHA-256, and check a stored file against its recorded digest. |
| **Sources & Findings** | Record research sources and findings associated with a case. |
| **Timeline** | Record and review events by timestamp. |
| **Report Center** | Export case information as Markdown and JSON. |
| **Wi-Fi Radar** | Display nearby Wi-Fi broadcast details reported by NetworkManager's `nmcli`, when the host system supports it. |
| **Network Lab** | Assemble a virtual topology with devices such as PCs, laptops, servers, routers, switches, access points, and firewalls. Add virtual links, review basic IP settings, and import/export topology JSON. |
| **Retro Desk UI** | Dark, terminal-inspired styling with muted green accents. |

## Requirements

- Linux is the documented environment; Kali Linux and Debian-based distributions are suitable starting points.
- Python 3.11 or newer is recommended.
- Git is needed for the clone-based installation method.
- Wi-Fi Radar needs `nmcli`, NetworkManager, and a compatible wireless adapter. Other modules can be used without running Wi-Fi Radar.
- A modern browser to open the local Streamlit interface.

## Quick Start / Hızlı başlangıç

### Option A: Clone the repository

```bash
git clone https://github.com/raxwqx/TRACEVAULT.git
cd TRACEVAULT
```

### Option B: Download a ZIP from GitHub

1. Open the repository: <https://github.com/raxwqx/TRACEVAULT>
2. Select **Code**.
3. Click **Download ZIP**.
4. Extract the archive.
5. Open a terminal in the extracted `TRACEVAULT` directory.

### Install dependencies

On Kali Linux / Debian-based systems, install Python tools and NetworkManager:

```bash
sudo apt update
sudo apt install -y python3 python3-venv python3-pip network-manager
```

Create a virtual environment and install Python dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### Run tests and launch

Run the tests from the repository root:

```bash
PYTHONPATH=. python -m pytest -q
```

Start TRACEVAULT:

```bash
streamlit run app.py
```

Open the address printed in the terminal. The default is usually:

<http://127.0.0.1:8501>

To stop the server, return to the terminal and press `Ctrl+C`. To leave the virtual environment, run `deactivate`.

## Using TRACEVAULT

1. **Open the Research Desk.** Use the sidebar to move between modules.
2. **Build your notes vault.** Create a note, choose a folder, add tags, and write Markdown.
3. **Link related notes.** Type `[[Exact Note Title]]` in a note. For the graph to show the relationship, the target note needs to exist with the matching title.
4. **Create a case.** Add a case record before associating evidence, sources, findings, or events with it.
5. **Record evidence context.** Add files through the Evidence Vault and describe where they came from and why they matter. Preserve important originals separately.
6. **Track sources and findings.** Keep source details and findings linked to the relevant case. Distinguish a source's statement from your own interpretation.
7. **Create a timeline.** Record event times carefully, including timezone context where relevant.
8. **Review local Wi-Fi details.** The Wi-Fi Radar reads what the local wireless stack reports. Results vary with hardware, driver, permissions, and NetworkManager configuration.
9. **Practice network design.** Use the Network Lab to add virtual devices and links, review basic configuration checks, and export/import a topology as JSON.
10. **Export reports.** Use the relevant export controls to save available case data and reports.

## Repository layout

```text
TRACEVAULT/
├── app.py                       # Streamlit interface
├── tracevault/
│   ├── __init__.py
│   ├── core.py                  # Case, evidence, source and report logic
│   └── db.py                    # Local SQLite database setup
├── tests/                       # Automated tests
├── .github/workflows/           # GitHub Actions workflows
├── requirements.txt              # Python dependencies
├── .gitignore                   # Excludes local/sensitive files
└── README.md
```

Runtime files and the SQLite database are stored locally under `data/`.

## Troubleshooting

### `ModuleNotFoundError: No module named 'tracevault'`

Make sure the terminal is in the repository root, activate the virtual environment, and run:

```bash
PYTHONPATH=. python -m pytest -q
```

### `streamlit: command not found`

Activate the virtual environment and install the dependencies again:

```bash
source .venv/bin/activate
python -m pip install -r requirements.txt
```

### Wi-Fi Radar does not list networks

Check that `nmcli` is available and inspect NetworkManager's device list:

```bash
command -v nmcli
nmcli device status
nmcli dev wifi list
```

The feature depends on your wireless hardware, driver, permissions, and local system configuration. It may not work in some virtual machines or on systems without a compatible wireless adapter.

### Port 8501 is busy

Use another port:

```bash
streamlit run app.py --server.port 8502
```

Then open <http://127.0.0.1:8502>.

---

# 🇹🇷 Türkçe

## TRACEVAULT nedir?

TRACEVAULT, araştırma süreçlerini tek bir çalışma alanında düzenlemeye yardımcı olan **yerel çalışan bir araştırma masasıdır**. Kişisel not kasasını, notlar arası bağlantıları, vaka kayıtlarını, kanıt metaverilerini, kaynak ve bulgu takibini, olay zaman çizelgesini, vaka raporu dışa aktarmayı, yerel Wi-Fi bilgi ekranını ve sanal ağ topolojisi laboratuvarını bir araya getirir.

Arayüz dili klasik araştırma terminallerinden ilham alır: koyu paneller, ölçülü yeşil vurgular, monospace etiketler ve bilgi odaklı bir yerleşim.

### Özellik güvertesi

| Modül | Açıklama |
|---|---|
| **Araştırma Masası** | Vaka, not, kanıt kaydı ve bulguların genel özeti. |
| **Bilgi Kasası** | Not oluşturma, düzenleme, arama, etiketleme ve klasörlere ayırma. Markdown yazabilir, `[[Tam Not Başlığı]]` biçimiyle notları bağlayabilirsin. |
| **Bilgi Grafiği** | `[[not bağlantısı]]` mevcut bir nota işaret ettiğinde notlar arasındaki ilişkiyi görselleştirir. |
| **Vaka Dosyaları** | Ad, açıklama ve durum bilgileri içeren vaka kayıtları oluşturur. |
| **Kanıt Kasası** | Yüklenen dosyaları yerel veri klasörüne kaydeder, metaverilerini tutar, SHA-256 özeti hesaplar ve dosyanın kayıtlı özetle eşleşmesini denetler. |
| **Kaynaklar ve Bulgular** | Bir vakayla ilişkili kaynakları ve bulguları kaydeder. |
| **Zaman Çizelgesi** | Olayları zaman damgalarıyla kaydetmeye ve sıralı incelemeye yardımcı olur. |
| **Rapor Merkezi** | Vaka bilgilerini Markdown ve JSON olarak dışa aktarır. |
| **Wi-Fi Radarı** | Sistem desteklediğinde NetworkManager `nmcli` üzerinden bildirilen yakındaki Wi-Fi yayın bilgilerini gösterir. |
| **Ağ Laboratuvarı** | PC, laptop, sunucu, router, switch, access point ve firewall gibi sanal cihazlarla topoloji kurar. Sanal bağlantılar ekleyebilir, temel IP ayarlarını inceleyebilir ve topolojiyi JSON olarak içe/dışa aktarabilirsin. |
| **Retro Arayüz** | Yumuşak yeşil vurgulara sahip koyu, terminal esintili görünüm. |

## Gereksinimler

- Belgelenen ortam Linux'tur; Kali Linux ve Debian tabanlı dağıtımlar iyi bir başlangıçtır.
- Python 3.11 veya üzeri önerilir.
- Git ile klonlama yöntemi için Git gerekir.
- Wi-Fi Radarı için `nmcli`, NetworkManager ve uyumlu kablosuz adaptör gerekir. Wi-Fi Radar kullanılmadan diğer modüller de açılabilir.
- Yerel Streamlit arayüzünü açmak için güncel bir tarayıcı gerekir.

## Kurulum ve hızlı başlangıç

### Seçenek A: Depoyu Git ile klonla

```bash
git clone https://github.com/raxwqx/TRACEVAULT.git
cd TRACEVAULT
```

### Seçenek B: GitHub üzerinden ZIP indir

1. Depoyu aç: <https://github.com/raxwqx/TRACEVAULT>
2. **Code** düğmesine bas.
3. **Download ZIP** seçeneğini seç.
4. ZIP dosyasını çıkart.
5. Çıkarttığın `TRACEVAULT` klasöründe terminal aç.

### Bağımlılıkları kur

Kali Linux / Debian tabanlı sistemlerde Python araçlarını ve NetworkManager'ı yükle:

```bash
sudo apt update
sudo apt install -y python3 python3-venv python3-pip network-manager
```

Sanal ortam oluştur ve Python bağımlılıklarını yükle:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### Testleri çalıştır ve uygulamayı başlat

Komutları depo kök klasöründe çalıştır:

```bash
PYTHONPATH=. python -m pytest -q
```

TRACEVAULT'ı başlat:

```bash
streamlit run app.py
```

Terminalde gösterilen adresi aç. Varsayılan adres genellikle şudur:

<http://127.0.0.1:8501>

Sunucuyu durdurmak için terminale dönüp `Ctrl+C` tuşlarına bas. Sanal ortamdan çıkmak için `deactivate` yaz.

## TRACEVAULT nasıl kullanılır?

1. **Araştırma Masası'nı aç.** Sol menüden bölümler arasında dolaş.
2. **Bilgi kasanı oluştur.** Bir not aç, klasörünü seç, etiket ekle ve Markdown içeriğini yaz.
3. **İlgili notları bağla.** Notun içine `[[Tam Not Başlığı]]` yaz. Grafikte ilişkinin görünmesi için hedef notun aynı başlıkla mevcut olması gerekir.
4. **Vaka oluştur.** Kanıtları, kaynakları, bulguları veya olayları ilişkilendirmeden önce vaka kaydı aç.
5. **Kanıt bağlamını kaydet.** Kanıt Kasası'na dosya eklerken nereden geldiğini ve neden önemli olduğunu açıkla. Önemli materyallerin orijinalini ayrıca koru.
6. **Kaynakları ve bulguları takip et.** Kaynak ayrıntılarını ve bulguları ilgili vakayla ilişkilendir. Kaynağın söylediği şeyle kendi yorumunu birbirinden ayır.
7. **Zaman çizelgesi hazırla.** Olay saatlerini dikkatle gir; gerekiyorsa saat dilimini de belirt.
8. **Yerel Wi-Fi bilgilerini incele.** Wi-Fi Radarı, yerel kablosuz sistemin bildirdiği verileri okur. Sonuçlar donanım, sürücü, izinler ve NetworkManager yapılandırmasına göre değişebilir.
9. **Ağ tasarımını çalış.** Ağ Laboratuvarı'na sanal cihazlar ve bağlantılar ekle, temel yapılandırma kontrollerini incele ve topolojiyi JSON olarak dışa aktar veya içe aktar.
10. **Raporları dışa aktar.** İlgili dışa aktarma kontrolleriyle mevcut vaka bilgilerini ve raporları kaydet.

## Depo klasör yapısı

```text
TRACEVAULT/
├── app.py                       # Streamlit arayüzü
├── tracevault/
│   ├── __init__.py
│   ├── core.py                  # Vaka, kanıt, kaynak ve rapor mantığı
│   └── db.py                    # Yerel SQLite veritabanı kurulumu
├── tests/                       # Otomatik testler
├── .github/workflows/           # GitHub Actions iş akışları
├── requirements.txt              # Python bağımlılıkları
├── .gitignore                   # Yerel/hassas dosyaları dışlar
└── README.md
```

Çalışma sırasında oluşturulan dosyalar ve SQLite veritabanı yerel `data/` klasöründe tutulur.

## Sorun giderme

### `ModuleNotFoundError: No module named 'tracevault'`

Terminalin depo kök klasöründe olduğundan emin ol, sanal ortamı etkinleştir ve komutu çalıştır:

```bash
PYTHONPATH=. python -m pytest -q
```

### `streamlit: command not found`

Sanal ortamı etkinleştir ve bağımlılıkları yeniden yükle:

```bash
source .venv/bin/activate
python -m pip install -r requirements.txt
```

### Wi-Fi Radarı ağları listelemiyor

`nmcli` komutunun bulunduğunu kontrol et ve NetworkManager aygıt listesini incele:

```bash
command -v nmcli
nmcli device status
nmcli dev wifi list
```

Bu özellik kablosuz donanıma, sürücüye, izinlere ve sistem yapılandırmasına bağlıdır. Bazı sanal makinelerde veya uyumlu kablosuz adaptörü olmayan sistemlerde çalışmayabilir.

### 8501 portu kullanımda

Farklı bir port kullan:

```bash
streamlit run app.py --server.port 8502
```

Ardından <http://127.0.0.1:8502> adresini aç.

---

## 🔐 Privacy, Safety & Güvenlik

### English

TRACEVAULT is designed for local-first use, but **local storage is not encryption**. Someone with access to your computer account or files may be able to read data stored on the machine.

- **Keep private records private.** The local `data/` directory may contain a database and uploaded evidence. Do not push real case records, personal data, credentials, or sensitive evidence to a public repository.
- **Review before every push.** Run `git status` and make sure data files, exports, secrets, and virtual environments are not being committed.
- **Preserve originals.** For important forensic material, keep an untouched original and conduct checks on a copy where practical.
- **Understand SHA-256.** A matching digest indicates that a checked file matches the recorded hash. By itself, it does not establish who created the file, where it originated, whether its contents are true, or whether it is legally admissible.
- **Wi-Fi Radar is observational.** It lists broadcast details made visible by the local wireless stack. It is not a password-cracking, packet-interception, disconnection, or unauthorized-access tool.
- **Network Lab is virtual.** It does not run Cisco IOS, emulate physical hardware, or send real network packets through the simulated topology.
- **Get permission.** Use TRACEVAULT for your own records, authorized investigations, learning, and lawful OSINT work.

### Türkçe

TRACEVAULT yerel kullanım için tasarlanmıştır; ancak **yerel depolama şifreleme demek değildir**. Bilgisayar hesabına veya dosyalara erişebilen biri, cihazdaki verileri okuyabilir.

- **Özel kayıtları gizli tut.** Yerel `data/` klasörü veritabanı ve yüklenen kanıtları içerebilir. Gerçek vaka kayıtlarını, kişisel verileri, parolaları veya hassas kanıtları herkese açık depoya gönderme.
- **Her gönderimden önce kontrol et.** `git status` çalıştır; veri dosyalarının, dışa aktarımların, sırların ve sanal ortamların commit edilmediğinden emin ol.
- **Orijinal materyali koru.** Önemli adli materyallerde değişmemiş bir orijinal bulundur ve mümkün olduğunda kontrolleri kopya üzerinde yap.
- **SHA-256'nın sınırlarını bil.** Hash eşleşmesi, kontrol edilen dosyanın kayıtlı özetle aynı olduğunu gösterir. Tek başına dosyayı kimin oluşturduğunu, kaynağını, içeriğinin doğruluğunu veya hukuki geçerliliğini kanıtlamaz.
- **Wi-Fi Radarı gözlem amaçlıdır.** Yerel kablosuz sistemin görünür kıldığı yayın bilgilerini listeler. Parola kırma, paket ele geçirme, bağlantı kesme veya izinsiz erişim aracı değildir.
- **Ağ Laboratuvarı sanaldır.** Cisco IOS çalıştırmaz, fiziksel donanımı emüle etmez ve sanal topoloji üzerinden gerçek ağ paketi göndermez.
- **İzin al.** TRACEVAULT'ı kendi kayıtların, izinli incelemeler, öğrenme ve hukuka uygun OSINT çalışmaları için kullan.

## 🧪 Testing / Testler

Run from the repository root with the dependencies installed:

```bash
PYTHONPATH=. python -m pytest -q
```

Bağımlılıklar kurulu durumdayken depo kökünde aynı komutu çalıştır:

```bash
PYTHONPATH=. python -m pytest -q
```

## 🤝 Contributing / Katkı

Bug reports, documentation improvements, and code contributions are welcome. For code changes, run the tests and describe the purpose of your change clearly in the pull request.

Hata bildirimleri, dokümantasyon iyileştirmeleri ve kod katkıları memnuniyetle karşılanır. Kod değişikliklerinde testleri çalıştır ve pull request içinde değişikliğin amacını açıkça belirt. Hassas vaka verilerini, kişisel bilgileri veya kanıt dosyalarını issue ya da pull request içine ekleme.

## 📜 License / Lisans

TRACEVAULT is distributed under the MIT License. See [`LICENSE`](LICENSE) for the full license text.

TRACEVAULT MIT lisansı altında dağıtılır. Lisans metninin tamamı için [`LICENSE`](LICENSE) dosyasına bak.

---

<div align="center">

<pre>
            /\
           /  \       TRACEVAULT
      ____/____\____________________________
      \____________________________________/
          ~~~~~ ~~~~~ ~~~~~ ~~~~~
       LOCAL-FIRST · RESEARCH · RECORD · REVIEW
</pre>

**Keep your notes connected. Keep your evidence considered.**  
**Notlarını ilişkilendir. Kanıtlarını dikkatle değerlendir.**

</div>
