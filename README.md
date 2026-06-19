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

Terminalinize tek bir satır kopyalayarak uygulamayı global olarak kurabilirsiniz:

```bash
curl -sL https://raw.githubusercontent.com/ApoBen/NetViz-r/main/install.sh | bash
```

Kurulum tamamlandıktan sonra, terminalinizin herhangi bir yerinde sadece şu komutu yazarak arayüzü açabilirsiniz:
```bash
netvizor
```

*(Gelişmiş mod özelliklerini kullanmak istiyorsanız `sudo netvizor` yazabilirsiniz)*

## 🪟 Windows Kurulumu

Windows sistemlerde kullanmak için repoyu indirip klasör içindeki başlatıcıyı çalıştırın:
1. Sağ üstten projeyi `.zip` olarak indirin veya `git clone https://github.com/ApoBen/NetViz-r.git` komutunu kullanın.
2. Klasörün içindeki `run.bat` dosyasına çift tıklayın. Otomatik olarak kurulup açılacaktır.
*(Gelişmiş paket analizi için Windows sisteminizde Npcap kurulu olmalıdır.)*

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
