import pygame
import random
from enum import Enum
from collections import namedtuple

pygame.init()
font = pygame.font.Font('arial.ttf', 25)

class Direction(Enum):
    RIGHT = 1
    LEFT = 2
    UP = 3
    DOWN = 4

Point = namedtuple('Point', 'x, y')

# rgb colors
WHITE = (255, 255, 255)
RED = (200, 0, 0)
BLUE1 = (0, 0, 255)
BLUE2 = (0, 100, 255)
BLACK = (0, 0, 0)

BLOCK_SIZE = 20
SPEED = 20

class SnakeGame:

    def __init__(self, w=640, h=480):
        self.w = w
        self.h = h
        self.display = pygame.display.set_mode((self.w, self.h))
        pygame.display.set_caption('Snake')
        self.clock = pygame.time.Clock()
        self.direction = Direction.RIGHT
        self.head = Point(self.w / 2, self.h / 2)
        self.snake = [self.head,
                      Point(self.head.x - BLOCK_SIZE, self.head.y),
                      Point(self.head.x - (2 * BLOCK_SIZE), self.head.y)]
        self.score = 0
        self.food = None
        self._place_food()
        self.speed_multiplier = 1

    def _place_food(self):
        x = random.randint(0, (self.w - BLOCK_SIZE) // BLOCK_SIZE) * BLOCK_SIZE
        y = random.randint(0, (self.h - BLOCK_SIZE) // BLOCK_SIZE) * BLOCK_SIZE
        self.food = Point(x, y)
        if self.food in self.snake:
            self._place_food()

    def play_step(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    self.speed_multiplier = min(10, self.speed_multiplier * 10)
                elif event.key == pygame.K_a:
                    self.speed_multiplier = max(0.1, self.speed_multiplier / 10)

        self.snake.pop()
        self._move(self.direction)
        self.snake.insert(0, self.head)

        game_over = False
        if self._is_collision():
            game_over = True
            return game_over, self.score

        if self.head == self.food:
            self.score += 1
            self._place_food()
            self.snake.append(Point(self.snake[-1].x, self.snake[-1].y))

        self._update_ui()
        self.clock.tick(SPEED * self.speed_multiplier)
        return game_over, self.score

    def _is_collision(self):
        if self.head.x > self.w - BLOCK_SIZE or self.head.x < 0 or \
                self.head.y > self.h - BLOCK_SIZE or self.head.y < 0:
            return True
        if self.head in self.snake[1:]:
            return True
        return False

    def _update_ui(self):
        self.display.fill(BLACK)

        for pt in self.snake:
            pygame.draw.rect(self.display, BLUE1, pygame.Rect(pt.x, pt.y, BLOCK_SIZE, BLOCK_SIZE))
            pygame.draw.rect(self.display, BLUE2, pygame.Rect(pt.x + 4, pt.y + 4, 12, 12))

        pygame.draw.rect(self.display, RED, pygame.Rect(self.food.x, self.food.y, BLOCK_SIZE, BLOCK_SIZE))

        text = font.render("Score: " + str(self.score), True, WHITE)
        self.display.blit(text, [0, 0])
        pygame.display.flip()

    def _move(self, direction):
        x = self.head.x
        y = self.head.y
        if direction == Direction.RIGHT:
            x += BLOCK_SIZE
        elif direction == Direction.LEFT:
            x -= BLOCK_SIZE
        elif direction == Direction.DOWN:
            y += BLOCK_SIZE
        elif direction == Direction.UP:
            y -= BLOCK_SIZE

        self.head = Point(x, y)

class SafeHamiltonianAI:
    def __init__(self, game):
        self.game = game
        self.hamiltonian_cycle = self.generate_hamiltonian_cycle()

    def generate_hamiltonian_cycle(self):
        width = self.game.w // BLOCK_SIZE
        height = self.game.h // BLOCK_SIZE
        cycle = [[0] * width for _ in range(height)]

        def dfs(x, y, count):
            if count == width * height:
                return True
            for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                nx, ny = x + dx, y + dy
                if 0 <= nx < width and 0 <= ny < height and cycle[ny][nx] == 0:
                    cycle[ny][nx] = count + 1
                    if dfs(nx, ny, count + 1):
                        return True
                    cycle[ny][nx] = 0
            return False

        cycle[0][0] = 1
        dfs(0, 0, 1)
        return cycle

    def get_next_move(self):
        head = self.game.snake[0]
        x = int(head.x // BLOCK_SIZE)
        y = int(head.y // BLOCK_SIZE)
        current_index = self.hamiltonian_cycle[y][x]
        next_index = (current_index % (self.game.w * self.game.h // BLOCK_SIZE ** 2)) + 1

        for dy in range(self.game.h // BLOCK_SIZE):
            for dx in range(self.game.w // BLOCK_SIZE):
                if self.hamiltonian_cycle[dy][dx] == next_index:
                    next_point = Point(dx * BLOCK_SIZE, dy * BLOCK_SIZE)
                    return self.get_direction(head, next_point)

        print("ERROR: No valid move found. This should not happen.")
        return self.game.direction

    def get_direction(self, from_point, to_point):
        if to_point.x > from_point.x:
            return Direction.RIGHT
        elif to_point.x < from_point.x:
            return Direction.LEFT
        elif to_point.y > from_point.y:
            return Direction.DOWN
        else:
            return Direction.UP

if __name__ == '__main__':
    game = SnakeGame()
    ai = SafeHamiltonianAI(game)

    while True:
        next_direction = ai.get_next_move()
        game.direction = next_direction
        game_over, score = game.play_step()

        if game_over:
            break

    print('Final Score', score)

    pygame.quit()
