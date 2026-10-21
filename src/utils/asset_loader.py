import pygame
import os

def load_image(filename, scale_to=None):
    """
    Tải ảnh từ thư mục assets/images/
    scale_to: Một tuple (width, height) nếu muốn đổi kích thước ảnh.
    """
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__))) 
    path = os.path.join(base_dir, 'assets', 'images', filename)
    
    try:
        image = pygame.image.load(path).convert_alpha()
        if scale_to:
            image = pygame.transform.scale(image, scale_to)
        return image
    except (pygame.error, FileNotFoundError) as e:
        print(f"Không thể tải ảnh: {path}. Lỗi: {e}")
        # Trả về cục màu hồng để game không bị crash nếu thiếu ảnh
        fallback = pygame.Surface((64, 64))
        fallback.fill((255, 0, 255)) 
        return fallback