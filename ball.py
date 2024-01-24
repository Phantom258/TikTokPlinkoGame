from multis import *
from obstacles import *
from settings import *
from PIL import Image, ImageDraw
import pygame, pymunk, random
import requests
from io import BytesIO

# URL megadása
image_url = "https://p16-sign-useast2a.tiktokcdn.com/tos-useast2a-avt-0068-euttp/a6e563c1f94a64b5c4a2998ac4f49bdb~c5_100x100.jpeg?lk3s=a5d48078&x-expires=1706302800&x-signature=tISOM4skLEeamwhaJgF1k%2FammTE%3D"

# Kép letöltése a hálózatról
response = requests.get(image_url)
image_data = BytesIO(response.content)

# Kép betöltése a Pygame segítségével
pygame.init()
image = pygame.image.load(image_data)

class Ball(pygame.sprite.Sprite):
    def __init__(self, pos, space, board, delta_time, user_id):
        super().__init__()
        self.display_surface = pygame.display.get_surface()
        self.space = space
        self.board = board
        self.delta_time = delta_time
        self.body = pymunk.Body(body_type = pymunk.Body.DYNAMIC)
        self.body.position = pos
        self.shape = pymunk.Circle(self.body, BALL_RAD)
        self.shape.elasticity = 0.9
        self.shape.density = 10000
        self.shape.mass = 1000
        self.shape.filter = pymunk.ShapeFilter(categories=BALL_CATEGORY, mask=BALL_MASK)
        self.space.add(self.body, self.shape)
        self.image = image
        self.rect = self.image.get_rect(topleft=(self.body.position.x, self.body.position.y))
        self.user_id = user_id

    def update(self):
        pos_x, pos_y = int(self.body.position.x), int(self.body.position.y)
        self.rect.centerx = pos_x
        self.rect.centery = pos_y

        # Check to see if ball hits obstacle
        for obstacle in self.board.obstacle_sprites:
            if pygame.sprite.collide_rect(self, obstacle):
                # Create animation and add to animation_group
                obstacle_centerx, obstacle_centery = obstacle.rect.centerx, obstacle.rect.centery
                obstacle_pos = (obstacle_centerx, obstacle_centery)

                for animating_obstacle in animation_group:
                    if obstacle_pos == animating_obstacle.coords:
                        animating_obstacle.kill()

                # Instantiate obstacle animation: params -> x, y, radius, color, delta_time
                obs_anim = AnimatedObstacle(obstacle_centerx, obstacle_centery, 16, (255, 255, 255), self.delta_time)
                animation_group.add(obs_anim)

        # Check to see if ball hits multi
        for multi in multi_group:
            if pygame.sprite.collide_rect(self, multi):
                multi.hit_sound()
                multipliers[str(multi.multi_amt)] += 1
                print(f"Total plays: {sum([val for val in multipliers.values()])} | {multipliers}")
                multi.animate(multi.color, multi.multi_amt)
                multi.is_animating = True

                # Display previous multi on right side of screen
                prev_rgb = multi.color
                prev_multi = PrevMulti(str(multi.multi_amt), prev_rgb)
                prev_multi_group.add(prev_multi)
                self.kill()
        
        # Draw red ball
        self.display_surface.blit(self.image, (pos_x, pos_y))