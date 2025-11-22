import pandas as pd
import matplotlib.pyplot as plt
import os
from datetime import datetime

STATS_FILE = "snake_stats.csv"

def analyze_snake_data():
    if not os.path.exists(STATS_FILE):
        print(f"Hata: '{STATS_FILE}' dosyası bulunamadı. Lütfen oyunu birkaç kez oynayıp veriyi oluşturun.")
        return

    df = pd.read_csv(STATS_FILE)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    # Oyun başına verimliliği hesaplayabilmek için oyunu bitiş anına göre gruplayalım
    crash_data = df[df['event'] == 'CRASH'].copy()
    
    # Yalnızca ilk EAT kaydından son CRASH kaydına kadar olan veriyi alalım
    first_event_time = df['timestamp'].iloc[0]
    last_event_time = df['timestamp'].iloc[-1]
    
    # Geçen toplam süreyi hesapla
    time_elapsed = last_event_time - first_event_time
    total_seconds = time_elapsed.total_seconds()

    # Oynanan toplam oyun sayısı
    total_games = len(crash_data)
    
    # Ortalama ve Maksimum Değerler
    avg_length = crash_data['length'].mean()
    max_score = crash_data['score'].max()
    
    # 🟢 YENİ METRİK HESAPLAMALARI
    total_eats = len(df[df['event'] == 'EAT'])
    
    # Büyüme Hızı: Toplam uzama / Toplam süre
    if total_seconds > 0:
        avg_growth_rate = total_eats / total_seconds # Saniyede kaç yem yenmiş
    else:
        avg_growth_rate = 0

    print("\n--- YILAN POPÜLASYON ANALİZİ ---")
    print(f"Veri Kaydı Süresi: {time_elapsed} saniye")
    print(f"Toplam Yenen Yem Sayısı (EAT event): {total_eats}")
    print("="*30)
    print(f"Toplam Oynanan Oyun Sayısı: {total_games}")
    print(f"En Yüksek Skor: {max_score}")
    print(f"En Uzun Ulaşılan Yılan Boyu: {df['length'].max()}")
    print(f"Ortalama BÜYÜME HIZI (Verimlilik): {avg_growth_rate:.4f} yem/saniye")
    print("="*30)
    
    # 3. Görselleştirme: Büyüme Hızı Grafiği
    plt.figure(figsize=(12, 6))
    
    plt.plot(df['timestamp'], df['length'], 
             marker='o', linestyle='-', color='lime', linewidth=2, markersize=5)
    
    crash_events = df[df['event'] == 'CRASH']
    plt.scatter(crash_events['timestamp'], crash_events['length'], 
                marker='X', color='red', s=100, label='Oyun Sonu (Crash)')
    
    plt.title('Yılanın Büyüme Trajektorisi ve Verimlilik', fontsize=16)
    plt.xlabel('Zaman', fontsize=12)
    plt.ylabel('Yılan Uzunluğu (Hücre)', fontsize=12)
    plt.grid(True, linestyle='--', alpha=0.6)
    
    plt.gcf().autofmt_xdate() 
    plt.legend()
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    analyze_snake_data()