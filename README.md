# 🐍 Pygame ile Gelişmiş Yılan Oyunu (Data Logger)

<p align="center">
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/Pygame-FF5A5F?style=for-the-badge&logo=pygame&logoColor=white" />
  <img src="https://img.shields.io/badge/Data%20Analysis-Pandas%2FMatplotlib-000000?style=for-the-badge&logo=pandas&logoColor=white" />
</p>

Bu proje, klasik Yılan Oyunu'nun (Snake Game) sadece bir kopyası değil, aynı zamanda **algoritmik verimlilik** ve **veri bilimi** özelliklerini birleştiren gelişmiş bir versiyonudur.

## ✨ Temel Özellikler ve Algoritmik Yapı

- **🎮 Smooth Movement (Pürüzsüz Hareket):** Yılanın hareketleri, geleneksel grid atlamalı hareket yerine, FPS ve piksel tabanlı interpolasyon kullanılarak daha akıcı (smooth) hale getirilmiştir.
- **📊 CSV Veri Kaydı:** Yılanın her yem yiyişi (`EAT`) ve oyunu bitirişi (`CRASH`) olayları, zaman damgası, skor ve uzunluk bilgileriyle birlikte otomatik olarak **`snake_stats.csv`** dosyasına kaydedilir. (Yılan popülasyonu analizi için ideal).
- **🚀 Veri Analizi Betiği:** **`veri_analizi.py`** betiği, Pandas ve Matplotlib kullanarak CSV verilerini okur, oynanan oyun sayısını, ortalama büyüme hızını ve skor trajektorisini görselleştirir.
- **🧩 Gelişmiş Game Loop:** Yüksek skor kaydı, ses efektleri, duraklatma (`P`), yeniden başlatma (`R`) ve duvar modları (Çarpışma/Geçiş) gibi tüm modern özelliklere sahiptir.
- **📈 Hız Dinamiği:** Skor arttıkça yılanın hareket hızı dinamik olarak artar.

## ⚙️ Kurulum ve Çalıştırma

1.  **Gerekli Kütüphaneler:**
    ```bash
    pip install pygame pandas matplotlib
    ```
2.  **Oyun:**
    ```bash
    python yilan_oyunu.py
    ```
3.  **Veri Analizi:** (Oyun oynayıp veri kaydı oluşturduktan sonra)
    ```bash
    python veri_analizi.py
    ```

---

Şimdi depoyu oluştur ve bu metni `README.md` olarak kaydet. Hazır olduğunda bana haber ver, yükleme komutlarını çalıştıralım.
