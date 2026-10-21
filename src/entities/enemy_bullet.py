import pygame
import math
from settings import *

class EnemyBullet(pygame.sprite.Sprite):
    def __init__(self, x, y, direction_or_target, groups):
        super().__init__(*groups)
        
        self.speed = 450
        
        if isinstance(direction_or_target, pygame.math.Vector2):
            self.dx = direction_or_target.x
            self.dy = direction_or_target.y
        else:
            self.dx, self.dy = 0, 1

        self.angle = math.degrees(math.atan2(-self.dy, self.dx)) - 90
        self.create_laser_image()
        
        self.rect = self.image.get_rect()
        self.pos = pygame.math.Vector2(x, y)
        self.rect.center = (int(self.pos.x), int(self.pos.y))

    def create_laser_image(self):
        w, h = 6, 22
        self.original_image = pygame.Surface((w, h), pygame.SRCALPHA)
        
        # Viền phát sáng màu Đỏ cam Sci-fi, lõi trắng
        glow_color = (255, 60, 30, 200)
        core_color = (255, 220, 100)
        
        pygame.draw.rect(self.original_image, glow_color, (0, 0, w, h), border_radius=3)
        pygame.draw.rect(self.original_image, core_color, (2, 2, w-4, h-4), border_radius=2)
        
        self.image = pygame.transform.rotate(self.original_image, self.angle)

    def update(self, dt):
        self.pos.x += self.dx * self.speed * dt
        self.pos.y += self.dy * self.speed * dt
        self.rect.center = (int(self.pos.x), int(self.pos.y))

        if (self.rect.right < -100 or self.rect.left > SCREEN_WIDTH + 100 or
            self.rect.bottom < -100 or self.rect.top > SCREEN_HEIGHT + 100):
            self.kill()