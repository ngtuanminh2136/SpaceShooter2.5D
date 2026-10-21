# src/utils/particles.py
import pygame
import random

class Particle(pygame.sprite.Sprite):
    def __init__(self, x, y, groups):
        super().__init__(groups)
        
        # Tạo kích thước ngẫu nhiên cho hạt vụn
        self.size = random.randint(4, 8)
        self.image = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        
        # Chọn màu ngẫu nhiên (Cam, Đỏ, hoặc Vàng nhạt)
        self.color = random.choice([(255, 100, 0), (255, 50, 0), (255, 200, 50)]) 
        self.image.fill(self.color)
        
        self.rect = self.image.get_rect(center=(x, y))
        self.pos = pygame.math.Vector2(x, y)
        
        # Tạo hướng văng ngẫu nhiên 360 độ
        self.velocity = pygame.math.Vector2(random.uniform(-1, 1), random.uniform(-1, 1))
        if self.velocity.length() > 0:
            # Tốc độ văng ra ngẫu nhiên
            self.velocity = self.velocity.normalize() * random.randint(100, 300)
            
        # Thời gian tồn tại của hạt (0.2 đến 0.5 giây)
        self.timer = random.uniform(0.2, 0.5)

    def update(self, dt):
        # Di chuyển hạt
        self.pos += self.velocity * dt
        self.rect.center = (round(self.pos.x), round(self.pos.y))
        
        # Giảm dần kích thước hạt (tạo hiệu ứng mờ dần/teo nhỏ)
        if self.timer > 0:
            self.timer -= dt
        else:
            self.kill() # Xóa hạt khi hết thời gian