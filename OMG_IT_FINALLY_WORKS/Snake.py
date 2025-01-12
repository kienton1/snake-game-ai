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

ARENA_WIDTH = 32
ARENA_HEIGHT = 24
ARENA_SIZE = ARENA_WIDTH * ARENA_HEIGHT


class SnakeGame:
    def __init__(self, w=640, h=480):
        self.w = w
        self.h = h
        self.display = pygame.display.set_mode((self.w, self.h))
        pygame.display.set_caption('Snake AI')
        self.clock = pygame.time.Clock()

        self.direction = Direction.RIGHT
        self.head = Point(self.w // 2, self.h // 2)
        self.snake = [self.head,
                      Point(self.head.x - BLOCK_SIZE, self.head.y),
                      Point(self.head.x - (2 * BLOCK_SIZE), self.head.y)]

        self.score = 0
        self.food = None
        self._place_food()

        self.maze = Maze()
        self.maze.generate()

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

        # Move
        self._move(self._ai_get_new_direction())

        # Check if game over
        game_over = False
        if self._is_collision():
            game_over = True
            return game_over, self.score

        # Place new food or move
        if self.head == self.food:
            self.score += 1
            self._place_food()
        else:
            self.snake.pop()

        # Update UI and clock
        self._update_ui()
        self.clock.tick(SPEED)

        return game_over, self.score

    def _is_collision(self):
        if (self.head.x > self.w - BLOCK_SIZE or self.head.x < 0 or
                self.head.y > self.h - BLOCK_SIZE or self.head.y < 0):
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
        self.snake.insert(0, self.head)

    def _ai_get_new_direction(self):
        x = self.head.x // BLOCK_SIZE
        y = self.head.y // BLOCK_SIZE
        path_number = self.maze.get_path_number(x, y)
        distance_to_food = self.maze.path_distance(path_number, self.maze.get_path_number(self.food.x // BLOCK_SIZE,
                                                                                          self.food.y // BLOCK_SIZE))
        distance_to_tail = self.maze.path_distance(path_number,
                                                   self.maze.get_path_number(self.snake[-1].x // BLOCK_SIZE,
                                                                             self.snake[-1].y // BLOCK_SIZE))

        cutting_amount_available = distance_to_tail - len(self.snake) - 3
        num_empty_squares = ARENA_SIZE - len(self.snake) - 1

        if num_empty_squares < ARENA_SIZE // 2:
            cutting_amount_available = 0
        elif distance_to_food < distance_to_tail:
            cutting_amount_available -= 1
            if (distance_to_tail - distance_to_food) * 4 > num_empty_squares:
                cutting_amount_available -= 10

        cutting_amount_desired = distance_to_food
        cutting_amount_available = min(cutting_amount_available, cutting_amount_desired)
        cutting_amount_available = max(cutting_amount_available, 0)

        directions = [Direction.RIGHT, Direction.LEFT, Direction.DOWN, Direction.UP]
        best_dir = None
        best_dist = -1

        for dir in directions:
            new_x, new_y = x, y
            if dir == Direction.RIGHT:
                new_x += 1
            elif dir == Direction.LEFT:
                new_x -= 1
            elif dir == Direction.DOWN:
                new_y += 1
            elif dir == Direction.UP:
                new_y -= 1

            if self._is_valid_move(new_x, new_y):
                dist = self.maze.path_distance(path_number, self.maze.get_path_number(new_x, new_y))
                if dist <= cutting_amount_available and dist > best_dist:
                    best_dir = dir
                    best_dist = dist

        return best_dir if best_dir else Direction.RIGHT

    def _is_valid_move(self, x, y):
        if x < 0 or y < 0 or x >= ARENA_WIDTH or y >= ARENA_HEIGHT:
            return False
        return Point(x * BLOCK_SIZE, y * BLOCK_SIZE) not in self.snake


class Maze:
    def __init__(self):
        self.nodes = [[{'visited': False, 'can_go_right': False, 'can_go_down': False} for _ in range(ARENA_WIDTH // 2)]
                      for _ in range(ARENA_HEIGHT // 2)]
        self.tour_to_number = [[0 for _ in range(ARENA_WIDTH)] for _ in range(ARENA_HEIGHT)]

    def generate(self):
        self._generate_r(-1, -1, 0, 0)
        self._generate_tour_number()

    def _generate_r(self, from_x, from_y, x, y):
        if x < 0 or y < 0 or x >= ARENA_WIDTH // 2 or y >= ARENA_HEIGHT // 2:
            return
        if self.nodes[y][x]['visited']:
            return

        self.nodes[y][x]['visited'] = True

        if from_x != -1:
            if from_x < x:
                self.nodes[from_y][from_x]['can_go_right'] = True
            elif from_x > x:
                self.nodes[y][x]['can_go_right'] = True
            elif from_y < y:
                self.nodes[from_y][from_x]['can_go_down'] = True
            elif from_y > y:
                self.nodes[y][x]['can_go_down'] = True

        directions = [(0, -1), (0, 1), (-1, 0), (1, 0)]
        random.shuffle(directions)

        for dx, dy in directions:
            self._generate_r(x, y, x + dx, y + dy)

    def _generate_tour_number(self):
        x, y = 0, 0
        start_dir = Direction.UP if self._can_go_down(x, y) else Direction.LEFT
        dir = start_dir
        number = 0

        while number < ARENA_SIZE:
            next_dir = self._find_next_dir(x, y, dir)

            if dir == Direction.RIGHT:
                self._set_tour_number(x * 2, y * 2, number)
                number += 1
                if next_dir in [Direction.RIGHT, Direction.DOWN, Direction.LEFT]:
                    self._set_tour_number(x * 2 + 1, y * 2, number)
                    number += 1
                if next_dir in [Direction.DOWN, Direction.LEFT]:
                    self._set_tour_number(x * 2 + 1, y * 2 + 1, number)
                    number += 1
                if next_dir == Direction.LEFT:
                    self._set_tour_number(x * 2, y * 2 + 1, number)
                    number += 1
            elif dir == Direction.DOWN:
                self._set_tour_number(x * 2 + 1, y * 2, number)
                number += 1
                if next_dir in [Direction.DOWN, Direction.LEFT, Direction.UP]:
                    self._set_tour_number(x * 2 + 1, y * 2 + 1, number)
                    number += 1
                if next_dir in [Direction.LEFT, Direction.UP]:
                    self._set_tour_number(x * 2, y * 2 + 1, number)
                    number += 1
                if next_dir == Direction.UP:
                    self._set_tour_number(x * 2, y * 2, number)
                    number += 1
            elif dir == Direction.LEFT:
                self._set_tour_number(x * 2 + 1, y * 2 + 1, number)
                number += 1
                if next_dir in [Direction.LEFT, Direction.UP, Direction.RIGHT]:
                    self._set_tour_number(x * 2, y * 2 + 1, number)
                    number += 1
                if next_dir in [Direction.UP, Direction.RIGHT]:
                    self._set_tour_number(x * 2, y * 2, number)
                    number += 1
                if next_dir == Direction.RIGHT:
                    self._set_tour_number(x * 2 + 1, y * 2, number)
                    number += 1
            elif dir == Direction.UP:
                self._set_tour_number(x * 2, y * 2 + 1, number)
                number += 1
                if next_dir in [Direction.UP, Direction.RIGHT, Direction.DOWN]:
                    self._set_tour_number(x * 2, y * 2, number)
                    number += 1
                if next_dir in [Direction.RIGHT, Direction.DOWN]:
                    self._set_tour_number(x * 2 + 1, y * 2, number)
                    number += 1
                if next_dir == Direction.DOWN:
                    self._set_tour_number(x * 2 + 1, y * 2 + 1, number)
                    number += 1

            dir = next_dir
            if dir == Direction.RIGHT:
                x += 1
            elif dir == Direction.LEFT:
                x -= 1
            elif dir == Direction.DOWN:
                y += 1
            elif dir == Direction.UP:
                y -= 1

    def _find_next_dir(self, x, y, dir):
        if dir == Direction.RIGHT:
            if self._can_go_up(x, y): return Direction.UP
            if self._can_go_right(x, y): return Direction.RIGHT
            if self._can_go_down(x, y): return Direction.DOWN
            return Direction.LEFT
        elif dir == Direction.DOWN:
            if self._can_go_right(x, y): return Direction.RIGHT
            if self._can_go_down(x, y): return Direction.DOWN
            if self._can_go_left(x, y): return Direction.LEFT
            return Direction.UP
        elif dir == Direction.LEFT:
            if self._can_go_down(x, y): return Direction.DOWN
            if self._can_go_left(x, y): return Direction.LEFT
            if self._can_go_up(x, y): return Direction.UP
            return Direction.RIGHT
        elif dir == Direction.UP:
            if self._can_go_left(x, y): return Direction.LEFT
            if self._can_go_up(x, y): return Direction.UP
            if self._can_go_right(x, y): return Direction.RIGHT
            return Direction.DOWN

    def _can_go_right(self, x, y):
        return self.nodes[y][x]['can_go_right']

    def _can_go_down(self, x, y):
        return self.nodes[y][x]['can_go_down']

    def _can_go_left(self, x, y):
        return x > 0 and self.nodes[y][x - 1]['can_go_right']

    def _can_go_up(self, x, y):
        return y > 0 and self.nodes[y - 1][x]['can_go_down']

    def _set_tour_number(self, x, y, number):
        if self.tour_to_number[y][x] != 0:
            return
        self.tour_to_number[y][x] = number

    def get_path_number(self, x, y):
        return self.tour_to_number[y][x]

    def path_distance(self, a, b):
        if a < b:
            return b - a - 1
        return b - a - 1 + ARENA_SIZE


if __name__ == '__main__':
    game = SnakeGame()

    while True:
        game_over, score = game.play_step()

        if game_over:
            break

    print('Final Score', score)

    pygame.quit()
