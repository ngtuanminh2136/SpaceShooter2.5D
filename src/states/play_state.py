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
                        # CHỈNH SỬA TẠI ĐÂY: Giảm rung khi đạn bắn chết Boss
                        self.trigger_shake(duration=0.4, intensity=5)
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
                # CHỈNH SỬA TẠI ĐÂY: Giảm rung khi người chơi đâm trúng Boss chết
                self.trigger_shake(duration=0.4, intensity=5)
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

    def draw_text_with_shadow(self, surface, text, font, color, pos):
        shadow = font.render(text, True, BLACK)
        surface.blit(shadow, (pos[0] + 2, pos[1] + 2))
        text_surf = font.render(text, True, color)
        surface.blit(text_surf, pos)

    def draw_hud(self, screen):
        s = self.get_scale_factor()
        w, h = self.game.current_width, self.game.current_height

        font_hud = self.get_font(13 * s, bold=False)
        font_value = self.get_font(18 * s, bold=True)
        font_detail = self.get_font(11 * s, bold=False)

        panel_w = int(240 * s)
        panel_h = int(120 * s)
        hud_bg = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
        hud_bg.fill((0, 5, 15, 120))
        screen.blit(hud_bg, (0, 0))

        pad = int(20 * s)
        c_len = int(12 * s)
        pygame.draw.line(screen, CYAN, (pad, pad), (pad + c_len, pad), 2)
        pygame.draw.line(screen, CYAN, (pad, pad), (pad, pad + c_len), 2)
        
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

        prog_w = int(200 * s)
        prog_h = int(2 * s)
        prog_x = pad + int(10 * s)
        prog_y = start_y + line_space * 3 + int(10 * s)
        
        target_score = self.stage_config["boss_spawn_score"]
        ratio = min(1.0, self.score / target_score) if target_score > 0 else 1.0
        
        pygame.draw.rect(screen, (50, 60, 80), (prog_x, prog_y, prog_w, prog_h))
        pygame.draw.rect(screen, CYAN, (prog_x, prog_y, prog_w * ratio, prog_h))
        self.draw_text_with_shadow(screen, f"BOSS PROTOCOL: {int(ratio*100)}%", font_detail, (150, 180, 200), (prog_x, prog_y + int(5 * s)))

        if self.boss and self.boss.alive():
            boss_hp_ratio = self.boss.hp / self.boss.max_hp
            bar_w = int(min(400 * s, w * 0.5))
            bar_h = int(6 * s)
            bar_x = (w - bar_w) // 2
            bar_y = int(40 * s)

            warning_alpha = abs(int(math.sin(self.time_elapsed * 8) * 255))
            lbl_color = (255, max(50, 200 - warning_alpha), max(50, 200 - warning_alpha)) 
            warn_text = f"WARNING: ANOMALY DETECTED [{self.stage_config['name']}]"
            
            warn_surf = font_hud.render(warn_text, True, lbl_color)
            warn_rect = warn_surf.get_rect(center=(w // 2, bar_y - int(15 * s)))
            
            for dx, dy in [(-1,-1), (-1,1), (1,-1), (1,1), (0,2)]:
                shadow = font_hud.render(warn_text, True, BLACK)
                screen.blit(shadow, (warn_rect.x + dx, warn_rect.y + dy))
            screen.blit(warn_surf, warn_rect)

            pygame.draw.rect(screen, (80, 10, 10), (bar_x, bar_y, bar_w, bar_h))
            pygame.draw.rect(screen, (255, 50, 50), (bar_x, bar_y, bar_w * boss_hp_ratio, bar_h))
            pygame.draw.line(screen, WHITE, (bar_x, bar_y - int(4 * s)), (bar_x, bar_y + bar_h + int(4 * s)), 2)
            pygame.draw.line(screen, WHITE, (bar_x + bar_w, bar_y - int(4 * s)), (bar_x + bar_w, bar_y + bar_h + int(4 * s)), 2)

    # --- MÀN HÌNH THẮNG (Đã bỏ chữ SYS, giữ UI chuẩn) ---
    def draw_victory_screen(self, screen):
        s = self.get_scale_factor()
        w, h = self.game.current_width, self.game.current_height
        
        title_font = self.get_font(48 * s, bold=True)
        stats_font = self.get_font(24 * s, bold=False)
        btn_font = self.get_font(20 * s, bold=True)

        overlay = pygame.Surface((w, h), pygame.SRCALPHA)
        overlay.fill((10, 15, 25, 200))
        screen.blit(overlay, (0, 0))

        # Đổi thành STAGE CLEARED
        title_text = f"STAGE {self.stage_id} CLEARED"
        title_surf = title_font.render(title_text, True, CYAN)
        title_rect = title_surf.get_rect(center=(w // 2, h // 2 - int(120 * s)))
        screen.blit(title_surf, title_rect)

        panel_width, panel_height = int(580 * s), int(80 * s)
        panel_x = (w - panel_width) // 2
        panel_y = h // 2 - int(40 * s)
        
        pygame.draw.rect(screen, (20, 25, 40), (panel_x, panel_y, panel_width, panel_height), border_radius=int(10*s))
        pygame.draw.rect(screen, (0, 150, 150), (panel_x, panel_y, panel_width, panel_height), max(1, int(2*s)), border_radius=int(10*s))

        pilot_surf = stats_font.render(f"PILOT: {self.player_name}", True, (200, 200, 200))
        score_surf = stats_font.render(f"SCORE: {self.score}", True, (255, 215, 0))
        kills_surf = stats_font.render(f"KILLS: {self.total_kills}", True, (255, 100, 100))

        screen.blit(pilot_surf, (panel_x + int(30 * s), panel_y + int(25 * s)))
        screen.blit(score_surf, (panel_x + int(250 * s), panel_y + int(25 * s)))
        screen.blit(kills_surf, (panel_x + int(440 * s), panel_y + int(25 * s)))

        if self.stage_id < 4:
            controls = [
                ("N", "NEXT STAGE", (0, 255, 100)),
                ("R", "REPLAY", (200, 200, 200)),
                ("M", "MENU", (200, 200, 200)),
                ("Q", "QUIT", (255, 80, 80))
            ]
        else:
            controls = [
                ("R", "REPLAY", (200, 200, 200)),
                ("M", "MENU", (200, 200, 200)),
                ("Q", "QUIT", (255, 80, 80))
            ]
        
        total_btns = len(controls)
        spacing = int(180 * s)
        start_x = (w - (spacing * (total_btns - 1))) // 2 - int(45 * s)
        btn_y = h // 2 + int(90 * s)

        for i, (key, label, color) in enumerate(controls):
            x_pos = start_x + (i * spacing)
            
            key_surf = btn_font.render(f"[{key}]", True, WHITE)
            key_rect = key_surf.get_rect(topleft=(x_pos, btn_y))
            
            bg_rect = key_rect.inflate(int(16*s), int(10*s))
            pygame.draw.rect(screen, (50, 55, 70), bg_rect, border_radius=int(5*s))
            screen.blit(key_surf, key_rect)

            label_surf = btn_font.render(label, True, color)
            screen.blit(label_surf, (bg_rect.right + int(10*s), btn_y))

    # --- MÀN HÌNH PAUSE (Đã bỏ chữ SYSTEM, nâng cấp UI giống Win) ---
    def draw_pause_screen(self, screen):
        s = self.get_scale_factor()
        w, h = self.game.current_width, self.game.current_height
        
        title_font = self.get_font(48 * s, bold=True)
        btn_font = self.get_font(20 * s, bold=True)

        overlay = pygame.Surface((w, h), pygame.SRCALPHA)
        overlay.fill((0, 5, 15, 180))
        screen.blit(overlay, (0, 0))

        # Đổi thành PAUSED
        title = title_font.render("PAUSED", True, WHITE)
        screen.blit(title, title.get_rect(center=(w // 2, h // 2 - int(50 * s))))

        controls = [
            ("ESC", "RESUME", (0, 255, 100)),
            ("M", "MENU", (200, 200, 200)),
            ("Q", "QUIT", (255, 80, 80))
        ]
        
        total_btns = len(controls)
        spacing = int(180 * s)
        start_x = (w - (spacing * (total_btns - 1))) // 2 - int(45 * s)
        btn_y = h // 2 + int(40 * s)

        for i, (key, label, color) in enumerate(controls):
            x_pos = start_x + (i * spacing)
            
            key_surf = btn_font.render(f"[{key}]", True, WHITE)
            key_rect = key_surf.get_rect(topleft=(x_pos, btn_y))
            
            bg_rect = key_rect.inflate(int(16*s), int(10*s))
            pygame.draw.rect(screen, (50, 55, 70), bg_rect, border_radius=int(5*s))
            screen.blit(key_surf, key_rect)

            label_surf = btn_font.render(label, True, color)
            screen.blit(label_surf, (bg_rect.right + int(10*s), btn_y))

    # --- MÀN HÌNH THUA (Nâng cấp giao diện Panel giống màn hình Thắng) ---
    def draw_game_over(self, screen):
        s = self.get_scale_factor()
        w, h = self.game.current_width, self.game.current_height
        
        title_font = self.get_font(48 * s, bold=True)
        stats_font = self.get_font(24 * s, bold=False)
        btn_font = self.get_font(20 * s, bold=True)

        overlay = pygame.Surface((w, h), pygame.SRCALPHA)
        overlay.fill((25, 5, 5, 200)) # Ám đỏ
        screen.blit(overlay, (0, 0))

        alpha = max(100, abs(int(math.sin(self.time_elapsed * 5) * 255)))
        title_surf = title_font.render("CRITICAL FAILURE", True, (255, 100, 100))
        title_surf.set_alpha(alpha)
        title_rect = title_surf.get_rect(center=(w // 2, h // 2 - int(120 * s)))
        screen.blit(title_surf, title_rect)

        # Khung viền đỏ cho Game Over
        panel_width, panel_height = int(580 * s), int(80 * s)
        panel_x = (w - panel_width) // 2
        panel_y = h // 2 - int(40 * s)
        
        pygame.draw.rect(screen, (40, 20, 20), (panel_x, panel_y, panel_width, panel_height), border_radius=int(10*s))
        pygame.draw.rect(screen, (150, 50, 50), (panel_x, panel_y, panel_width, panel_height), max(1, int(2*s)), border_radius=int(10*s))

        pilot_surf = stats_font.render(f"PILOT: {self.player_name}", True, (200, 200, 200))
        score_surf = stats_font.render(f"SCORE: {self.score}", True, (255, 215, 0))
        stage_surf = stats_font.render(f"STAGE: {self.stage_id}", True, (255, 100, 100))

        screen.blit(pilot_surf, (panel_x + int(30 * s), panel_y + int(25 * s)))
        screen.blit(score_surf, (panel_x + int(250 * s), panel_y + int(25 * s)))
        screen.blit(stage_surf, (panel_x + int(440 * s), panel_y + int(25 * s)))

        controls = [
            ("R", "RESTART", (0, 255, 100)),
            ("M", "MENU", (200, 200, 200)),
            ("Q", "QUIT", (255, 80, 80))
        ]
        
        total_btns = len(controls)
        spacing = int(180 * s)
        start_x = (w - (spacing * (total_btns - 1))) // 2 - int(45 * s)
        btn_y = h // 2 + int(90 * s)

        for i, (key, label, color) in enumerate(controls):
            x_pos = start_x + (i * spacing)
            
            key_surf = btn_font.render(f"[{key}]", True, WHITE)
            key_rect = key_surf.get_rect(topleft=(x_pos, btn_y))
            
            bg_rect = key_rect.inflate(int(16*s), int(10*s))
            pygame.draw.rect(screen, (50, 55, 70), bg_rect, border_radius=int(5*s))
            screen.blit(key_surf, key_rect)

            label_surf = btn_font.render(label, True, color)
            screen.blit(label_surf, (bg_rect.right + int(10*s), btn_y))

    def draw(self, screen):
        render_surface = screen
        offset_x, offset_y = 0, 0
        if self.shake_duration > 0:
            offset_x = random.randint(-self.shake_intensity, self.shake_intensity)
            offset_y = random.randint(-self.shake_intensity, self.shake_intensity)
            render_surface = pygame.Surface((self.game.current_width, self.game.current_height))

        self.background.draw(render_surface)
        
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