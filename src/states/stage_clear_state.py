import pygame
import sys
from settings import *

class StageClearState:
    def __init__(self, game, pilot_name="HOHO", score=0, kills=0, stage=1):
        self.game = game
        self.pilot_name = pilot_name
        self.score = score
        self.kills = kills
        self.stage = stage

        try:
            self.title_font = pygame.font.SysFont("arial", 48, bold=True)
            self.stats_font = pygame.font.SysFont("arial", 28)
            self.btn_font = pygame.font.SysFont("arial", 24, bold=True)
        except:
            self.title_font = pygame.font.Font(None, 60)
            self.stats_font = pygame.font.Font(None, 36)
            self.btn_font = pygame.font.Font(None, 32)

    def handle_events(self, event):
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_n:
                from states.play_state import PlayState
                self.game.state = PlayState(self.game, stage_id=self.stage + 1)
            elif event.key == pygame.K_r:
                from states.play_state import PlayState
                self.game.state = PlayState(self.game, stage_id=self.stage)
            elif event.key == pygame.K_m:
                from states.menu_state import MenuState
                self.game.state = MenuState(self.game)
            elif event.key == pygame.K_q:
                pygame.quit()
                sys.exit()

    def update(self, dt):
        pass

    def draw(self, screen):
        screen_width = screen.get_width()
        screen_height = screen.get_height()

        overlay = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
        overlay.fill((10, 15, 25, 200))
        screen.blit(overlay, (0, 0))

        title_text = f"SYS.OVERRIDE: STAGE {self.stage} CLEARED"
        title_surf = self.title_font.render(title_text, True, (0, 255, 255))
        title_rect = title_surf.get_rect(center=(screen_width // 2, screen_height // 2 - 120))
        screen.blit(title_surf, title_rect)

        panel_width, panel_height = 500, 100
        panel_x = (screen_width - panel_width) // 2
        panel_y = screen_height // 2 - 40
        
        pygame.draw.rect(screen, (20, 25, 40), (panel_x, panel_y, panel_width, panel_height), border_radius=10)
        pygame.draw.rect(screen, (0, 150, 150), (panel_x, panel_y, panel_width, panel_height), 2, border_radius=10)

        pilot_surf = self.stats_font.render(f"PILOT: {self.pilot_name}", True, (200, 200, 200))
        score_surf = self.stats_font.render(f"SCORE: {self.score}", True, (255, 215, 0))
        kills_surf = self.stats_font.render(f"KILLS: {self.kills}", True, (255, 100, 100))

        screen.blit(pilot_surf, (panel_x + 30, panel_y + 35))
        screen.blit(score_surf, (panel_x + 200, panel_y + 35))
        screen.blit(kills_surf, (panel_x + 370, panel_y + 35))

        controls = [
            ("N", "NEXT STAGE", (0, 255, 100)),
            ("R", "REPLAY", (200, 200, 200)),
            ("M", "MENU", (200, 200, 200)),
            ("Q", "QUIT", (255, 80, 80))
        ]
        
        start_x = screen_width // 2 - 320
        btn_y = screen_height // 2 + 100
        spacing = 170

        for i, (key, label, color) in enumerate(controls):
            x_pos = start_x + (i * spacing)
            key_surf = self.btn_font.render(f"[{key}]", True, (255, 255, 255))
            key_rect = key_surf.get_rect(topleft=(x_pos, btn_y))
            pygame.draw.rect(screen, (50, 55, 70), key_rect.inflate(16, 10), border_radius=5)
            screen.blit(key_surf, key_rect)

            label_surf = self.btn_font.render(label, True, color)
            screen.blit(label_surf, (key_rect.right + 15, btn_y))