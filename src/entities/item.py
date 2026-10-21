import pygame
import math

class Item(pygame.sprite.Sprite):
    def __init__(self, x, y, item_type, groups, game):
        super().__init__(groups)
        self.game = game
        self.item_type = item_type # 'heal' hoặc 'triple_shot'
        
        # Tạo hình khối hiển thị tượng trưng cho Item
        self.size = 24
        self.original_image = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        
        if self.item_type == 'heal':
            # Ô màu xanh lá chữ thập/tròn đại diện cho Hồi máu
            pygame.draw.circle(self.original_image, (0, 255, 100), (12, 12), 12)
            pygame.draw.rect(self.original_image, (255, 255, 255), (10, 4, 4, 16))
            pygame.draw.rect(self.original_image, (255, 255, 255), (4, 10, 16, 4))
        elif self.item_type == 'triple_shot':
            # Ô màu vàng đại diện cho Đạn 3 nòng
            pygame.draw.circle(self.original_image, (255, 220, 0), (12, 12), 12)
            # Vẽ 3 vạch đạn
            pygame.draw.rect(self.original_image, (255, 50, 50), (6, 6, 3, 12))
            pygame.draw.rect(self.original_image, (255, 50, 50), (11, 4, 3, 14))
            pygame.draw.rect(self.original_image, (255, 50, 50), (16, 6, 3, 12))

        self.image = self.original_image
        self.rect = self.image.get_rect(center=(x, y))
        self.pos = pygame.math.Vector2(x, y)
        
        # Biến hiệu ứng xoay nhẹ cho đẹp mắt
        self.angle = 0
        # Tự biến mất sau 10 giây nếu người chơi không nhặt
        self.lifespan = 10.0 

    def update(self, dt):
        self.lifespan -= dt
        if self.lifespan <= 0:
            self.kill()
            return

        # Hiệu ứng xoay tròn vật phẩm
        self.angle = (self.angle + 90 * dt) % 360
        self.image = pygame.transform.rotate(self.original_image, int(self.angle))
        self.rect = self.image.get_rect(center=(round(self.pos.x), round(self.pos.y)))