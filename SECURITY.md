# Security Policy / Güvenlik Politikası

## Supported versions / Desteklenen sürümler

Security fixes are applied to the latest release on the `main` branch.

Güvenlik düzeltmeleri `main` dalındaki en son sürüme uygulanır.

## Reporting a vulnerability / Güvenlik açığı bildirme

Please **do not** open a public issue for a security problem and do not attach
real case data, personal data, credentials, or evidence files.

Güvenlik sorunları için lütfen **herkese açık issue açma**; gerçek vaka
verisi, kişisel veri, parola veya kanıt dosyası ekleme.

Use GitHub private vulnerability reporting:

- <https://github.com/raxwqx/TRACEVAULT/security/advisories/new>

Please include:

- affected version or commit,
- steps to reproduce,
- expected and actual behavior,
- impact assessment,
- a minimal proof of concept without sensitive data.

Lütfen şunları ekle:

- etkilenen sürüm veya commit,
- yeniden üretme adımları,
- beklenen ve gerçek davranış,
- etki değerlendirmesi,
- hassas veri içermeyen en küçük kanıt.

## Scope / Kapsam

TRACEVAULT is a local-first desktop-style application. Relevant reports include
path traversal in evidence handling, unsafe file writes, SQL injection,
cross-site scripting in rendered Markdown, and unintended network activity.

TRACEVAULT yerel çalışan bir masaüstü tarzı uygulamadır. Kanıt işlemede yol
aşımı (path traversal), güvensiz dosya yazımı, SQL enjeksiyonu, işlenen
Markdown içinde XSS ve istenmeyen ağ etkinliği bu kapsamdadır.

The Wi-Fi Radar only reads broadcast information exposed by the local wireless
stack. It is not a password-cracking, packet-capture, or deauthentication tool.
The Network Lab is a simulator and does not send real packets.

Wi-Fi Radarı yalnızca yerel kablosuz sistemin sunduğu yayın bilgilerini okur.
Parola kırma, paket yakalama veya bağlantı kesme aracı değildir. Ağ Laboratuvarı
bir simülatördür ve gerçek paket göndermez.
