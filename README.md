<h1 align="center">🌐 NetVizör</h1>

<p align="center">
  <b>Gerçek Zamanlı Ağ Trafiği İzleme ve Güvenlik Uyarı (IDS) Sistemi</b><br>
  <i>Real-time Network Traffic Monitoring and IDS Dashboard</i>
</p>

<p align="center">
  Linux • Windows • Android (Termux)
</p>

---

NetVizör, bilgisayarınızda veya cihazınızda çalışan uygulamaların ağ kullanımlarını, canlı bağlantıları ve olası güvenlik tehditlerini modern, şık ve koyu temalı bir web arayüzü üzerinden izlemenizi sağlayan bir araçtır.

## 🚀 Hızlı Kurulum (Linux & Termux)

Terminalinize tek bir satır kopyalayarak uygulamayı global ve otomatik olarak kurabilirsiniz:

```bash
curl -sSL "https://raw.githubusercontent.com/ApoBen/netvizor/main/install.sh?$(date +%s)" | bash
```

Kurulum tamamlandıktan sonra terminalinize sadece şunu yazarak arayüzü başlatabilirsiniz:
```bash
netvizor
```

---

## 💻 Platformlara Göre Çalıştırma Kılavuzu

### 🐧 1. Linux (Ubuntu, Debian, Arch vb.)
Linux üzerinde tüm özellikleri tam kapasiteyle kullanmak için:
* **Temel Mod (Root gerekmez)**:
  ```bash
  netvizor
  ```
* **Gelişmiş Mod (IDS & Paket Analizi - Root gerekir)**:
  ```bash
  sudo netvizor
  ```
  *Uygulama arka planda uvicorn sunucusunu başlatacak ve tarayıcınızda otomatik olarak `http://localhost:8765` adresini açacaktır.*

### 🤖 2. Android
*(Geliştirme Aşamasında / Coming Soon)*
Android platformu için tamamen yerel (Native) bir mobil uygulama geliştirme çalışmaları devam etmektedir. Şu an için mobil arayüz planlamadadır.

### 🪟 3. Windows
Windows ortamında tek komutla kurmak için PowerShell penceresine şu komutu kopyalayın:

```powershell
iwr -useb https://raw.githubusercontent.com/ApoBen/netvizor/main/install.ps1 | iex
```

Kurulum bittikten sonra herhangi bir komut satırından arayüzü başlatabilirsiniz:
```cmd
netvizor
```
*Not: Windows üzerinde Gelişmiş Paket Analizi modunu kullanabilmek için bilgisayarınızda **Npcap** (veya WinPcap) kurulu olmalıdır.*

---

## 🛡️ Güvenlik Özellikleri (Mini-IDS)
Uygulama arka planda olası tehditleri izler ve arayüzde bildirimler (Toasts) ile uyarır:
- 🚨 **Port Taraması Algılama (Port Scan):** Bir IP adresi çok kısa sürede birçok portunuza bağlanmaya çalışırsa uyarır *(Root gerektirir)*.
- 🚨 **Şüpheli Port Bağlantıları:** Metasploit (4444), IRC Botnet (6667) vb. arka kapı portlarına giden veya gelen bağlantıları anında tespit eder.
- ⚠️ **Ani Veri Sızdırma / Spike Algılama:** Bir uygulamanın ağ kullanım hızı ortalamasının %500 üstüne çıkarsa uyarır. (İstenmeyen uyarıları "Beyaz Liste"ye ekleyebilirsiniz).

## 📊 Öne Çıkan Özellikler
- **Gerçek Zamanlı Arayüz:** Sayfa yenilemeye gerek kalmadan tüm istatistikler ve grafikler akıcı bir şekilde güncellenir.
- **Süreç Bazlı Ağ Kullanımı:** Chrome, Discord, Spotify gibi uygulamaların anlık ne kadar veri tükettiğini ve toplam ne kadar veri aktardığını logolarıyla birlikte görün.
- **Kayıt ve Duraklatma:** İstediğiniz an veri akışını dondurup geçmişi `.json` formatında kaydedebilirsiniz.
- **Çoklu Dil (i18n):** Türkçe ve İngilizce desteği tek tık uzağınızda.

---

## 💻 Çalışma Modları

- **Temel Mod:** Root yetkisi gerektirmez. Uygulamaların bant genişliğini, süreç istatistiklerini ve aktif bağlantılarını güvenli bir şekilde görüntüler. Termux üzerinde en stabil çalışan moddur.
- **Gelişmiş Mod (`sudo` / Admin):** `scapy` motorunu çalıştırır. Her bir paketin protokolünü analiz eder (TCP/UDP/ICMP), DNS sorgularını izler ve tam kapsamlı port taraması tespitleri yapar.

---
*Geliştirici Notu: Android cihazlarda (Termux) donanım/kernel limitleri nedeniyle root olmadan süreç bazlı detaylar veya paket günlüğü kısıtlanabilir. Uygulama çökmez, bunun yerine Graceful Degradation ile mevcut temel verileri göstermeye devam eder.*
