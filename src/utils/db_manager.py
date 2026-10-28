import sqlite3
import os
from datetime import datetime

class DatabaseManager:
    def __init__(self, db_name="game_data.db"):
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        self.db_path = os.path.join(base_dir, db_name)
        self.init_db()

    def get_connection(self):
        return sqlite3.connect(self.db_path)

    def init_db(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Bảng lưu kết quả chơi
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS high_scores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                player_name TEXT DEFAULT 'Pilot',
                score INTEGER NOT NULL,
                level INTEGER NOT NULL,
                kills INTEGER DEFAULT 0,
                created_at TEXT NOT NULL
            )
        ''')
        
        # Bảng lưu thông tin người chơi hiện tại (Player Profile)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS player_profile (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                player_name TEXT NOT NULL,
                last_login TEXT NOT NULL
            )
        ''')

        # Bảng lưu Tiền xu (Coins) và Cấp độ Nâng cấp (Upgrades)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS player_upgrades (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                coins INTEGER DEFAULT 0,
                hp_lvl INTEGER DEFAULT 0,
                damage_lvl INTEGER DEFAULT 0,
                speed_lvl INTEGER DEFAULT 0,
                shield_lvl INTEGER DEFAULT 0
            )
        ''')
        
        conn.commit()
        conn.close()

    def get_active_player(self):
        """Lấy tên người chơi hiện tại/gần nhất"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT player_name FROM player_profile WHERE id = 1')
        row = cursor.fetchone()
        conn.close()
        return row[0] if row else None

    def set_active_player(self, player_name):
        """Lưu hoặc cập nhật người chơi hiện tại"""
        conn = self.get_connection()
        cursor = conn.cursor()
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        cursor.execute('''
            INSERT INTO player_profile (id, player_name, last_login)
            VALUES (1, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                player_name = excluded.player_name,
                last_login = excluded.last_login
        ''', (player_name, now))
        conn.commit()
        conn.close()

    def get_player_upgrades(self):
        """Tải số Coins và các cấp độ nâng cấp từ SQLite"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT coins, hp_lvl, damage_lvl, speed_lvl, shield_lvl FROM player_upgrades WHERE id = 1')
        row = cursor.fetchone()
        conn.close()
        
        if row:
            coins, hp, dmg, spd, shd = row
            return coins, {'hp': hp, 'damage': dmg, 'speed': spd, 'shield': shd}
        else:
            return 0, {'hp': 0, 'damage': 0, 'speed': 0, 'shield': 0}

    def save_player_upgrades(self, coins, upgrades):
        """Lưu hoặc cập nhật Coins và các cấp độ nâng cấp vào SQLite"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO player_upgrades (id, coins, hp_lvl, damage_lvl, speed_lvl, shield_lvl)
            VALUES (1, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                coins = excluded.coins,
                hp_lvl = excluded.hp_lvl,
                damage_lvl = excluded.damage_lvl,
                speed_lvl = excluded.speed_lvl,
                shield_lvl = excluded.shield_lvl
        ''', (coins, upgrades.get('hp', 0), upgrades.get('damage', 0), upgrades.get('speed', 0), upgrades.get('shield', 0)))
        conn.commit()
        conn.close()

    def save_score(self, score, level, kills=0, player_name="Pilot"):
        conn = self.get_connection()
        cursor = conn.cursor()
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        cursor.execute('''
            INSERT INTO high_scores (player_name, score, level, kills, created_at)
            VALUES (?, ?, ?, ?, ?)
        ''', (player_name, score, level, kills, now))
        conn.commit()
        conn.close()

    def get_top_scores(self, limit=5):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT player_name, score, level, kills, created_at 
            FROM high_scores 
            ORDER BY score DESC 
            LIMIT ?
        ''', (limit,))
        rows = cursor.fetchall()
        conn.close()
        return rows

    def get_highest_score(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT MAX(score) FROM high_scores')
        result = cursor.fetchone()[0]
        conn.close()
        return result if result is not None else 0