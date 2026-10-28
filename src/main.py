import pygame
import sys
from settings import *
from utils.db_manager import DatabaseManager
from states.menu_state import MenuState
from states.name_input_state import NameInputState

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
        pygame.display.set_caption("Space Shooter 2.5D")
        self.clock = pygame.time.Clock()
        
        self.current_width = SCREEN_WIDTH
        self.current_height = SCREEN_HEIGHT
        
        self.db = DatabaseManager()
        
        # Tải Tiền xu và Cấp độ Nâng cấp lưu từ SQLite
        self.coins, self.upgrades = self.db.get_player_upgrades()
        
        active_player = self.db.get_active_player()
        
        if active_player is None:
            self.state = NameInputState(self)
        else:
            self.state = MenuState(self)

    def change_state(self, new_state):
        # Lưu dữ liệu nâng cấp và tiền mỗi khi chuyển màn chơi/State
        self.db.save_player_upgrades(self.coins, self.upgrades)
        self.state = new_state

    def run(self):
        while True:
            dt = self.clock.tick(FPS) / 1000.0
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    # Lưu dữ liệu vào CSDL trước khi thoát game
                    self.db.save_player_upgrades(self.coins, self.upgrades)
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.VIDEORESIZE:
                    self.current_width, self.current_height = event.w, event.h
                    self.screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
                
                self.state.handle_events(event)

            self.state.update(dt)
            self.state.draw(self.screen)
            pygame.display.flip()

if __name__ == "__main__":
    game = Game()
    game.run()