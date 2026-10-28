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

        # --- LẤY CHỈ SỐ NÂNG CẤP TỪ GAME ---
        upgrades = getattr(self.game, 'upgrades', {'hp': 0, 'damage': 0, 'speed': 0, 'shield': 0})
        
        self.max_hp = PLAYER_HP + upgrades['hp'] * 20
        self.hp = self.max_hp
        
        self.max_shield = 50 + upgrades['shield'] * 15
        self.shield = 0  # Giáp ban đầu bằng 0, nhặt item để nạp

        self.speed = PLAYER_SPEED + upgrades['speed'] * 25
        self.bullet_damage = 10 + upgrades['damage'] * 5

        self.angle = 0
        self.shoot_cooldown = 0.15 
        self.shoot_timer = 0
        self.triple_shot_timer = 0

    def take_damage(self, amount):
        """Khấu trừ Giáp trước khi trừ Máu"""
        if self.shield > 0:
            if self.shield >= amount:
                self.shield -= amount
            else:
                remaining_damage = amount - self.shield
                self.shield = 0
                self.hp -= remaining_damage
        else:
            self.hp -= amount
            
        if self.hp < 0:
            self.hp = 0

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

        # Giới hạn khung hình
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
        s = self.game.get_scale_factor() if hasattr(self.game, 'get_scale_factor') else 1.0
        local_offset = pygame.math.Vector2(0, 22 * s)
        rotated_offset = local_offset.rotate(-self.angle)
        trail_pos = self.pos + rotated_offset
        
        flame_len = random.randint(18, 28) * s
        tip_offset = pygame.math.Vector2(0, flame_len).rotate(-self.angle)
        tip_pos = trail_pos + tip_offset
        
        left_wing_offset = pygame.math.Vector2(-8 * s, 0).rotate(-self.angle)
        right_wing_offset = pygame.math.Vector2(8 * s, 0).rotate(-self.angle)
        
        p1 = trail_pos + left_wing_offset
        p2 = trail_pos + right_wing_offset
        p3 = tip_pos
        
        trail_surf = pygame.Surface((int(70 * s), int(70 * s)), pygame.SRCALPHA)
        center_surf = pygame.math.Vector2(35 * s, 35 * s)
        lp1 = center_surf + (p1 - trail_pos)
        lp2 = center_surf + (p2 - trail_pos)
        lp3 = center_surf + (p3 - trail_pos)
        
        pygame.draw.polygon(trail_surf, (0, 220, 255, 180), [lp1, lp2, lp3])
        surface.blit(trail_surf, (trail_pos.x - 35 * s, trail_pos.y - 35 * s))

    def draw_shield(self, surface):
        """Vẽ hiệu ứng Vòng giáp bảo vệ khi shield > 0"""
        if self.shield > 0:
            s = self.game.get_scale_factor() if hasattr(self.game, 'get_scale_factor') else 1.0
            padding = int(18 * s)
            shield_w = self.rect.width + padding
            shield_h = self.rect.height + padding
            shield_surf = pygame.Surface((shield_w, shield_h), pygame.SRCALPHA)
            
            alpha = int(100 + (self.shield / self.max_shield) * 120)
            color = (0, 180, 255, alpha)
            
            center = (shield_w // 2, shield_h // 2)
            radius = int(max(self.rect.width, self.rect.height) // 2 + 6 * s)
            pygame.draw.circle(shield_surf, color, center, radius, max(1, int(3 * s)))
            pygame.draw.circle(shield_surf, (0, 150, 255, 30), center, radius)
            
            surface.blit(shield_surf, (self.rect.centerx - shield_w // 2, self.rect.centery - shield_h // 2))

    def rotate(self):
        mouse_x, mouse_y = pygame.mouse.get_pos()
        rel_x = mouse_x - self.pos.x
        rel_y = mouse_y - self.pos.y
        
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
            
            if self.triple_shot_timer > 0:
                for angle in [0, -15, 15]:
                    b = Bullet(spawn_x, spawn_y, direction.rotate(angle), self.bullet_groups, game=self.game)
                    b.damage = self.bullet_damage
            else:
                b = Bullet(spawn_x, spawn_y, direction, self.bullet_groups, game=self.game)
                b.damage = self.bullet_damage
            
            if hasattr(self.game.state, 'sound_manager'):
                self.game.state.sound_manager.play('laser')

            self.shoot_timer = self.shoot_cooldown

    def draw(self, surface):
        self.draw_engine_trail(surface)
        surface.blit(self.image, self.rect)
        self.draw_shield(surface)

    def draw_health(self, screen):
        ratio = max(0, self.hp / self.max_hp)
        bar_width = 50
        bar_height = 6
        
        x = self.rect.centerx - (bar_width // 2)
        y = self.rect.top - 18
        
        pygame.draw.rect(screen, RED, (x, y, bar_width, bar_height))
        pygame.draw.rect(screen, GREEN, (x, y, bar_width * ratio, bar_height))
        pygame.draw.rect(screen, WHITE, (x, y, bar_width, bar_height), 1)

        if self.shield > 0:
            sh_ratio = max(0, self.shield / self.max_shield)
            pygame.draw.rect(screen, (30, 30, 30), (x, y - 6, bar_width, 4))
            pygame.draw.rect(screen, (0, 180, 255), (x, y - 6, bar_width * sh_ratio, 4))

        if self.triple_shot_timer > 0:
            power_ratio = self.triple_shot_timer / 7.0
            offset_y = 12 if self.shield > 0 else 6
            pygame.draw.rect(screen, YELLOW, (x, y - offset_y, bar_width * power_ratio, 4))