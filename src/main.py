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
        active_player = self.db.get_active_player()
        
        # Nếu chưa có thông tin người chơi -> Chuyển vào màn nhập tên New Pilot
        # Nếu đã có -> Chuyển thẳng vào Menu và hiện "Welcome Back"
        if active_player is None:
            self.state = NameInputState(self)
        else:
            self.state = MenuState(self)

    def change_state(self, new_state):
        self.state = new_state

    def run(self):
        while True:
            dt = self.clock.tick(FPS) / 1000.0
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
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