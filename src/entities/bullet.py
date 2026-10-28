import pygame
import math
from settings import *

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, direction_or_target, groups, is_enemy=False, game=None):
        super().__init__(*groups)
        self.game = game
        
        self.is_enemy = is_enemy
        self.speed = 400 if is_enemy else 700
        
        # Sát thương mặc định là 10 (sẽ được ghi đè bởi chỉ số nâng cấp của Player)
        self.damage = 10
        
        if isinstance(direction_or_target, pygame.math.Vector2):
            self.dx = direction_or_target.x
            self.dy = direction_or_target.y
        else:
            self.dx, self.dy = 0, -1

        self.angle = math.degrees(math.atan2(-self.dy, self.dx)) - 90
        self.create_laser_image()
        
        self.rect = self.image.get_rect()
        self.pos = pygame.math.Vector2(x, y)
        self.rect.center = (int(self.pos.x), int(self.pos.y))

    def create_laser_image(self):
        w, h = 6, 24
        self.original_image = pygame.Surface((w, h), pygame.SRCALPHA)
        
        core_color = WHITE
        glow_color = (255, 50, 50, 200) if self.is_enemy else (0, 230, 255, 200)
        
        pygame.draw.rect(self.original_image, glow_color, (0, 0, w, h), border_radius=3)
        pygame.draw.rect(self.original_image, core_color, (2, 2, w-4, h-4), border_radius=2)
        
        self.image = pygame.transform.rotate(self.original_image, self.angle)

    def update(self, dt):
        self.pos.x += self.dx * self.speed * dt
        self.pos.y += self.dy * self.speed * dt
        self.rect.center = (int(self.pos.x), int(self.pos.y))

        max_w = self.game.current_width if (self.game and hasattr(self.game, 'current_width')) else SCREEN_WIDTH
        max_h = self.game.current_height if (self.game and hasattr(self.game, 'current_height')) else SCREEN_HEIGHT

        if (self.rect.right < -300 or self.rect.left > max_w + 300 or
            self.rect.bottom < -300 or self.rect.top > max_h + 300):
            self.kill()