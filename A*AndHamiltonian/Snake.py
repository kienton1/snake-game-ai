import pygame
import random
from enum import Enum
from collections import namedtuple
import heapq

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

        # Remove the tail before updating the head
        self.snake.pop()

        # Move the head
        self._move(self.direction)
        self.snake.insert(0, self.head)

        game_over = False
        if self._is_collision():
            game_over = True
            return game_over, self.score

        if self.head == self.food:
            self.score += 1
            self._place_food()
            # Add a new segment to the snake
            self.snake.append(Point(self.snake[-1].x, self.snake[-1].y))

        self._update_ui()
        self.clock.tick(SPEED)
        return game_over, self.score

    def _is_collision(self):
        if self.head.x > self.w - BLOCK_SIZE or self.head.x < 0 or \
                self.head.y > self.h - BLOCK_SIZE or self.head.y < 0:
            print("Found a Wall")
            return True
        if self.head in self.snake[1:-1]:
            print("Found Myself")
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

        self.head = Point(int(x), int(y))


class ImprovedAI:
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

    def is_safe_move(self, next_head, snake):
        if next_head.x < 0 or next_head.x >= self.game.w or \
                next_head.y < 0 or next_head.y >= self.game.h:
            return False
        if next_head in snake[:-1]:
            return False
        return True

    def get_next_move(self):
        head = self.game.snake[0]
        food = self.game.food
        snake_length = len(self.game.snake)
        total_squares = (self.game.w // BLOCK_SIZE) * (self.game.h // BLOCK_SIZE)

        if snake_length < total_squares * 0.3:
            path = self.a_star(head, food, self.game.snake)
            if path and self.can_reach_tail(path[-1], self.game.snake):
                print("Using A*")
                return self.get_direction(head, path[1])

        print("Using Hamilton")
        return self.follow_hamiltonian_cycle()

    def a_star(self, start, goal, snake):
        def heuristic(a, b, snake_length):
            manhattan_distance = abs(a.x - b.x) + abs(a.y - b.y)
            return manhattan_distance + (snake_length // 10)

        def get_neighbors(point, snake):
            neighbors = []
            for dx, dy in [(0, BLOCK_SIZE), (BLOCK_SIZE, 0), (0, -BLOCK_SIZE), (-BLOCK_SIZE, 0)]:
                new_point = Point(point.x + dx, point.y + dy)
                if self.is_safe_move(new_point, snake):
                    neighbors.append(new_point)
            return neighbors

        def can_reach_percentage(position, snake, threshold=0.8):
            total_squares = (self.game.w // BLOCK_SIZE) * (self.game.h // BLOCK_SIZE)
            empty_squares = total_squares - len(snake)
            reachable_squares = self.count_reachable_squares(position, snake)
            return reachable_squares / empty_squares >= threshold

        open_set = []
        heapq.heappush(open_set, (0, start))
        came_from = {}
        g_score = {start: 0}
        f_score = {start: heuristic(start, goal, len(snake))}

        while open_set:
            current = heapq.heappop(open_set)[1]

            if current == goal:
                path = []
                while current in came_from:
                    path.append(current)
                    current = came_from[current]
                path.append(start)
                path = path[::-1]

                # Check if the path allows the snake to reach at least 80% of empty squares
                if can_reach_percentage(path[-1], snake):
                    return path
                else:
                    continue  # Discard this path and continue searching

            for neighbor in get_neighbors(current, snake):
                tentative_g_score = g_score[current] + BLOCK_SIZE

                if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    f_score[neighbor] = g_score[neighbor] + heuristic(neighbor, goal, len(snake))
                    heapq.heappush(open_set, (f_score[neighbor], neighbor))

        return None

    def count_reachable_squares(self, position, snake):
        visited = set()
        stack = [position]
        count = 0

        while stack:
            current = stack.pop()
            if current not in visited and self.is_safe_move(current, snake):
                visited.add(current)
                count += 1
                for dx, dy in [(0, BLOCK_SIZE), (BLOCK_SIZE, 0), (0, -BLOCK_SIZE), (-BLOCK_SIZE, 0)]:
                    stack.append(Point(current.x + dx, current.y + dy))

        return count

    def can_reach_tail(self, position, snake):
        visited = set()
        stack = [position]
        tail = snake[-1]

        while stack:
            current = stack.pop()
            if current == tail:
                return True
            if current not in visited and self.is_safe_move(current, snake):
                visited.add(current)
                for dx, dy in [(0, BLOCK_SIZE), (BLOCK_SIZE, 0), (0, -BLOCK_SIZE), (-BLOCK_SIZE, 0)]:
                    stack.append(Point(current.x + dx, current.y + dy))
        return False

    def follow_hamiltonian_cycle(self):
        head = self.game.snake[0]
        x = max(0, min(int(head.x // BLOCK_SIZE), (self.game.w // BLOCK_SIZE) - 1))
        y = max(0, min(int(head.y // BLOCK_SIZE), (self.game.h // BLOCK_SIZE) - 1))
        current_index = self.hamiltonian_cycle[y][x]
        next_index = (current_index % (self.game.w * self.game.h // BLOCK_SIZE ** 2)) + 1

        # Always find the next point in the Hamiltonian cycle
        for dy in range(self.game.h // BLOCK_SIZE):
            for dx in range(self.game.w // BLOCK_SIZE):
                if self.hamiltonian_cycle[dy][dx] == next_index:
                    next_point = Point(dx * BLOCK_SIZE, dy * BLOCK_SIZE)
                    if self.is_safe_move(next_point, self.game.snake):
                        return self.get_direction(head, next_point)

        # If the next point in the cycle is not safe, look for any safe adjacent move
        for direction in [Direction.RIGHT, Direction.LEFT, Direction.UP, Direction.DOWN]:
            next_point = self.get_next_point(head, direction)
            if self.is_safe_move(next_point, self.game.snake):
                return direction

        # If no safe move is found, this should never happen in a valid Hamiltonian cycle
        print("ERROR: No safe move found. This should not happen.")
        return self.game.direction

    def get_next_point(self, head, direction):
        if direction == Direction.RIGHT:
            return Point(head.x + BLOCK_SIZE, head.y)
        elif direction == Direction.LEFT:
            return Point(head.x - BLOCK_SIZE, head.y)
        elif direction == Direction.UP:
            return Point(head.x, head.y - BLOCK_SIZE)
        elif direction == Direction.DOWN:
            return Point(head.x, head.y + BLOCK_SIZE)

    def get_direction(self, from_point, to_point):
        if to_point.x > from_point.x:
            return Direction.RIGHT
        elif to_point.x < from_point.x:
            return Direction.LEFT
        elif to_point.y > from_point.y:
            return Direction.DOWN
        else:
            return Direction.UP

    def chase_tail(self):
        head = self.game.snake[0]
        tail = self.game.snake[-1]
        path = self.a_star(head, tail, self.game.snake[:-1])
        if path:
            return self.get_direction(head, path[1])
        return self.follow_hamiltonian_cycle()


if __name__ == '__main__':
    game = SnakeGame()
    ai = ImprovedAI(game)

    while True:
        next_direction = ai.get_next_move()
        game.direction = next_direction
        game_over, score = game.play_step()

        if game_over:
            break

    print('Final Score', score)

    pygame.quit()
