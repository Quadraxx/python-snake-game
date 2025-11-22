import pygame
import random
import os
import sys
import csv
from datetime import datetime

# --- AYARLAR ---
SCREEN_W, SCREEN_H = 600, 420
CELL = 20
GRID_W = SCREEN_W // CELL
GRID_H = SCREEN_H // CELL

# 🟢 Hız ayarı (Kullanıcı İsteği: 4)
BASE_SPEED = 4 
SPEED_INCREMENT_AT_SCORE = 40 
MAX_SPEED = 18

FPS = 30 # Frame hızı (Pürüzsüz hareket için)

# RENKLER
WHITE = (255, 255, 255)
GREEN = (2, 120, 2)
HEAD_GREEN = (40, 240, 40) 
RED = (255, 60, 60)
BLACK = (0, 0, 0)
GRAY = (150, 150, 150)
YELLOW = (255, 255, 100)
SHADOW_COLOR = (1, 50, 1)

# DOSYA SABİTLERİ
HS_FILE = "highscore.txt"
# 🟢 YENİ: İstatistik kayıt dosyası
STATS_FILE = "snake_stats.csv" 

pygame.init()
pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
pygame.display.set_caption("Yılan Oyunu - Hüseyin Akın (Gelişmiş)")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Consolas", 20)
big_font = pygame.font.SysFont("Consolas", 44)
score_font = pygame.font.SysFont("Consolas", 24)

# Sesleri yükle
sound_enabled = True
eat_sound = None
crash_sound = None

def load_sounds():
    global eat_sound, crash_sound, sound_enabled
    try:
        eat_sound = pygame.mixer.Sound("eat.wav")
    except Exception:
        eat_sound = None
    try:
        crash_sound = pygame.mixer.Sound("crash.wav")
    except Exception:
        crash_sound = None

load_sounds()

# --- YARDIMCI FONKSİYONLAR ---

def read_highscore():
    try:
        with open(HS_FILE, "r") as f:
            return int(f.read().strip() or 0)
    except Exception:
        return 0

def write_highscore(v):
    try:
        with open(HS_FILE, "w") as f:
            f.write(str(int(v)))
    except Exception:
        pass

# 🟢 YENİ: İstatistik Kaydetme Fonksiyonu
def log_stats(skor, uzunluk, olay_turu):
    """Mevcut skor, yılan uzunluğu ve zamanı CSV dosyasına kaydeder."""
    file_exists = os.path.isfile(STATS_FILE)
    
    with open(STATS_FILE, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        
        if not file_exists:
            writer.writerow(['timestamp', 'score', 'length', 'event'])
            
        writer.writerow([
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            skor,
            uzunluk,
            olay_turu
        ])

# Menü ekranı
def menu_screen(sound_on, wall_mode):
    selection = 0
    options = ["Başlat", f"Ses: {'Açık' if sound_on else 'Kapalı'}", f"Duvarlar: {'Aktif' if wall_mode else 'Geçiş'}", "Çıkış"]
    while True:
        screen.fill(BLACK)
        title = big_font.render("YILAN OYUNU", True, YELLOW)
        screen.blit(title, (SCREEN_W//2 - title.get_width()//2, 40))
        for i, opt in enumerate(options):
            color = WHITE if i == selection else GRAY
            t = font.render(opt, True, color)
            screen.blit(t, (SCREEN_W//2 - t.get_width()//2, 150 + i*40))
        hint = font.render("W/S veya ↑/↓ ile seç - Enter ile onayla - S: ses toggle (kısayol)", True, GRAY)
        screen.blit(hint, (SCREEN_W//2 - hint.get_width()//2, SCREEN_H - 40))
        pygame.display.flip()

        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if ev.type == pygame.KEYDOWN:
                if ev.key in (pygame.K_w, pygame.K_UP):
                    selection = (selection - 1) % len(options)
                elif ev.key in (pygame.K_s, pygame.K_DOWN):
                    selection = (selection + 1) % len(options)
                elif ev.key == pygame.K_RETURN:
                    return selection, sound_on, wall_mode
                elif ev.key == pygame.K_s:
                    sound_on = not sound_on
                    options[1] = f"Ses: {'Açık' if sound_on else 'Kapalı'}"
                elif ev.key == pygame.K_ESCAPE:
                    pygame.quit(); sys.exit()

# grid -> pixel center
def cell_to_pixel(cell):
    x, y = cell
    return x * CELL, y * CELL

# Yeni yem oluştur
def spawn_food(govde):
    attempts = 0
    while True:
        attempts += 1
        fx = random.randrange(0, GRID_W)
        fy = random.randrange(0, GRID_H)
        if [fx, fy] not in govde:
            return [fx, fy]
        if attempts > 1000:
            for i in range(GRID_W):
                for j in range(GRID_H):
                    if [i,j] not in govde:
                        return [i,j]

# Oyun döngüsü
def game_loop(sound_on=True, wall_mode=True):
    global eat_sound, crash_sound

    # Başlangıç değişkenleri
    start_x = GRID_W // 2
    start_y = GRID_H // 2
    govde = [[start_x, start_y], [start_x-1, start_y], [start_x-2, start_y]]
    direction = "SAG" 

    head_cell = list(govde[0])
    head_px_x, head_px_y = cell_to_pixel(head_cell)
    head_px_x = float(head_px_x)
    head_px_y = float(head_px_y)

    target_cell = list(govde[0])
    food = spawn_food(govde)
    score = 0
    highscore = read_highscore()
    speed = BASE_SPEED
    paused = False
    requested_dir = direction
    running = True
    died = False

    while running:
        clock.tick(FPS) 
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT: return False, score
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_ESCAPE: return False, score
                if ev.key == pygame.K_p: paused = not paused
                if ev.key == pygame.K_r: return True, score
                if ev.key == pygame.K_s: sound_on = not sound_on
                
                # Yön kontrolü
                if ev.key in (pygame.K_UP, pygame.K_w) and direction != "ASAGI": requested_dir = "YUKARI"
                if ev.key in (pygame.K_DOWN, pygame.K_s) and direction != "YUKARI": requested_dir = "ASAGI"
                if ev.key in (pygame.K_LEFT, pygame.K_a) and direction != "SAG": requested_dir = "SOL"
                if ev.key in (pygame.K_RIGHT, pygame.K_d) and direction != "SOL": requested_dir = "SAG"

        if paused:
            # Pause ekranı çizimi
            screen.fill(BLACK)
            paused_t = big_font.render("PAUSE", True, WHITE)
            screen.blit(paused_t, (SCREEN_W//2 - paused_t.get_width()//2, 120))
            s = font.render("P: Devam - R: Yeniden - S: Ses - ESC: Çık", True, GRAY)
            screen.blit(s, (SCREEN_W//2 - s.get_width()//2, 200))
            pygame.display.flip()
            continue

        # Hücreye ulaşma kontrolü
        target_px = cell_to_pixel(target_cell)
        arrived = (abs(head_px_x - target_px[0]) < speed and abs(head_px_y - target_px[1]) < speed)

        if arrived:
            # Pikselleri tam hücre merkezine eşitle
            head_px_x, head_px_y = float(target_cell[0]*CELL), float(target_cell[1]*CELL)
            
            direction = requested_dir

            # Bir sonraki hedef hücreyi hesapla
            next_cell = list(target_cell)
            if direction == "SAG": next_cell[0] += 1
            elif direction == "SOL": next_cell[0] -= 1
            elif direction == "YUKARI": next_cell[1] -= 1
            elif direction == "ASAGI": next_cell[1] += 1

            # Duvar modu ve çarpma kontrolü
            if not wall_mode: next_cell[0] %= GRID_W; next_cell[1] %= GRID_H # Wrap-around
            else:
                if next_cell[0] < 0 or next_cell[0] >= GRID_W or next_cell[1] < 0 or next_cell[1] >= GRID_H: died = True
            
            if next_cell in govde: died = True # Kendine çarpma kontrolü

            if died:
                log_stats(score, len(govde), 'CRASH') # 🟢 ÖLÜM KAYDI
                if sound_on and crash_sound:
                    try: crash_sound.play()
                    except Exception: pass
                if score > highscore: write_highscore(score)
                return True, score

            # Yeni baş hücresini gövdeye insert et
            govde.insert(0, list(next_cell))
            target_cell = list(next_cell)
            head_cell = list(next_cell)
            
            # Yem yeme kontrolü
            if next_cell == food:
                score += 10
                log_stats(score, len(govde), 'EAT') # 🟢 YEM YEME KAYDI
                if sound_on and eat_sound:
                    try: eat_sound.play()
                    except Exception: pass
                food = spawn_food(govde)
                speed = min(BASE_SPEED + score // SPEED_INCREMENT_AT_SCORE, MAX_SPEED)
            else:
                govde.pop() # Kuyruk çıkar (boy sabit kalır)

        else:
            # Hedefe doğru yumuşak ilerle (Pürüzsüz hareket)
            target_px_x, target_px_y = target_cell[0]*CELL, target_cell[1]*CELL
            
            # İlerleme
            if direction == "SAG": head_px_x += speed
            elif direction == "SOL": head_px_x -= speed
            elif direction == "YUKARI": head_px_y -= speed
            elif direction == "ASAGI": head_px_y += speed
            
            # Hedefi aşmamak için kısıtla
            if direction == "SAG" and head_px_x > target_px_x: head_px_x = target_px_x
            if direction == "SOL" and head_px_x < target_px_x: head_px_x = target_px_x
            if direction == "YUKARI" and head_px_y < target_px_y: head_px_y = target_px_y
            if direction == "ASAGI" and head_px_y > target_px_y: head_px_y = target_px_y

        # --- EKRAN ÇİZİMİ ---
        screen.fill(BLACK)

        # Grid çizgileri
        for gx in range(0, SCREEN_W, CELL):
            pygame.draw.line(screen, (15,15,15), (gx,0), (gx, SCREEN_H))
        for gy in range(0, SCREEN_H, CELL):
            pygame.draw.line(screen, (15,15,15), (0,gy), (SCREEN_W, gy))

        # Yem çizimi
        food_px = cell_to_pixel(food)
        pygame.draw.circle(screen, RED, (food_px[0] + CELL//2, food_px[1] + CELL//2), CELL//2 - 2)
        pygame.draw.circle(screen, YELLOW, (food_px[0] + CELL//2 - 3, food_px[1] + CELL//2 - 3), 3)

        # Gövde çizimi (Pürüzsüz kafa çizimi dahil)
        for i, c in enumerate(govde):
            
            if i == 0:
                # Kafa (Piksel tabanlı çizim)
                head_rect = pygame.Rect(head_px_x + 1, head_px_y + 1, CELL - 2, CELL - 2)
                pygame.draw.rect(screen, HEAD_GREEN, head_rect, 0, 3) 
                
                # Gözler
                eye_size = 3
                eye_offset_x = 4
                eye_offset_y = 6
                # Yöne göre göz pozisyonu hesaplama
                if direction == "SAG": eye1 = (head_px_x + CELL - eye_offset_x, head_px_y + eye_offset_y); eye2 = (head_px_x + CELL - eye_offset_x, head_px_y + CELL - eye_offset_y)
                elif direction == "SOL": eye1 = (head_px_x + eye_offset_x, head_px_y + eye_offset_y); eye2 = (head_px_x + eye_offset_x, head_px_y + CELL - eye_offset_y)
                elif direction == "YUKARI": eye1 = (head_px_x + eye_offset_y, head_px_y + eye_offset_x); eye2 = (head_px_x + CELL - eye_offset_y, head_px_y + eye_offset_x)
                else: eye1 = (head_px_x + eye_offset_y, head_px_y + CELL - eye_offset_x); eye2 = (head_px_x + CELL - eye_offset_y, head_px_y + CELL - eye_offset_x)

                pygame.draw.circle(screen, BLACK, eye1, eye_size)
                pygame.draw.circle(screen, BLACK, eye2, eye_size)
                
            else:
                # Gövde (Grid tabanlı çizim)
                px = c[0]*CELL
                py = c[1]*CELL
                rect = pygame.Rect(px + 1, py + 1, CELL - 2, CELL - 2)
                shadow_rect = pygame.Rect(px + 2, py + 2, CELL - 2, CELL - 2)
                pygame.draw.rect(screen, SHADOW_COLOR, shadow_rect, 0, 3)
                pygame.draw.rect(screen, GREEN, rect, 0, 3) 
                
        # --- HUD: Skor, Yüksek Skor ve Hız ---
        hs = read_highscore()
        hud_score = score_font.render(f"SKOR: {score}", True, YELLOW)
        hud_hs = score_font.render(f"YÜKSEK SKOR: {hs}", True, WHITE)
        hud_speed = score_font.render(f"HIZ: {speed}", True, WHITE)
        
        screen.blit(hud_score, (10, 5))
        screen.blit(hud_hs, (150, 5))
        screen.blit(hud_speed, (380, 5))
        
        # Kontrol ipuçları
        tips = font.render("P: Pause  R: Yeniden  S: Ses Aç/Kapat  ESC: Çık", True, GRAY)
        screen.blit(tips, (10, SCREEN_H - 22))

        pygame.display.flip()

    return False, score

# Ana program akışı
def main():
    global sound_enabled
    sound_on = True if (eat_sound is not None or crash_sound is not None) else False
    wall_mode = True

    while True:
        sel, sound_on, wall_mode = menu_screen(sound_on, wall_mode)
        if sel == 0:
            sound_enabled = sound_on
            restart_flag, final_score = game_loop(sound_on, wall_mode)
            
            hs = read_highscore()
            if final_score > hs:
                write_highscore(final_score)
                hs = final_score
                
            if restart_flag:
                while True:
                    screen.fill(BLACK)
                    t1 = big_font.render("OYUN BİTTİ!", True, RED)
                    screen.blit(t1, (SCREEN_W//2 - t1.get_width()//2, 90))
                    t2 = font.render(f"Skor: {final_score}      En Yüksek: {hs}", True, WHITE)
                    screen.blit(t2, (SCREEN_W//2 - t2.get_width()//2, 170))
                    t3 = font.render("R: Yeniden Başlat   M: Menüye Dön   ESC: Çık", True, GRAY)
                    screen.blit(t3, (SCREEN_W//2 - t3.get_width()//2, 230))
                    pygame.display.flip()
                    ev = pygame.event.wait()
                    if ev.type == pygame.QUIT: pygame.quit(); sys.exit()
                    if ev.type == pygame.KEYDOWN:
                        if ev.key == pygame.K_r: break
                        if ev.key == pygame.K_m: break
                        if ev.key == pygame.K_ESCAPE: pygame.quit(); sys.exit()
                continue
            else:
                continue
        elif sel == 3:
            pygame.quit()
            sys.exit()

if __name__ == "__main__":
    if not (os.path.exists("eat.wav") and os.path.exists("crash.wav")):
        print("Not: eat.wav veya crash.wav bulunamadı. Ses kapalı ya da dosyayı aynı klasöre koyabilirsiniz.")
    main()