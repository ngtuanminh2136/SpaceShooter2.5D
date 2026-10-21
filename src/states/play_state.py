import pygame
import random
import sys
import math
from settings import *
from entities.player import Player
from entities.background import Background
from entities.enemy import Enemy
from entities.boss import Boss
from entities.item import Item
from utils.sound_manager import SoundManager
from utils.db_manager import DatabaseManager

class PlayState:
    def __init__(self, game, stage_id=1):
        self.game = game
        self.stage_id = stage_id
        self.stage_config = STAGE_CONFIGS.get(stage_id, STAGE_CONFIGS[1])
        
        self.background = Background(self.game)
        self.sound_manager = SoundManager()
        self.db = DatabaseManager()
        
        self.font_cache = {}
        
        self.score = 0
        self.total_kills = 0
        self.saved_to_db = False
        self.player_name = self.db.get_active_player() or "PILOT"
        
        self.is_game_over = False
        self.is_victory = False
        self.is_paused = False
        
        self.boss = None
        self.boss_spawned = False
        
        self.shake_duration = 0.0
        self.shake_intensity = 0
        
        self.time_elapsed = 0
        self.reset_game()

    def get_font(self, size, bold=False):
        size = max(11, int(size))
        key = (size, bold)
        if key not in self.font_cache:
            try:
                self.font_cache[key] = pygame.font.SysFont("segoe ui", size, bold=bold)
            except:
                self.font_cache[key] = pygame.font.SysFont("arial", size, bold=bold)
        return self.font_cache[key]
        
    def get_scale_factor(self):
        w, h = self.game.current_width, self.game.current_height
        return max(0.85, min(w / 1024.0, h / 512.0))

    def reset_game(self):
        self.score = 0
        self.total_kills = 0
        self.saved_to_db = False
        self.player_name = self.db.get_active_player() or "PILOT"
        
        self.is_game_over = False
        self.is_victory = False
        self.is_paused = False
        
        self.enemy_spawn_timer = 0.0
        self.boss = None
        self.boss_spawned = False
        self.shake_duration = 0.0
        self.time_elapsed = 0
        
        self.all_sprites = pygame.sprite.Group()
        self.bullets = pygame.sprite.Group()
        self.enemy_bullets = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.items = pygame.sprite.Group()
        
        self.player = Player(self.all_sprites, self.game, [self.all_sprites, self.bullets])

    def trigger_shake(self, duration=0.5, intensity=15):
        self.shake_duration = duration
        self.shake_intensity = intensity

    def handle_events(self, event):
        if event.type == pygame.KEYDOWN:
            if self.is_game_over or self.is_victory:
                if event.key == pygame.K_n and self.is_victory and self.stage_id < 4:
                    self.game.change_state(PlayState(self.game, stage_id=self.stage_id + 1))
                elif event.key == pygame.K_r:
                    self.reset_game()
                elif event.key == pygame.K_m:
                    from states.menu_state import MenuState
                    self.game.change_state(MenuState(self.game))
                elif event.key == pygame.K_q:
                    pygame.quit()
                    sys.exit()
                return

            if event.key in (pygame.K_ESCAPE, pygame.K_SPACE):
                self.is_paused = not self.is_paused

            if self.is_paused:
                if event.key == pygame.K_m:
                    from states.menu_state import MenuState
                    self.game.change_state(MenuState(self.game))
                elif event.key == pygame.K_q:
                    pygame.quit()
                    sys.exit()

    def update(self, dt):
        self.time_elapsed += dt
        
        if self.is_paused:
            return
            
        self.background.update(dt)
        
        if self.shake_duration > 0:
            self.shake_duration -= dt

        if self.is_game_over or self.is_victory:
            if not self.saved_to_db:
                self.db.save_score(self.score, self.stage_id, self.total_kills, player_name=self.player_name)
                self.saved_to_db = True
            return

        self.enemy_spawn_timer -= dt
        if self.enemy_spawn_timer <= 0:
            for _ in range(self.stage_config["enemies_per_wave"]):
                self.spawn_enemy()
            self.enemy_spawn_timer = self.stage_config["spawn_delay"]

        if self.score >= self.stage_config["boss_spawn_score"] and not self.boss_spawned:
            self.spawn_boss()
            self.boss_spawned = True
            
        self.all_sprites.update(dt)
        self.check_collisions()

    def check_collisions(self):
        hits = pygame.sprite.groupcollide(self.enemies, self.bullets, False, True)
        for enemy, bullets_hit in hits.items():
            for bullet in bullets_hit:
                enemy.take_damage(10)
                if enemy.hp <= 0:
                    self.sound_manager.play('explosion')
                    self.total_kills += 1
                    
                    if isinstance(enemy, Boss):
                        self.score += 1000
                        self.boss = None
                        self.trigger_shake(duration=0.6, intensity=18)
                        self.is_victory = True
                    else:
                        self.score += 100
                        if random.random() < 0.25:
                            item_type = random.choice(['heal', 'triple_shot'])
                            Item(enemy.pos.x, enemy.pos.y, item_type, [self.all_sprites, self.items], self.game)

        bullet_hits = pygame.sprite.spritecollide(self.player, self.enemy_bullets, True)
        for bullet in bullet_hits:
            self.player.hp -= 15
            self.sound_manager.play('hit')
            if self.player.hp <= 0:
                self.player.hp = 0
                self.is_game_over = True

        item_hits = pygame.sprite.spritecollide(self.player, self.items, True)
        for item in item_hits:
            self.sound_manager.play('powerup')
            if item.item_type == 'heal':
                self.player.hp = min(self.player.max_hp, self.player.hp + 30)
            elif item.item_type == 'triple_shot':
                self.player.triple_shot_timer = 7.0

        player_hits = pygame.sprite.spritecollide(self.player, self.enemies, True)
        for hit in player_hits:
            self.sound_manager.play('hit')
            if isinstance(hit, Boss):
                self.player.hp -= 50
                self.boss = None
                self.trigger_shake(duration=0.6, intensity=18)
                self.is_victory = True
            else:
                self.player.hp -= 20
                
            if self.player.hp <= 0:
                self.player.hp = 0
                self.is_game_over = True

    def spawn_enemy(self):
        edge = random.choice(['top', 'bottom', 'left', 'right'])
        x, y = 0, 0
        if edge == 'top':
            x, y = random.randint(0, self.game.current_width), -50
        elif edge == 'bottom':
            x, y = random.randint(0, self.game.current_width), self.game.current_height + 50
        elif edge == 'left':
            x, y = -50, random.randint(0, self.game.current_height)
        elif edge == 'right':
            x, y = self.game.current_width + 50, random.randint(0, self.game.current_height)
        
        enemy = Enemy(x, y, [self.all_sprites, self.enemies], self.game, self.player, [self.all_sprites])
        enemy.hp = self.stage_config["enemy_hp"]
        enemy.speed = self.stage_config["enemy_speed"]

    def spawn_boss(self):
        x = self.game.current_width // 2
        y = -100
        self.boss = Boss(x, y, [self.all_sprites, self.enemies], self.game, self.player, 
                         [self.all_sprites, self.enemy_bullets], [self.all_sprites])
        self.boss.max_hp = self.stage_config["boss_hp"]
        self.boss.hp = self.boss.max_hp

    # --- HÀM VẼ TEXT CÓ ĐỔ BÓNG GIÚP CHỮ NỔI BẬT ---
    def draw_text_with_shadow(self, surface, text, font, color, pos):
        # Đổ bóng đen lệch xuống dưới phải 2px
        shadow = font.render(text, True, BLACK)
        surface.blit(shadow, (pos[0] + 2, pos[1] + 2))
        
        # Chữ thật
        text_surf = font.render(text, True, color)
        surface.blit(text_surf, pos)

    def draw_hud(self, screen):
        s = self.get_scale_factor()
        w, h = self.game.current_width, self.game.current_height

        font_hud = self.get_font(13 * s, bold=False)
        font_value = self.get_font(18 * s, bold=True)
        font_detail = self.get_font(11 * s, bold=False)

        # --- LỚP NỀN MỜ CHO HUD TRÁI (GIÚP CHỮ KHÔNG BỊ CHÌM VÀO SAO) ---
        panel_w = int(240 * s)
        panel_h = int(120 * s)
        hud_bg = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
        hud_bg.fill((0, 5, 15, 120)) # Nền đen hơi xanh mờ (120/255)
        screen.blit(hud_bg, (0, 0))

        pad = int(20 * s)
        
        c_len = int(12 * s)
        pygame.draw.line(screen, CYAN, (pad, pad), (pad + c_len, pad), 2)
        pygame.draw.line(screen, CYAN, (pad, pad), (pad, pad + c_len), 2)
        
        # Thay màu Label sáng hơn chút
        label_color = (180, 190, 200)
        
        self.draw_text_with_shadow(screen, "TACTICAL DATA", font_detail, (150, 200, 255), (pad + int(8 * s), pad + int(4 * s)))

        stg_color = self.stage_config["color"]
        col1_x = pad + int(10 * s)
        col2_x = pad + int(85 * s)
        start_y = pad + int(20 * s)
        line_space = int(22 * s)

        self.draw_text_with_shadow(screen, "SYS.STAGE //", font_hud, label_color, (col1_x, start_y))
        self.draw_text_with_shadow(screen, f"{self.stage_id} [{self.stage_config['name']}]", font_value, stg_color, (col2_x, start_y - int(3 * s)))

        self.draw_text_with_shadow(screen, "SCORE //", font_hud, label_color, (col1_x, start_y + line_space))
        self.draw_text_with_shadow(screen, str(self.score), font_value, CYAN, (col2_x, start_y + line_space - int(3 * s)))

        self.draw_text_with_shadow(screen, "KILLS //", font_hud, label_color, (col1_x, start_y + line_space * 2))
        self.draw_text_with_shadow(screen, str(self.total_kills), font_value, WHITE, (col2_x, start_y + line_space * 2 - int(3 * s)))

        # Thanh tiến trình gọi Boss
        prog_w = int(200 * s)
        prog_h = int(2 * s)
        prog_x = pad + int(10 * s)
        prog_y = start_y + line_space * 3 + int(10 * s)
        
        target_score = self.stage_config["boss_spawn_score"]
        ratio = min(1.0, self.score / target_score) if target_score > 0 else 1.0
        
        pygame.draw.rect(screen, (50, 60, 80), (prog_x, prog_y, prog_w, prog_h))
        pygame.draw.rect(screen, CYAN, (prog_x, prog_y, prog_w * ratio, prog_h))
        
        self.draw_text_with_shadow(screen, f"BOSS PROTOCOL: {int(ratio*100)}%", font_detail, (150, 180, 200), (prog_x, prog_y + int(5 * s)))


        # --- THANH MÁU BOSS ---
        if self.boss and self.boss.alive():
            boss_hp_ratio = self.boss.hp / self.boss.max_hp
            bar_w = int(min(400 * s, w * 0.5))
            bar_h = int(6 * s)
            bar_x = (w - bar_w) // 2
            bar_y = int(40 * s)

            # Cảnh báo: Đổi sang màu Đỏ Sáng (Bright Red) và thêm đổ bóng đen dày
            warning_alpha = abs(int(math.sin(self.time_elapsed * 8) * 255))
            # Màu text: Đỏ sáng
            lbl_color = (255, max(50, 200 - warning_alpha), max(50, 200 - warning_alpha)) 
            warn_text = f"WARNING: ANOMALY DETECTED [{self.stage_config['name']}]"
            
            # Vẽ viền bóng đen xung quanh để không bị chìm
            warn_surf = font_hud.render(warn_text, True, lbl_color)
            warn_rect = warn_surf.get_rect(center=(w // 2, bar_y - int(15 * s)))
            
            # Tự đổ bóng bằng vòng lặp nhỏ
            for dx, dy in [(-1,-1), (-1,1), (1,-1), (1,1), (0,2)]:
                shadow = font_hud.render(warn_text, True, BLACK)
                screen.blit(shadow, (warn_rect.x + dx, warn_rect.y + dy))
            
            screen.blit(warn_surf, warn_rect)

            pygame.draw.rect(screen, (80, 10, 10), (bar_x, bar_y, bar_w, bar_h))
            pygame.draw.rect(screen, (255, 50, 50), (bar_x, bar_y, bar_w * boss_hp_ratio, bar_h))
            pygame.draw.line(screen, WHITE, (bar_x, bar_y - int(4 * s)), (bar_x, bar_y + bar_h + int(4 * s)), 2)
            pygame.draw.line(screen, WHITE, (bar_x + bar_w, bar_y - int(4 * s)), (bar_x + bar_w, bar_y + bar_h + int(4 * s)), 2)

    def draw_victory_screen(self, screen):
        s = self.get_scale_factor()
        w, h = self.game.current_width, self.game.current_height
        
        font_large = self.get_font(40 * s, bold=True)
        font_med = self.get_font(20 * s, bold=False)

        overlay = pygame.Surface((w, h), pygame.SRCALPHA)
        overlay.fill((10, 30, 10, 220))
        screen.blit(overlay, (0, 0))

        title = font_large.render(f"SYS.OVERRIDE: STAGE {self.stage_id} CLEARED", True, CYAN)
        screen.blit(title, title.get_rect(center=(w // 2, h // 2 - int(50 * s))))

        stats = font_med.render(f"PILOT: {self.player_name} // SCORE: {self.score} // KILLS: {self.total_kills}", True, WHITE)
        screen.blit(stats, stats.get_rect(center=(w // 2, h // 2 + int(10 * s))))

        if self.stage_id < 4:
            hint = "[N] NEXT STAGE   [R] REPLAY   [M] MENU   [Q] QUIT"
        else:
            hint = "LEGENDARY PILOT!   [R] REPLAY   [M] MENU   [Q] QUIT"
        
        hint_surf = font_med.render(hint, True, (150, 200, 150))
        screen.blit(hint_surf, hint_surf.get_rect(center=(w // 2, h // 2 + int(50 * s))))

    def draw_pause_screen(self, screen):
        s = self.get_scale_factor()
        w, h = self.game.current_width, self.game.current_height
        
        font_large = self.get_font(40 * s, bold=True)
        font_med = self.get_font(18 * s, bold=False)

        overlay = pygame.Surface((w, h), pygame.SRCALPHA)
        overlay.fill((0, 5, 15, 180))
        screen.blit(overlay, (0, 0))

        title = font_large.render("SYSTEM PAUSED", True, WHITE)
        screen.blit(title, title.get_rect(center=(w // 2, h // 2 - int(30 * s))))

        hint = font_med.render("[ESC/SPACE] RESUME   [M] MENU   [Q] QUIT", True, CYAN)
        screen.blit(hint, hint.get_rect(center=(w // 2, h // 2 + int(20 * s))))

    def draw_game_over(self, screen):
        s = self.get_scale_factor()
        w, h = self.game.current_width, self.game.current_height
        
        font_large = self.get_font(44 * s, bold=True)
        font_med = self.get_font(20 * s, bold=False)

        overlay = pygame.Surface((w, h), pygame.SRCALPHA)
        overlay.fill((25, 5, 5, 200))
        screen.blit(overlay, (0, 0))

        alpha = max(100, abs(int(math.sin(self.time_elapsed * 5) * 255)))
        title = font_large.render("CRITICAL FAILURE", True, (255, 100, 100))
        title.set_alpha(alpha)
        screen.blit(title, title.get_rect(center=(w // 2, h // 2 - int(60 * s))))

        stats = font_med.render(f"PILOT: {self.player_name} // STAGE: {self.stage_id} // SCORE: {self.score}", True, WHITE)
        screen.blit(stats, stats.get_rect(center=(w // 2, h // 2)))

        hint = font_med.render("[R] RESTART   [M] MAIN MENU   [Q] QUIT", True, (150, 150, 150))
        screen.blit(hint, hint.get_rect(center=(w // 2, h // 2 + int(45 * s))))

    def draw(self, screen):
        render_surface = screen
        offset_x, offset_y = 0, 0
        if self.shake_duration > 0:
            offset_x = random.randint(-self.shake_intensity, self.shake_intensity)
            offset_y = random.randint(-self.shake_intensity, self.shake_intensity)
            render_surface = pygame.Surface((self.game.current_width, self.game.current_height))

        self.background.draw(render_surface)
        
        # --- THAY THẾ cho self.all_sprites.draw() để kích hoạt hiệu ứng vệt lửa của Player ---
        for sprite in self.all_sprites:
            if hasattr(sprite, 'draw'):
                sprite.draw(render_surface)
            else:
                render_surface.blit(sprite.image, sprite.rect)
        
        if not self.is_game_over and not self.is_victory:
            self.player.draw_health(render_surface)
        
        self.draw_hud(render_surface)

        if self.is_paused:
            self.draw_pause_screen(render_surface)
        elif self.is_victory:
            self.draw_victory_screen(render_surface)
        elif self.is_game_over:
            self.draw_game_over(render_surface)

        if self.shake_duration > 0:
            screen.blit(render_surface, (offset_x, offset_y))