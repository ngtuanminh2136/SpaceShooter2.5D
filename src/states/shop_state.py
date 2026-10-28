import pygame
import sys
import math
from settings import *

class ShopState:
    def __init__(self, game, return_state="menu"):
        self.game = game
        self.return_state = return_state
        
        self.font_title = pygame.font.SysFont("consolas", 40, bold=True)
        self.font_hud = pygame.font.SysFont("consolas", 20, bold=True)
        self.font_item = pygame.font.SysFont("consolas", 18)
        
        self.shop_items = [
            {"name": "MAX HP", "key": "hp", "base_cost": 100, "cost_scale": 50, "bonus": "+20 HP"},
            {"name": "DAMAGE", "key": "damage", "base_cost": 150, "cost_scale": 75, "bonus": "+5 Damage"},
            {"name": "SPEED", "key": "speed", "base_cost": 120, "cost_scale": 60, "bonus": "+25 Speed"},
            {"name": "MAX SHIELD", "key": "shield", "base_cost": 150, "cost_scale": 75, "bonus": "+15 Shield"}
        ]

    def get_cost(self, item):
        upgrades = getattr(self.game, 'upgrades', {'hp': 0, 'damage': 0, 'speed': 0, 'shield': 0})
        level = upgrades[item["key"]]
        return item["base_cost"] + level * item["cost_scale"]

    def buy_upgrade(self, index):
        item = self.shop_items[index]
        cost = self.get_cost(item)
        
        coins = getattr(self.game, 'coins', 0)
        if coins >= cost:
            self.game.coins -= cost
            self.game.upgrades[item["key"]] += 1
            if hasattr(self.game, 'sound_manager'):
                self.game.sound_manager.play('powerup')

    def handle_events(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_1, pygame.K_KP1): self.buy_upgrade(0)
            elif event.key in (pygame.K_2, pygame.K_KP2): self.buy_upgrade(1)
            elif event.key in (pygame.K_3, pygame.K_KP3): self.buy_upgrade(2)
            elif event.key in (pygame.K_4, pygame.K_KP4): self.buy_upgrade(3)
            elif event.key in (pygame.K_RETURN, pygame.K_ESCAPE, pygame.K_SPACE):
                if self.return_state == "play":
                    from states.play_state import PlayState
                    stage_id = getattr(self.game, 'current_stage', 1)
                    self.game.change_state(PlayState(self.game, stage_id=stage_id))
                else:
                    from states.menu_state import MenuState
                    self.game.change_state(MenuState(self.game))

    def update(self, dt):
        pass

    def draw(self, screen):
        screen.fill((10, 15, 30))
        w, h = self.game.current_width, self.game.current_height
        
        title = self.font_title.render("ARMORY & UPGRADES", True, (0, 255, 200))
        screen.blit(title, title.get_rect(center=(w // 2, 50)))
        
        coins = getattr(self.game, 'coins', 0)
        coins_txt = self.font_hud.render(f"CREDITS: {coins} COINS", True, (255, 215, 0))
        screen.blit(coins_txt, coins_txt.get_rect(center=(w // 2, 95)))

        start_y = 140
        box_w, box_h = min(600, w - 80), 65
        upgrades = getattr(self.game, 'upgrades', {'hp': 0, 'damage': 0, 'speed': 0, 'shield': 0})

        for i, item in enumerate(self.shop_items):
            level = upgrades[item["key"]]
            cost = self.get_cost(item)
            box_rect = pygame.Rect((w - box_w) // 2, start_y + i * 80, box_w, box_h)
            
            can_afford = coins >= cost
            border_color = (0, 200, 255) if can_afford else (100, 100, 100)
            
            box_bg = pygame.Surface((box_w, box_h), pygame.SRCALPHA)
            box_bg.fill((20, 30, 50, 180) if can_afford else (15, 15, 20, 180))
            screen.blit(box_bg, box_rect.topleft)
            pygame.draw.rect(screen, border_color, box_rect, 2, border_radius=6)

            key_txt = self.font_hud.render(f"[{i+1}]", True, (255, 255, 255))
            screen.blit(key_txt, (box_rect.x + 15, box_rect.y + 20))

            name_txt = self.font_hud.render(f"{item['name']} (LVL {level})", True, (255, 255, 255))
            bonus_txt = self.font_item.render(f"Effect: {item['bonus']}", True, (150, 200, 255))
            screen.blit(name_txt, (box_rect.x + 70, box_rect.y + 12))
            screen.blit(bonus_txt, (box_rect.x + 70, box_rect.y + 36))

            cost_color = (255, 215, 0) if can_afford else (255, 80, 80)
            cost_txt = self.font_hud.render(f"{cost} C", True, cost_color)
            screen.blit(cost_txt, (box_rect.right - 120, box_rect.y + 22))

        hint = self.font_item.render("Press [ENTER] or [ESC] to Return", True, (150, 150, 150))
        screen.blit(hint, hint.get_rect(center=(w // 2, h - 40)))