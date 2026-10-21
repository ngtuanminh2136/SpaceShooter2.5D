import pygame
import sys
import math
import os
from settings import *
from utils.db_manager import DatabaseManager
from utils.sound_manager import SoundManager

class MenuState:
    def __init__(self, game):
        self.game = game
        self.db = DatabaseManager()
        self.active_player = self.db.get_active_player() or "PILOT"

        # Khởi tạo quản lý âm thanh và phát nhạc nền lặp vô hạn ở Menu
        self.sound_manager = SoundManager()
        self.sound_manager.play_music('forest_2.ogg', volume=0.3)
        
        self.font_cache = {}
        
        self.options = ["PLAY", "SANDBOX (STAGE)", "COLLECTION (PILOT)", "LEADERBOARD", "QUIT"]
        self.selected_index = 0
        self.selected_stage = 1
        self.option_rects = []
        
        self.show_leaderboard = False
        self.show_stage_select = False
        
        self.time_elapsed = 0

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

    def handle_events(self, event):
        s = self.get_scale_factor()
        w, h = self.game.current_width, self.game.current_height

        # Xử lý khi đang mở bảng Leaderboard
        if self.show_leaderboard:
            if event.type == pygame.MOUSEBUTTONDOWN or (event.type == pygame.KEYDOWN and event.key not in {pygame.K_PRINTSCREEN, pygame.K_PRINT, pygame.K_SYSREQ}):
                self.show_leaderboard = False
            return

        # Xử lý khi đang mở bảng chọn Stage
        if self.show_stage_select:
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_LEFT, pygame.K_a):
                    self.selected_stage = 4 if self.selected_stage == 1 else self.selected_stage - 1
                elif event.key in (pygame.K_RIGHT, pygame.K_d):
                    self.selected_stage = 1 if self.selected_stage == 4 else self.selected_stage + 1
                elif event.key == pygame.K_RETURN:
                    self.show_stage_select = False
                elif event.key == pygame.K_ESCAPE:
                    self.show_stage_select = False
            elif event.type == pygame.MOUSEMOTION:
                mouse_pos = event.pos
                card_w = int(min(210 * s, (w - 80 * s) / 4))
                card_h = int(min(330 * s, h * 0.68))
                spacing = int(18 * s)
                start_x = (w - (card_w * 4 + spacing * 3)) // 2
                card_y = int(h * 0.16)
                
                for stg in range(1, 5):
                    cx = start_x + (stg - 1) * (card_w + spacing)
                    rect = pygame.Rect(cx, card_y, card_w, card_h)
                    if rect.collidepoint(mouse_pos):
                        self.selected_stage = stg
                        break
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    mouse_pos = event.pos
                    card_w = int(min(210 * s, (w - 80 * s) / 4))
                    card_h = int(min(330 * s, h * 0.68))
                    spacing = int(18 * s)
                    start_x = (w - (card_w * 4 + spacing * 3)) // 2
                    card_y = int(h * 0.16)
                    
                    for stg in range(1, 5):
                        cx = start_x + (stg - 1) * (card_w + spacing)
                        rect = pygame.Rect(cx, card_y, card_w, card_h)
                        if rect.collidepoint(mouse_pos):
                            self.selected_stage = stg
                            self.show_stage_select = False
                            break
            return

        # Xử lý menu chính
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_UP, pygame.K_w):
                self.selected_index = (self.selected_index - 1) % len(self.options)
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                self.selected_index = (self.selected_index + 1) % len(self.options)
            elif event.key == pygame.K_RETURN:
                self.select_option()
            elif event.key == pygame.K_q:
                pygame.quit()
                sys.exit()
                
        elif event.type == pygame.MOUSEMOTION:
            mouse_pos = event.pos
            for i, rect in enumerate(self.option_rects):
                if rect.collidepoint(mouse_pos):
                    self.selected_index = i

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                mouse_pos = event.pos
                for i, rect in enumerate(self.option_rects):
                    if rect.collidepoint(mouse_pos):
                        self.selected_index = i
                        self.select_option()

    def select_option(self):
        if self.selected_index == 0:
            from states.play_state import PlayState
            self.game.change_state(PlayState(self.game, stage_id=self.selected_stage))
        elif self.selected_index == 1:
            self.show_stage_select = True
        elif self.selected_index == 2:
            from states.name_input_state import NameInputState
            self.game.change_state(NameInputState(self.game))
        elif self.selected_index == 3:
            self.show_leaderboard = True
        elif self.selected_index == 4:
            pygame.quit()
            sys.exit()

    def update(self, dt):
        self.time_elapsed += dt

    def draw_cinematic_background(self, screen, w, h):
        actual_w, actual_h = screen.get_size()
        current_dir = os.path.dirname(os.path.abspath(__file__))
        bg_path = os.path.join(current_dir, "..", "..", "assets", "menu.jpg")
        
        if os.path.exists(bg_path):
            try:
                img = pygame.image.load(bg_path).convert()
                bg_scaled = pygame.transform.scale(img, (actual_w, actual_h))
                screen.blit(bg_scaled, (0, 0))
            except Exception:
                screen.fill((5, 10, 20))
        else:
            screen.fill((5, 10, 20))

        uniform_overlay = pygame.Surface((actual_w, actual_h), pygame.SRCALPHA)
        uniform_overlay.fill((5, 10, 25, 70)) 
        screen.blit(uniform_overlay, (0, 0))

    def draw(self, screen):
        s = self.get_scale_factor()
        w, h = self.game.current_width, self.game.current_height

        self.draw_cinematic_background(screen, w, h)

        font_logo = self.get_font(48 * s, bold=True)
        font_logo_sub = self.get_font(16 * s, bold=True)
        font_menu = self.get_font(22 * s, bold=True) 
        font_hint = self.get_font(14 * s, bold=True) 

        left_margin = int(w * 0.12) 

        logo_text = "S P A C E   S H O O T E R"
        logo_surf = font_logo.render(logo_text, True, WHITE)
        screen.blit(logo_surf, (left_margin, int(h * 0.15)))

        line_y = int(h * 0.15) + logo_surf.get_height() + int(10 * s)
        pygame.draw.line(screen, CYAN, (left_margin, line_y), (left_margin + int(250 * s), line_y), 2)

        sub_logo_text = "V O I D   P R O T O C O L"
        sub_logo = font_logo_sub.render(sub_logo_text, True, CYAN)
        screen.blit(sub_logo, (left_margin, line_y + int(8 * s)))

        self.option_rects = []
        start_y = int(h * 0.38)
        spacing = int(45 * s)

        for i, option in enumerate(self.options):
            y_pos = start_y + i * spacing
            is_selected = (i == self.selected_index)
            text_color = CYAN if is_selected else (240, 245, 255)
            
            option_surf = font_menu.render(option, True, text_color)
            hit_rect = pygame.Rect(left_margin - int(40 * s), y_pos - int(10 * s), int(350 * s), int(40 * s))
            self.option_rects.append(hit_rect)

            if is_selected:
                offset = int(math.sin(self.time_elapsed * 6) * 5)
                cursor_x = left_margin - int(25 * s) + offset
                
                pygame.draw.polygon(screen, CYAN, [
                    (cursor_x, y_pos + int(8 * s)),
                    (cursor_x, y_pos + int(18 * s)),
                    (cursor_x + int(8 * s), y_pos + int(13 * s))
                ])
                pygame.draw.line(screen, (50, 180, 230), (cursor_x + int(12 * s), y_pos + int(13 * s)), (left_margin - int(5 * s), y_pos + int(13 * s)), 2)
            
            screen.blit(option_surf, (left_margin, y_pos))

        hint_str = "[W/S] NAVIGATE   [ENTER] SELECT   [Q] QUIT"
        hint_surf = font_hint.render(hint_str, True, (200, 220, 240)) 
        screen.blit(hint_surf, (left_margin, h - int(40 * s)))

        right_margin = w - int(w * 0.05)
        panel_w = int(220 * s)
        panel_h = int(65 * s)
        panel_x = right_margin - panel_w
        panel_y = int(25 * s)

        panel_bg_surf = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
        panel_bg_surf.fill((5, 15, 30, 220))
        screen.blit(panel_bg_surf, (panel_x, panel_y))

        corner_len = int(12 * s)
        pygame.draw.line(screen, CYAN, (panel_x, panel_y), (panel_x + corner_len, panel_y), 2)
        pygame.draw.line(screen, CYAN, (panel_x, panel_y), (panel_x, panel_y + corner_len), 2)
        pygame.draw.line(screen, (50, 150, 200), (panel_x + panel_w, panel_y + panel_h), (panel_x + panel_w - corner_len, panel_y + panel_h), 2)
        pygame.draw.line(screen, (50, 150, 200), (panel_x + panel_w, panel_y + panel_h), (panel_x + panel_w, panel_y + panel_h - corner_len), 2)

        hex_radius = int(16 * s)
        hex_cx = panel_x + int(30 * s)
        hex_cy = panel_y + int(24 * s)
        
        points = []
        for i in range(6):
            angle_deg = 60 * i - 30
            angle_rad = math.pi / 180 * angle_deg
            px = hex_cx + hex_radius * math.cos(angle_rad)
            py = hex_cy + hex_radius * math.sin(angle_rad)
            points.append((px, py))
        
        pygame.draw.polygon(screen, CYAN, points, 1)
        pygame.draw.circle(screen, CYAN, (hex_cx, hex_cy), int(3 * s))

        profile_label = self.get_font(12 * s, bold=True).render("ID.CARD", True, (120, 200, 255))
        screen.blit(profile_label, profile_label.get_rect(center=(hex_cx, hex_cy + int(26 * s))))

        text_x = hex_cx + int(30 * s)
        font_small = self.get_font(13 * s, bold=True)
        pilot_text = font_small.render(f"PILOT // {self.active_player.upper()}", True, WHITE)
        screen.blit(pilot_text, (text_x, panel_y + int(10 * s)))
        
        curr_stg = STAGE_CONFIGS[self.selected_stage]
        stg_text = font_small.render(f"SYS.STAGE // {self.selected_stage} [{curr_stg['name']}]", True, curr_stg["color"])
        screen.blit(stg_text, (text_x, panel_y + int(30 * s)))

        if self.show_stage_select:
            self.draw_stage_select(screen)
        elif self.show_leaderboard:
            self.draw_leaderboard(screen)

    def draw_stage_select(self, screen):
        s = self.get_scale_factor()
        w, h = self.game.current_width, self.game.current_height

        # Phủ lớp nền tối mờ sâu hơn để làm nổi bật các card stage
        overlay = pygame.Surface((w, h), pygame.SRCALPHA)
        overlay.fill((5, 10, 20, 240)) 
        screen.blit(overlay, (0, 0))

        font_title = self.get_font(36 * s, bold=True)
        font_option = self.get_font(20 * s, bold=True)
        font_sub = self.get_font(15 * s, bold=True)
        font_detail = self.get_font(14 * s, bold=True)  # Tăng kích thước và độ đậm chữ chi tiết

        title = font_title.render("SELECT DIFFICULTY STAGE", True, CYAN)
        screen.blit(title, title.get_rect(center=(w // 2, int(h * 0.09))))

        card_w = int(min(210 * s, (w - 80 * s) / 4))
        card_h = int(min(330 * s, h * 0.68))
        spacing = int(18 * s)
        start_x = (w - (card_w * 4 + spacing * 3)) // 2
        card_y = int(h * 0.16)

        for stg in range(1, 5):
            cx = start_x + (stg - 1) * (card_w + spacing)
            card_rect = pygame.Rect(cx, card_y, card_w, card_h)
            
            is_selected = (stg == self.selected_stage)
            cfg = STAGE_CONFIGS[stg]
            
            # Làm nền card sáng hơn một chút khi được chọn để dễ phân biệt
            bg_color = (25, 40, 60, 230) if is_selected else (15, 22, 32, 200)
            border_color = cfg["color"] if is_selected else (50, 70, 95)
            
            shape_surf = pygame.Surface((card_w, card_h), pygame.SRCALPHA)
            pygame.draw.rect(shape_surf, bg_color, shape_surf.get_rect(), border_radius=int(8 * s))
            pygame.draw.rect(shape_surf, border_color, shape_surf.get_rect(), width=int(2 * s) if is_selected else int(1 * s), border_radius=int(8 * s))
            screen.blit(shape_surf, (cx, card_y))

            stg_txt = font_option.render(f"STAGE {stg}", True, cfg["color"] if is_selected else WHITE)
            screen.blit(stg_txt, stg_txt.get_rect(center=(cx + card_w // 2, card_y + int(30 * s))))

            name_txt = font_sub.render(cfg["name"], True, cfg["color"])
            screen.blit(name_txt, name_txt.get_rect(center=(cx + card_w // 2, card_y + int(58 * s))))

            # Đổi màu tagline thành màu sáng dễ đọc hơn
            tagline_txt = font_detail.render(cfg["tagline"], True, (210, 225, 240))
            screen.blit(tagline_txt, tagline_txt.get_rect(center=(cx + card_w // 2, card_y + int(80 * s))))

            pygame.draw.line(screen, (70, 95, 125), (cx + int(15 * s), card_y + int(98 * s)), (cx + card_w - int(15 * s), card_y + int(98 * s)), 1)

            details = [
                f"Wave Size: {cfg['enemies_per_wave']}",
                f"Enemy HP: {cfg['enemy_hp']}",
                f"Speed: {cfg['enemy_speed']}",
                f"Boss HP: {cfg['boss_hp']}",
                f"Boss Score: {cfg['boss_spawn_score']}"
            ]
            for idx, d_str in enumerate(details):
                # Dùng màu TRẮNG SÁNG (WHITE) thay vì xám mờ để dễ nhìn tuyệt đối
                d_txt = font_detail.render(d_str, True, (255, 255, 255))
                screen.blit(d_txt, (cx + int(15 * s), card_y + int(115 * s + idx * 27 * s)))

            if stg == 4:
                danger_lbl = font_detail.render("[ EXTREME HELL ]", True, RED)
                screen.blit(danger_lbl, danger_lbl.get_rect(center=(cx + card_w // 2, card_y + card_h - int(20 * s))))

        hint = font_sub.render("A/D or Arrows: Select | ENTER/CLICK: Confirm | ESC: Cancel", True, (220, 235, 255))
        screen.blit(hint, hint.get_rect(center=(w // 2, h - int(25 * s))))

    def draw_leaderboard(self, screen):
        s = self.get_scale_factor()
        w, h = self.game.current_width, self.game.current_height

        overlay = pygame.Surface((w, h), pygame.SRCALPHA)
        overlay.fill((10, 15, 25, 230))
        screen.blit(overlay, (0, 0))

        font_title = self.get_font(34 * s, bold=True)
        font_sub = self.get_font(16 * s, bold=False)
        font_option = self.get_font(20 * s, bold=True)

        panel_w = int(min(740 * s, w * 0.82))
        panel_h = int(min(400 * s, h * 0.80))
        panel_x = (w - panel_w) // 2
        panel_y = (h - panel_h) // 2
        
        panel_rect = pygame.Rect(panel_x, panel_y, panel_w, panel_h)
        pygame.draw.rect(screen, (20, 30, 45), panel_rect, border_radius=int(12 * s))
        pygame.draw.rect(screen, CYAN, panel_rect, width=int(1 * s), border_radius=int(12 * s))

        title = font_title.render("TOP 5 PILOTS LEADERBOARD", True, CYAN)
        screen.blit(title, title.get_rect(center=(w // 2, panel_y + int(35 * s))))

        col_x = {
            "RANK": panel_x + int(panel_w * 0.06),
            "PILOT": panel_x + int(panel_w * 0.18),
            "SCORE": panel_x + int(panel_w * 0.44),
            "STAGE": panel_x + int(panel_w * 0.65),
            "KILLS": panel_x + int(panel_w * 0.82)
        }
        header_y = panel_y + int(80 * s)

        for col_name, x_pos in col_x.items():
            txt = font_sub.render(col_name, True, GREEN)
            screen.blit(txt, (x_pos, header_y))

        pygame.draw.line(screen, (50, 70, 100), (panel_x + int(25 * s), header_y + int(25 * s)), (panel_x + panel_w - int(25 * s), header_y + int(25 * s)), 1)

        top_scores = self.db.get_top_scores(5)
        start_y = header_y + int(36 * s)

        if not top_scores:
            empty_txt = font_option.render("No Records Found! Be the first pilot.", True, WHITE)
            screen.blit(empty_txt, empty_txt.get_rect(center=(w // 2, panel_y + panel_h // 2)))
        else:
            for idx, row in enumerate(top_scores):
                name, score, stage_num, kills, date_str = row
                row_y = start_y + idx * int(35 * s)
                color = YELLOW if idx == 0 else WHITE
                
                stg_name = STAGE_CONFIGS.get(stage_num, {}).get("name", f"Stg {stage_num}")
                
                screen.blit(font_sub.render(f"#{idx+1}", True, color), (col_x["RANK"], row_y))
                screen.blit(font_sub.render(str(name)[:12], True, color), (col_x["PILOT"], row_y))
                screen.blit(font_sub.render(str(score), True, color), (col_x["SCORE"], row_y))
                screen.blit(font_sub.render(stg_name, True, color), (col_x["STAGE"], row_y))
                screen.blit(font_sub.render(str(kills), True, color), (col_x["KILLS"], row_y))

        hint = font_sub.render("Press ANY KEY or CLICK to return to Menu", True, (180, 180, 180))
        screen.blit(hint, hint.get_rect(center=(w // 2, panel_y + panel_h - int(25 * s))))