from ball import Ball
from board import *
from multis import *
from settings import *
import ctypes, pygame, pymunk, random, sys
import json

# Json fájl beolvasása
def load_gift_data(filename="gift_data.json"):
    try:
        with open(filename, "r", encoding="utf-8") as json_file:
            data = json.load(json_file)
        return data
    except FileNotFoundError:
        return []
    
def save_to_json(data, filename="gift_data.json"):
    with open(filename, "w", encoding="utf-8") as json_file:
        json.dump(data, json_file, ensure_ascii=False, indent=2)

# Maintain resolution regardless of Windows scaling settings
ctypes.windll.user32.SetProcessDPIAware()

class Game:
    def __init__(self):
        # General setup
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption(TITLE_STRING)
        self.clock = pygame.time.Clock()
        self.delta_time = 0

        # Pymunk
        self.space = pymunk.Space()
        self.space.gravity = (0, 1800)

        # Plinko setup
        self.ball_group = pygame.sprite.Group()
        self.board = Board(self.space)

        # Debugging
        self.balls_played = 0

    def run(self):
        # Load gift data
        gift_data = load_gift_data()

        self.start_time = pygame.time.get_ticks()

        while True:
            # Handle quit operation
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    # Get the position of the mouse click
                    mouse_pos = pygame.mouse.get_pos()

                    # Check if the mouse click position collides with the image rectangle
                    if self.board.play_rect.collidepoint(mouse_pos):
                        self.board.pressing_play = True
                    else:
                        self.board.pressing_play = False
                # Spawn ball on left mouse button release
                elif event.type == pygame.MOUSEBUTTONUP and event.button == 1 and self.board.pressing_play:
                    mouse_pos = pygame.mouse.get_pos()
                    if self.board.play_rect.collidepoint(mouse_pos):
                        random_x = WIDTH//2 + random.choice([random.randint(-20, -1), random.randint(1, 20)])
                        click.play()
                        self.ball = Ball((random_x, 20), self.space, self.board, self.delta_time)
                        self.ball_group.add(self.ball)
                        self.board.pressing_play = False
                    else:
                        self.board.pressing_play = False

            self.screen.fill(BG_COLOR)

            # Time variables
            self.delta_time = self.clock.tick(FPS) / 1000.0

            # Pymunk
            self.space.step(self.delta_time)
            self.board.update()
            self.ball_group.update()

            # Check for unplayed gifts and launch balls
            for data in gift_data:
                if not data["participated_in_game"]:
                    random_x = WIDTH//2 + random.choice([random.randint(-20, -1), random.randint(1, 20)])
                    user_id = data["user_id"]

                    # Csak indítsuk el a labdát, ha az adott felhasználó még nem játszott
                    if user_id not in [ball.user_id for ball in self.ball_group]:
                        ball = Ball((random_x, 20), self.space, self.board, self.delta_time, user_id)
                        self.ball_group.add(ball)
                        data["participated_in_game"] = True

                        # Mentsd el az adatokat a frissített állapottal
                        save_to_json(gift_data)

            pygame.display.update()

if __name__ == '__main__':
    game = Game()
    game.run()