import pygame
import os

class SoundManager:
    def __init__(self):
        try:
            pygame.mixer.init()
        except pygame.error:
            print("Không thể khởi tạo sound mixer.")

        self.sounds = {}
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        self.sounds_dir = os.path.join(base_dir, 'assets', 'sounds')

        # Khai báo các file hiệu ứng âm thanh (SFX)
        self.load_sound('laser', 'fire sound.wav')
        self.load_sound('victory', 'level_victory.wav')
        self.load_sound('pickup_health', 'pickup_health_heal_chi.wav')
        self.load_sound('pickup_shield', 'pickup_shield.wav')
        self.load_sound('pickup_triple', 'pickup_tripleshoot_weapon.wav')
        self.load_sound('explosion', 'explosion.wav')
        self.load_sound('hit', 'hit.wav')

    def load_sound(self, name, filename):
        path = os.path.join(self.sounds_dir, filename)
        if os.path.exists(path):
            try:
                sound = pygame.mixer.Sound(path)
                sound.set_volume(0.4)
                self.sounds[name] = sound
            except pygame.error:
                self.sounds[name] = None
        else:
            self.sounds[name] = None

    def play(self, name):
        """Phát âm thanh hiệu ứng. Riêng 'laser' (tiếng súng) dùng Channel(1) riêng biệt 
           để không bị ngắt quãng hoặc xung đột khi giữ chuột bắn liên tục."""
        if name in self.sounds and self.sounds[name]:
            if name == 'laser':
                channel = pygame.mixer.Channel(1)
                channel.play(self.sounds[name])
            else:
                self.sounds[name].play()

    def play_music(self, filename, volume=0.35, loops=-1):
        """Phát nhạc nền (BGM) từ thư mục assets/sounds/ với vòng lặp vô hạn"""
        path = os.path.join(self.sounds_dir, filename)
        if os.path.exists(path):
            try:
                pygame.mixer.music.load(path)
                pygame.mixer.music.set_volume(volume)
                pygame.mixer.music.play(loops=loops)
            except pygame.error as e:
                print(f"Lỗi khi phát nhạc nền {filename}: {e}")
        else:
            print(f"Không tìm thấy file nhạc nền tại: {path}")

    def stop_music(self):
        """Dừng nhạc nền"""
        pygame.mixer.music.stop()