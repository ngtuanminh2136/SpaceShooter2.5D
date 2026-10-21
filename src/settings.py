import pygame

# 1. Kích thước màn hình mới: 1024x512
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 512
FPS = 60

# 2. Bảng màu chuẩn Sci-Fi
WHITE       = (255, 255, 255)
BLACK       = (0, 0, 0)
RED         = (255, 60, 60)
GREEN       = (50, 255, 120)
YELLOW      = (255, 220, 0)
GRAY        = (160, 170, 190)
CYAN        = (0, 230, 255)
ORANGE      = (255, 140, 0)
PURPLE      = (200, 50, 255)
DARK_BG     = (10, 14, 26)
PANEL_BG    = (18, 24, 42)

# 3. Chỉ số Người chơi
PLAYER_SPEED = 500
PLAYER_HP = 200

# 4. CẤU HÌNH ĐỘ KHÓ 4 MÀN CHƠI (STAGE CONFIGS)
STAGE_CONFIGS = {
    1: {
        "name": "EASY",
        "tagline": "CASUAL FLIGHT",
        "color": GREEN,
        "spawn_delay": 3.0,          # Quái ra chậm
        "enemies_per_wave": 3,       # 3 con / đợt
        "enemy_hp": 10,              # Quái yếu
        "enemy_speed": 110,          # Tốc độ chậm
        "boss_hp": 250,              # Máu Boss
        "boss_spawn_score": 500      # 500 điểm Boss xuất hiện
    },
    2: {
        "name": "MEDIUM",
        "tagline": "STANDARD PATROL",
        "color": YELLOW,
        "spawn_delay": 2.8,          # Quái ra vừa
        "enemies_per_wave": 5,       # 5 con / đợt
        "enemy_hp": 25,              # Quái trâu hơn
        "enemy_speed": 160,          # Nhanh hơn
        "boss_hp": 500,              # Boss trâu
        "boss_spawn_score": 1000     # 1000 điểm Boss xuất hiện
    },
    3: {
        "name": "HARD",
        "tagline": "VETERAN ZONE",
        "color": ORANGE,
        "spawn_delay": 1.5,          # Quái ra dồn dập
        "enemies_per_wave": 7,       # 7 con / đợt
        "enemy_hp": 40,              # Quái rất trâu
        "enemy_speed": 210,          # Tốc độ cao
        "boss_hp": 900,              # Boss siêu trâu
        "boss_spawn_score": 1500     # 1500 điểm Boss xuất hiện
    },
    4: {
        "name": "ASIAN",             # ĐỘ KHÓ BÁ ĐẠO!
        "tagline": "ULTIMATE HELL",
        "color": RED,
        "spawn_delay": 1.0,          # Quái tràn màn hình
        "enemies_per_wave": 10,      # 10 con / đợt
        "enemy_hp": 65,              # Quái trâu điên
        "enemy_speed": 270,          # Di chuyển như chớp
        "boss_hp": 1600,             # Boss siêu khủng
        "boss_spawn_score": 2000     # 2000 điểm Boss xuất hiện
    }
}