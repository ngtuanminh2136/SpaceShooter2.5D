import pygame
import os

class SoundManager:
    def __init__(self):
        # Khởi tạo bộ xử lý âm thanh của Pygame
        try:
            pygame.mixer.init()
        except pygame.error:
            print("Không thể khởi tạo sound mixer.")

        self.sounds = {}
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        self.sounds_dir = os.path.join(base_dir, 'assets', 'sounds')

        # Khai báo các file hiệu ứng âm thanh (SFX)
        self.load_sound('laser', 'laser.wav')
        self.load_sound('explosion', 'explosion.wav')
        self.load_sound('powerup', 'powerup.wav')
        self.load_sound('hit', 'hit.wav')

    def load_sound(self, name, filename):
        path = os.path.join(self.sounds_dir, filename)
        if os.path.exists(path):
            try:
                sound = pygame.mixer.Sound(path)
                sound.set_volume(0.4) # Âm lượng hiệu ứng (40%)
                self.sounds[name] = sound
            except pygame.error:
                self.sounds[name] = None
        else:
            self.sounds[name] = None

    def play(self, name):
        """Phát âm thanh hiệu ứng theo tên, nếu không có file thì tự bỏ qua"""
        if name in self.sounds and self.sounds[name]:
            self.sounds[name].play()

    def play_music(self, filename, volume=0.35, loops=-1):
        """Phát nhạc nền (BGM) từ thư mục assets/sounds/ với vòng lặp vô hạn"""
        path = os.path.join(self.sounds_dir, filename)
        if os.path.exists(path):
            try:
                pygame.mixer.music.load(path)
                pygame.mixer.music.set_volume(volume)
                pygame.mixer.music.play(loops=loops)
                print(f"Đang phát nhạc nền: {filename}")
            except pygame.error as e:
                print(f"Lỗi khi phát nhạc nền {filename}: {e}")
        else:
            print(f"Không tìm thấy file nhạc nền tại: {path}")

    def stop_music(self):
        """Dừng nhạc nền"""
        pygame.mixer.music.stop()