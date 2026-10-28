import pygame
import math

class Item(pygame.sprite.Sprite):
    def __init__(self, x, y, item_type, groups, game):
        super().__init__(groups)
        self.game = game
        self.item_type = item_type # 'heal', 'triple_shot', hoặc 'shield'
        
        self.size = 24
        self.original_image = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        
        if self.item_type == 'heal':
            pygame.draw.circle(self.original_image, (0, 255, 100), (12, 12), 12)
            pygame.draw.rect(self.original_image, (255, 255, 255), (10, 4, 4, 16))
            pygame.draw.rect(self.original_image, (255, 255, 255), (4, 10, 16, 4))
        elif self.item_type == 'triple_shot':
            pygame.draw.circle(self.original_image, (255, 220, 0), (12, 12), 12)
            pygame.draw.rect(self.original_image, (255, 50, 50), (6, 6, 3, 12))
            pygame.draw.rect(self.original_image, (255, 50, 50), (11, 4, 3, 14))
            pygame.draw.rect(self.original_image, (255, 50, 50), (16, 6, 3, 12))
        elif self.item_type == 'shield':
            pygame.draw.circle(self.original_image, (0, 180, 255), (12, 12), 12)
            pygame.draw.circle(self.original_image, (255, 255, 255), (12, 12), 7, 2)
            pygame.draw.circle(self.original_image, (0, 220, 255), (12, 12), 4)

        self.image = self.original_image
        self.rect = self.image.get_rect(center=(x, y))
        self.pos = pygame.math.Vector2(x, y)
        
        self.angle = 0
        self.lifespan = 10.0 

    def update(self, dt):
        self.lifespan -= dt
        if self.lifespan <= 0:
            self.kill()
            return

        self.angle = (self.angle + 90 * dt) % 360
        self.image = pygame.transform.rotate(self.original_image, int(self.angle))
        self.rect = self.image.get_rect(center=(round(self.pos.x), round(self.pos.y)))