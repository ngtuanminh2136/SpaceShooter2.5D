import pygame
import sys
import math
from settings import *
from utils.db_manager import DatabaseManager

class NameInputState:
    def __init__(self, game):
        self.game = game
        self.db = DatabaseManager()
        
        self.font_title = pygame.font.SysFont("consolas", 48, bold=True)
        self.font_sub = pygame.font.SysFont("consolas", 24)
        self.font_input = pygame.font.SysFont("consolas", 28, bold=True)
        
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
                from states.menu_state import MenuState
                self.game.change_state(MenuState(self.game))
            else:
                if len(self.player_name) < 12 and (event.unicode.isalnum() or event.unicode in ['_', '-']):
                    self.player_name += event.unicode.upper()

    def update(self, dt):
        pass

    def draw(self, screen):
        screen.fill((10, 15, 30))
        
        title_text = "WELCOME, NEW PILOT!"
        shadow = self.font_title.render(title_text, True, (0, 0, 0))
        title_rect_shadow = shadow.get_rect(center=(self.game.current_width // 2 + 3, self.game.current_height // 3 - 27))
        screen.blit(shadow, title_rect_shadow)
        
        title = self.font_title.render(title_text, True, (0, 255, 150))
        title_rect = title.get_rect(center=(self.game.current_width // 2, self.game.current_height // 3 - 30))
        screen.blit(title, title_rect)

        sub = self.font_sub.render("Please enter your callsign / name to begin:", True, (200, 220, 255))
        sub_rect = sub.get_rect(center=(self.game.current_width // 2, self.game.current_height // 3 + 30))
        screen.blit(sub, sub_rect)

        box_w, box_h = 320, 60
        box_rect = pygame.Rect((self.game.current_width - box_w) // 2, self.game.current_height // 2, box_w, box_h)
        
        box_surface = pygame.Surface((box_w, box_h), pygame.SRCALPHA)
        pygame.draw.rect(box_surface, (0, 150, 255, 40), box_surface.get_rect())
        screen.blit(box_surface, box_rect.topleft)

        color_neon = (0, 200, 255)
        line_len = 20
        thick = 3
        x, y, w, h = box_rect
        
        pygame.draw.line(screen, color_neon, (x, y), (x + line_len, y), thick)
        pygame.draw.line(screen, color_neon, (x, y), (x, y + line_len), thick)
        pygame.draw.line(screen, color_neon, (x + w, y), (x + w - line_len, y), thick)
        pygame.draw.line(screen, color_neon, (x + w, y), (x + w, y + line_len), thick)
        pygame.draw.line(screen, color_neon, (x, y + h), (x + line_len, y + h), thick)
        pygame.draw.line(screen, color_neon, (x, y + h), (x, y + h - line_len), thick)
        pygame.draw.line(screen, color_neon, (x + w, y + h), (x + w - line_len, y + h), thick)
        pygame.draw.line(screen, color_neon, (x + w, y + h), (x + w, y + h - line_len), thick)

        name_txt = self.font_input.render(self.player_name, True, (255, 255, 255))
        name_rect = name_txt.get_rect(center=box_rect.center)
        screen.blit(name_txt, name_rect)

        if self.player_name == "":
            cursor_x = box_rect.centerx - 6
        else:
            cursor_x = name_rect.right + 4

        if (pygame.time.get_ticks() // 500) % 2 == 0:
            pygame.draw.rect(screen, (0, 255, 150), (cursor_x, box_rect.y + 15, 12, box_h - 30))

        alpha = int(abs(math.sin(pygame.time.get_ticks() / 500.0)) * 255)
        hint = self.font_sub.render("Press 'ENTER' to Confirm | 'ESC' to Back", True, (150, 150, 150))
        hint.set_alpha(max(40, alpha))
        hint_rect = hint.get_rect(center=(self.game.current_width // 2, self.game.current_height - 60))
        screen.blit(hint, hint_rect)