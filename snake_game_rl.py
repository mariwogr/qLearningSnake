import pygame
import random
from enum import Enum
from collections import namedtuple

pygame.init()
font = pygame.font.Font('arial.ttf', 25)
#font = pygame.font.SysFont('arial', 25)
    
Point = namedtuple('Point', 'x, y')

# rgb colors
WHITE = (255, 255, 255)
RED = (200,0,0)
BLUE1 = (0, 0, 255)
BLUE2 = (0, 100, 255)
BLACK = (0,0,0)

BLOCK_SIZE = 20
# SPEED = 20000000
SPEED = 20

class SnakeGameRL:
    
    def __init__(self, w=640, h=480):
        self.w = w
        self.h = h
        # init display
        self.display = pygame.display.set_mode((self.w, self.h))
        pygame.display.set_caption('Snake')
        self.clock = pygame.time.Clock()

        self.reset()
        
    def reset(self):
        # init game state
        self.direction = random.randint(0,3)
        
        self.head = Point(int(self.w/2), int(self.h/2))
        self.snake = [self.head, 
                      Point(self.head.x-BLOCK_SIZE, self.head.y),
                      Point(self.head.x-(2*BLOCK_SIZE), self.head.y),
                      Point(self.head.x-(3*BLOCK_SIZE), self.head.y),
                      Point(self.head.x-(4*BLOCK_SIZE), self.head.y),
                      Point(self.head.x-(5*BLOCK_SIZE), self.head.y),
                      Point(self.head.x-(6*BLOCK_SIZE), self.head.y)
                     ]
        
        self.score = 0
        self.food = None
        self._place_food()
        self.frame_iteration = 0
        
    def _place_food(self):
        x = random.randint(0, (self.w-BLOCK_SIZE )//BLOCK_SIZE )*BLOCK_SIZE 
        y = random.randint(0, (self.h-BLOCK_SIZE )//BLOCK_SIZE )*BLOCK_SIZE
        self.food = Point(x, y)
        if self.food in self.snake:
            self._place_food()

    def is_there_a_wall(self):

        wall_x = False
        wall_y = False

        head_x = self.head.x
        head_y = self.head.y

        if self.food.x < self.head.x: 
            # food left
            for i in range(head_x, self.food.x, -BLOCK_SIZE):
                if Point(i, head_y) in self.snake[1:]:
                    wall_x = True
                    break
        elif self.food.x > self.head.x:
            # food right
            for i in range(head_x, self.food.x, BLOCK_SIZE):
                if Point(i, head_y) in self.snake[1:]:
                    wall_x = True
                    break
        if self.food.y < self.head.y: # food up
            for i in range(head_y, self.food.y, -BLOCK_SIZE):
                if Point(head_x, i) in self.snake[1:]:
                    wall_y = True
                    break
        elif self.food.y > self.head.y: 
            # food down
            for i in range(head_y, self.food.y, BLOCK_SIZE):
                if Point(head_x, i) in self.snake[1:]:
                    wall_y = True
                    break

        return [wall_x, wall_y]
        
    def play_step(self, action):

        self.frame_iteration += 1

        # 1. collect user input
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
        
        # 2. move
        self._move(action) # update the head
        self.snake.insert(0, self.head)
        
        # 3. check if game over + calculate reward
        reward = 0
        game_over = False
        if self.is_collision(): # or self.frame_iteration > 100*len(self.snake):
            game_over = True
            reward = -10
            return reward, game_over, self.score
            
        # 4. place new food or just move
        if self.head == self.food:
            self.score += 1
            reward = 10
            self._place_food()
        else:
            self.snake.pop()
        
        # 5. update ui and clock
        self._update_ui()
        self.clock.tick(SPEED)
        # 6. return game over and score
        return reward, game_over, self.score
    
    def is_collision(self, pt=None):
        if pt is None:
            pt = self.head
        # hits boundary
        if pt.x > self.w - BLOCK_SIZE or pt.x < 0 or pt.y > self.h - BLOCK_SIZE or pt.y < 0:
            return True
        # hits itself
        if pt in self.snake[1:]:
            return True

        return False


    def danger(self):
        """ The agent will be looking at its direction and it will be looking if there is a collision or danger at front, right and/or left itself"""

        if self.direction == 0:
            collision_front = self.head.x > self.w - BLOCK_SIZE or Point(self.head.x + BLOCK_SIZE, self.head.y) in self.snake[1:]
            collision_left = self.head.y <= 0 or Point(self.head.x, self.head.y - BLOCK_SIZE) in self.snake[1:]
            collision_right = self.head.y > self.h - BLOCK_SIZE or Point(self.head.x, self.head.y + BLOCK_SIZE) in self.snake[1:]
        elif self.direction == 1:
            collision_front = self.head.x  <= 0 or Point(self.head.x - BLOCK_SIZE, self.head.y) in self.snake[1:]
            collision_left = self.head.y > self.h - BLOCK_SIZE or Point(self.head.x, self.head.y + BLOCK_SIZE) in self.snake[1:]
            collision_right = self.head.y <= 0 or Point(self.head.x, self.head.y - BLOCK_SIZE) in self.snake[1:]
        elif self.direction == 2:
            collision_front = self.head.y > self.h - BLOCK_SIZE or Point(self.head.x, self.head.y + BLOCK_SIZE) in self.snake[1:]
            collision_left = self.head.x > self.w - BLOCK_SIZE or Point(self.head.x + BLOCK_SIZE, self.head.y) in self.snake[1:]
            collision_right = self.head.x  <= 0 or Point(self.head.x - BLOCK_SIZE, self.head.y) in self.snake[1:]
        else:
            collision_front = self.head.y <= 0 or Point(self.head.x, self.head.y - BLOCK_SIZE) in self.snake[1:]
            collision_left = self.head.x  <= 0 or Point(self.head.x - BLOCK_SIZE, self.head.y) in self.snake[1:]
            collision_right = self.head.x > self.w - BLOCK_SIZE or Point(self.head.x + BLOCK_SIZE, self.head.y) in self.snake[1:]
        
        return [collision_front, collision_left, collision_right]
        
    def _update_ui(self):
        self.display.fill(BLACK)
        
        for pt in self.snake:
            pygame.draw.rect(self.display, BLUE1, pygame.Rect(pt.x, pt.y, BLOCK_SIZE, BLOCK_SIZE))
            pygame.draw.rect(self.display, BLUE2, pygame.Rect(pt.x+4, pt.y+4, 12, 12))
            
        pygame.draw.rect(self.display, RED, pygame.Rect(self.food.x, self.food.y, BLOCK_SIZE, BLOCK_SIZE))
        
        text = font.render("Score: " + str(self.score), True, WHITE)
        self.display.blit(text, [0, 0])
        pygame.display.flip()
        
    def _move(self, action):
        x = self.head.x
        y = self.head.y

        self.direction = action

        if self.direction == 0:
            x += BLOCK_SIZE
        elif self.direction == 1:
            x -= BLOCK_SIZE
        elif self.direction == 2:
            y += BLOCK_SIZE
        elif self.direction == 3:
            y -= BLOCK_SIZE
            
        self.head = Point(x, y)