import pygame
import math
from utils.asset_loader import load_image
from utils.particles import Particle
from entities.enemy_bullet import EnemyBullet

class Boss(pygame.sprite.Sprite):
    def __init__(self, x, y, groups, game, player, enemy_bullet_groups, particle_groups):
        super().__init__(groups)
        self.game = game
        self.player = player
        self.enemy_bullet_groups = enemy_bullet_groups
        self.particle_groups = particle_groups
        
        # Tải ảnh boss.png (Nếu chưa có ảnh, tự vẽ phi thuyền khổng lồ 120x120)
        self.original_image = load_image('boss1.png', (120, 120))
        if self.original_image.get_size() == (64, 64): 
            self.original_image = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.polygon(self.original_image, (200, 0, 50), [(60, 120), (0, 0), (120, 0)])
            pygame.draw.circle(self.original_image, (255, 200, 0), (60, 40), 20)

        self.image = self.original_image
        self.rect = self.image.get_rect(center=(x, y))
        self.pos = pygame.math.Vector2(x, y)
        
        self.speed = 70
        self.max_hp = 300 # Máu Boss rất trâu
        self.hp = self.max_hp
        
        self.shoot_timer = 0.0
        self.shoot_cooldown = 1.5 # 1.5 giây bắn 1 đợt đạn tỏa 5 tia

    def update(self, dt):
        self.move(dt)
        self.rotate()
        self.shoot(dt)

    def move(self, dt):
        # Boss di chuyển từ từ áp sát người chơi nhưng giữ khoảng cách > 200px
        direction = pygame.math.Vector2(self.player.pos.x - self.pos.x, self.player.pos.y - self.pos.y)
        if direction.length() > 200:
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

    def shoot(self, dt):
        self.shoot_timer -= dt
        if self.shoot_timer <= 0:
            # Tính hướng cơ sở về phía người chơi
            base_dir = pygame.math.Vector2(self.player.pos.x - self.pos.x, self.player.pos.y - self.pos.y)
            if base_dir.length() > 0:
                base_dir = base_dir.normalize()
            else:
                base_dir = pygame.math.Vector2(0, 1)

            # Bắn 5 viên đạn tỏa ra các góc (-30, -15, 0, 15, 30 độ)
            for angle in [-30, -15, 0, 15, 30]:
                shot_dir = base_dir.rotate(angle)
                EnemyBullet(self.pos.x, self.pos.y, shot_dir, self.enemy_bullet_groups)
                
            self.shoot_timer = self.shoot_cooldown

    def take_damage(self, amount):
        self.hp -= amount
        if self.hp <= 0:
            self.kill()
            # Nổ cực to với 60 hạt particle văng ra
            for _ in range(60):
                Particle(self.pos.x, self.pos.y, self.particle_groups)