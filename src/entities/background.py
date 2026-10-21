# src/entities/background.py
import pygame
from utils.asset_loader import load_image

class Background:
    def __init__(self, game):
        self.game = game
        
        # Tải ảnh nền gốc (hỗ trợ .png hoặc .jpg tùy bạn đặt trong assets)
        try:
            self.image = load_image('bg.png')
        except:
            try:
                self.image = load_image('bg.jpg')
            except:
                # Fallback nếu không tìm thấy ảnh
                self.image = pygame.Surface((1024, 512))
                self.image.fill((10, 15, 25))

        self.width = self.image.get_width()
        self.height = self.image.get_height()
        
        # Biến lưu vị trí cuộn dọc
        self.scroll_y = 0

    def update(self, dt):
        # Tự động cuộn hình nền xuống dưới tạo cảm giác tàu đang tiến lên
        self.scroll_y += 60 * dt 

    def draw(self, screen):
        screen_w = self.game.current_width
        screen_h = self.game.current_height
        
        # Tính phần dư để ảnh lặp lại mượt mà, chống lộ đường kẻ seam bằng cách bù trừ 1-2 pixel
        offset_y = self.scroll_y % self.height
        
        # Dùng vòng lặp vẽ lặp ảnh ra toàn màn hình
        for x in range(0, screen_w, self.width):
            for y in range(-self.height, screen_h + self.height, self.height):
                screen.blit(self.image, (x, y + offset_y))