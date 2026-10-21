# src/entities/enemy.py
import pygame
import math
from utils.asset_loader import load_image
from utils.particles import Particle

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, groups, game, player, particle_groups):
        super().__init__(groups)
        self.game = game
        self.player = player
        self.particle_groups = particle_groups
        
        # Tải ảnh enemy.png (Nếu bạn không có ảnh, hàm này tự bọc lại bằng hình vuông màu hồng)
        # Bạn có thể tự tải 1 ảnh tàu địch đặt tên enemy.png cho vào assets/images/
        self.original_image = load_image('ufo_game_enemy.png', (50, 50))
        
        # Nếu chưa có ảnh, mình đổi màu cái khối vuông mặc định thành ĐỎ cho dễ phân biệt
        if self.original_image.get_size() == (64, 64): 
            self.original_image.fill((255, 50, 50))

        self.image = self.original_image
        self.rect = self.image.get_rect(center=(x, y))
        self.pos = pygame.math.Vector2(x, y)
        
        self.speed = 150 # Chậm hơn người chơi một chút
        self.hp = 30     # Máu của kẻ thù

    def update(self, dt):
        self.move_towards_player(dt)
        self.rotate()

    def move_towards_player(self, dt):
        # Tính vector hướng tới người chơi
        direction = pygame.math.Vector2(self.player.pos.x - self.pos.x, self.player.pos.y - self.pos.y)
        
        if direction.length() > 0:
            direction = direction.normalize()
        
        self.pos += direction * self.speed * dt
        self.rect.center = (round(self.pos.x), round(self.pos.y))

    def rotate(self):
        rel_x = self.player.pos.x - self.pos.x
        rel_y = self.player.pos.y - self.pos.y
        angle = (180 / math.pi) * -math.atan2(rel_y, rel_x) - 90
        
        self.image = pygame.transform.rotate(self.original_image, int(angle))
        self.rect = self.image.get_rect(center=self.rect.center)

    def take_damage(self, amount):
        self.hp -= amount
        # Nếu hết máu thì chết và văng mảnh vụn
        if self.hp <= 0:
            self.kill() 
            # Bắn ra 20 hạt vụn (particles) tại vị trí quái chết
            for _ in range(20):
                Particle(self.pos.x, self.pos.y, self.particle_groups)