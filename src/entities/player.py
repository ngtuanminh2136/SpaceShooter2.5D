import pygame
import math
import random
from settings import *
from utils.asset_loader import load_image
from utils.particles import Particle
from entities.bullet import Bullet

class Player(pygame.sprite.Sprite):
    def __init__(self, groups, game, bullet_groups):
        super().__init__(groups)
        self.game = game
        self.bullet_groups = bullet_groups 
        
        self.original_image = load_image('ship7.png', (64, 64))
        self.image = self.original_image
        
        center_x = self.game.current_width // 2
        center_y = self.game.current_height // 2
        self.rect = self.image.get_rect(center=(center_x, center_y))
        
        self.pos = pygame.math.Vector2(self.rect.center)
        self.speed = PLAYER_SPEED

        # Lưu trữ góc quay của tàu để dùng cho vệt lửa đuôi
        self.angle = 0

        # Chỉ số máu
        self.max_hp = PLAYER_HP
        self.hp = self.max_hp

        # Cooldown bắn
        self.shoot_cooldown = 0.15 
        self.shoot_timer = 0

        # Trạng thái đạn chùm
        self.triple_shot_timer = 0

    def update(self, dt):
        if self.shoot_timer > 0:
            self.shoot_timer -= dt

        if self.triple_shot_timer > 0:
            self.triple_shot_timer -= dt

        self.move(dt)
        self.rotate()
        self.shoot()

    def move(self, dt):
        keys = pygame.key.get_pressed()
        direction = pygame.math.Vector2(0, 0)
        if keys[pygame.K_UP] or keys[pygame.K_w]: direction.y -= 1
        if keys[pygame.K_DOWN] or keys[pygame.K_s]: direction.y += 1
        if keys[pygame.K_LEFT] or keys[pygame.K_a]: direction.x -= 1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]: direction.x += 1

        if direction.length() > 0:
            direction = direction.normalize()

        self.pos += direction * self.speed * dt
        self.rect.center = (round(self.pos.x), round(self.pos.y))

        # Giới hạn trong màn hình
        if self.rect.left < 0:
            self.rect.left = 0
        elif self.rect.right > self.game.current_width:
            self.rect.right = self.game.current_width

        if self.rect.top < 0:
            self.rect.top = 0
        elif self.rect.bottom > self.game.current_height:
            self.rect.bottom = self.game.current_height
            
        self.pos.x = self.rect.centerx
        self.pos.y = self.rect.centery

    def draw_engine_trail(self, surface):
        # Vẽ vệt lửa đuôi tàu lớn hơn và xoay đồng bộ theo góc của phi thuyền
        s = self.game.get_scale_factor() if hasattr(self.game, 'get_scale_factor') else 1.0
        
        # Vector offset mặc định nằm phía sau đuôi tàu
        local_offset = pygame.math.Vector2(0, 22 * s)
        
        # Xoay vector offset theo góc hiện tại của tàu
        rotated_offset = local_offset.rotate(-self.angle)
        trail_pos = self.pos + rotated_offset
        
        # Tăng kích thước ngọn lửa lên (dài hơn và rộng hơn)
        flame_len = random.randint(18, 28) * s
        tip_offset = pygame.math.Vector2(0, flame_len).rotate(-self.angle)
        tip_pos = trail_pos + tip_offset
        
        # Mở rộng bề ngang cánh lửa
        left_wing_offset = pygame.math.Vector2(-8 * s, 0).rotate(-self.angle)
        right_wing_offset = pygame.math.Vector2(8 * s, 0).rotate(-self.angle)
        
        p1 = trail_pos + left_wing_offset
        p2 = trail_pos + right_wing_offset
        p3 = tip_pos
        
        # Tăng kích thước Surface chứa vệt lửa để không bị cắt cụt
        trail_surf = pygame.Surface((int(70 * s), int(70 * s)), pygame.SRCALPHA)
        
        center_surf = pygame.math.Vector2(35 * s, 35 * s)
        lp1 = center_surf + (p1 - trail_pos)
        lp2 = center_surf + (p2 - trail_pos)
        lp3 = center_surf + (p3 - trail_pos)
        
        # Vẽ tam giác lửa với độ trong suốt vừa phải cho rực rỡ
        pygame.draw.polygon(trail_surf, (0, 220, 255, 180), [lp1, lp2, lp3])
        surface.blit(trail_surf, (trail_pos.x - 35 * s, trail_pos.y - 35 * s))

    def rotate(self):
        mouse_x, mouse_y = pygame.mouse.get_pos()
        rel_x = mouse_x - self.pos.x
        rel_y = mouse_y - self.pos.y
        
        # Tính góc xoay và lưu vào self.angle
        self.angle = (180 / math.pi) * -math.atan2(rel_y, rel_x) - 90
        
        self.image = pygame.transform.rotate(self.original_image, int(self.angle))
        self.rect = self.image.get_rect(center=self.rect.center)

    def shoot(self):
        mouse_pressed = pygame.mouse.get_pressed()
        
        if mouse_pressed[0] and self.shoot_timer <= 0:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            direction = pygame.math.Vector2(mouse_x - self.pos.x, mouse_y - self.pos.y)
            
            if direction.length() > 0:
                direction = direction.normalize()
            else:
                direction = pygame.math.Vector2(0, -1) 
            
            muzzle_offset = 40 
            spawn_x = self.pos.x + direction.x * muzzle_offset
            spawn_y = self.pos.y + direction.y * muzzle_offset
            
            # Bắn đạn
            if self.triple_shot_timer > 0:
                dir_center = direction
                dir_left = direction.rotate(-15)
                dir_right = direction.rotate(15)
                
                Bullet(spawn_x, spawn_y, dir_center, self.bullet_groups, game=self.game)
                Bullet(spawn_x, spawn_y, dir_left, self.bullet_groups, game=self.game)
                Bullet(spawn_x, spawn_y, dir_right, self.bullet_groups, game=self.game)
            else:
                Bullet(spawn_x, spawn_y, direction, self.bullet_groups, game=self.game)
            
            # Phát âm thanh bắn súng
            if hasattr(self.game.state, 'sound_manager'):
                self.game.state.sound_manager.play('laser')

            self.shoot_timer = self.shoot_cooldown

    def draw(self, surface):
        # Vẽ vệt lửa đuôi tàu trước khi vẽ hình phi thuyền lên trên
        self.draw_engine_trail(surface)
        surface.blit(self.image, self.rect)

    def draw_health(self, screen):
        ratio = self.hp / self.max_hp
        bar_width = 50
        bar_height = 6
        
        x = self.rect.centerx - (bar_width // 2)
        y = self.rect.top - 15
        
        pygame.draw.rect(screen, RED, (x, y, bar_width, bar_height))
        pygame.draw.rect(screen, GREEN, (x, y, bar_width * ratio, bar_height))
        pygame.draw.rect(screen, WHITE, (x, y, bar_width, bar_height), 1)

        if self.triple_shot_timer > 0:
            power_ratio = self.triple_shot_timer / 7.0
            pygame.draw.rect(screen, YELLOW, (x, y - 8, bar_width * power_ratio, 4))