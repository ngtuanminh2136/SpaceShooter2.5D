import pygame
import sys
from settings import *
from utils.db_manager import DatabaseManager

class NameInputState:
    def __init__(self, game):
        self.game = game
        self.db = DatabaseManager()
        
        self.font_title = pygame.font.SysFont("arial", 48, bold=True)
        self.font_sub = pygame.font.SysFont("arial", 24)
        self.font_input = pygame.font.SysFont("arial", 28, bold=True)
        
        self.player_name = ""

    def handle_events(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                final_name = self.player_name.strip() if self.player_name.strip() else "PILOT"
                self.db.set_active_player(final_name)
                from states.menu_state import MenuState
                self.game.change_state(MenuState(self.game))
            elif event.key == pygame.K_BACKSPACE:
                self.player_name = self.player_name[:-1]
            elif event.key == pygame.K_ESCAPE:
                # Sửa thành quay lại Menu chính thay vì thoát game
                from states.menu_state import MenuState
                self.game.change_state(MenuState(self.game))
            else:
                if len(self.player_name) < 12 and (event.unicode.isalnum() or event.unicode in ['_', '-']):
                    self.player_name += event.unicode.upper()

    def update(self, dt):
        pass

    def draw(self, screen):
        screen.fill((10, 15, 30))
        
        # Tiêu đề Chào mừng người chơi mới
        title = self.font_title.render("WELCOME, NEW PILOT!", True, GREEN)
        title_rect = title.get_rect(center=(self.game.current_width // 2, self.game.current_height // 3 - 30))
        screen.blit(title, title_rect)

        sub = self.font_sub.render("Please enter your callsign / name to begin:", True, WHITE)
        sub_rect = sub.get_rect(center=(self.game.current_width // 2, self.game.current_height // 3 + 30))
        screen.blit(sub, sub_rect)

        # Ô nhập tên
        box_w, box_h = 300, 50
        box_rect = pygame.Rect((self.game.current_width - box_w) // 2, self.game.current_height // 2, box_w, box_h)
        pygame.draw.rect(screen, (30, 35, 60), box_rect)
        pygame.draw.rect(screen, YELLOW, box_rect, 2)

        # Con trỏ nhấp nháy _
        cursor = "_" if (pygame.time.get_ticks() // 500) % 2 == 0 else ""
        name_txt = self.font_input.render(self.player_name + cursor, True, WHITE)
        name_rect = name_txt.get_rect(center=box_rect.center)
        screen.blit(name_txt, name_rect)

        # Hướng dẫn (Đã đổi 'Quit' thành 'Back')
        hint = self.font_sub.render("Press 'ENTER' to Confirm | 'ESC' to Back", True, GRAY)
        hint_rect = hint.get_rect(center=(self.game.current_width // 2, self.game.current_height - 60))
        screen.blit(hint, hint_rect)