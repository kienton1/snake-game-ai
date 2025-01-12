import pygame
import random
from enum import Enum
from collections import namedtuple
import numpy as np

pygame.init()
font = pygame.font.Font('arial.ttf', 25)


# font = pygame.font.SysFont('arial', 25)

class Direction(Enum):
    RIGHT = 1
    LEFT = 2
    UP = 3
    DOWN = 4

#Point is a data structure that is used to represent a 2D point with x and y coords/ Used to define the position of the
    #snake or the position of the food
Point = namedtuple('Point', 'x, y')

# rgb colors
WHITE = (255, 255, 255)
RED = (200, 0, 0)
BLUE1 = (0, 0, 255)
BLUE2 = (0, 100, 255)
BLACK = (0, 0, 0)

BLOCK_SIZE = 20
SPEED = 200

class SnakeGameAI:

    def __init__(self, w=640, h=480):
        #self.w/ self.h sets the game window width and height for the environment/game
        self.w = w
        self.h = h
        # init display
        self.display = pygame.display.set_mode((self.w, self.h))
        #This sets the window title
        pygame.display.set_caption('Snake AI with RL')
        #This starts a clock to control the game's frame rate
        self.clock = pygame.time.Clock()
        #This resets the game state of the snake, the apple, the direction, the score, ect more on this later.
        self.reset()


    def reset(self):
        # init game state and points the snake to the RIGHT to start
        self.direction = Direction.RIGHT

        #Sets the head of the snake in the middle of the game when reset
        self.head = Point(self.w / 2, self.h / 2)

        #This is the list that is created to instantiate the snake with the head in the middle and the two blocks to the
        #left being apart of the body. This will be appended to to increase the legnth of the snake.
        self.snake = [self.head,
                      Point(self.head.x - BLOCK_SIZE, self.head.y),
                      Point(self.head.x - (2 * BLOCK_SIZE), self.head.y)]
        #This resets that score back to 0
        self.score = 0
        #This is a placeholder for the food which is later handled by th _place_food.
        self.food = None

        self._place_food()

        #This tracks te number of frames since the last action which will be used to detect inactivity
        self.frame_iteration = 0


    def _place_food(self):
        #This generates a random a and y coordinate for the food to be places when this function is called
        x = random.randint(0, (self.w - BLOCK_SIZE) // BLOCK_SIZE) * BLOCK_SIZE
        y = random.randint(0, (self.h - BLOCK_SIZE) // BLOCK_SIZE) * BLOCK_SIZE
        self.food = Point(x, y)
        #This if statement checks if the food is within the list snake and if it is then it recursively calls this
        #function to ensure that the food is not being placed in the snake.
        if self.food in self.snake:
            self._place_food()

    def play_step(self, action):
        #This increments the frame counter to track the games progress.
        self.frame_iteration += 1
        # 1. collect user input
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

        # 2. move this updates the head of the snake
        self._move(action)  # update the head
        #This inserts the new head position at the beginning of the self.snake head to make it seem like the snake is
        #slithering and it also moves the snake to the next point that the snake it directed to.
        self.snake.insert(0, self.head)

        # 3. check if game over
        reward = 0
        game_over = False
        #This ends the game if the snake collides with the wall or if the snake collides with anything within self.snake
        #list
        if self.is_collision() or self.frame_iteration > 100*len(self.snake):
            game_over = True
            #The AI gets -10 points if it dies or the game resets which is the same thing
            reward = - 10
            return reward, game_over, self.score

        # 4. place new food or just move
        #For every frame iteration, if the head cord is the same as the cord of food then the score increases by 1
        if self.head == self.food:
            self.score += 1
            #It is important to keep the positive reward similar to the negative reward becuase if the two are different
            #then the snake will go to food at all cost with no consideration of its danger status.
            reward = 10
            #If the food is touching the snake then _place_food() is called to create another food in the game.
            self._place_food()
        else:
            #Because at the beginning of this function we are going to insert a new cord in the self.snake list we have
            #to remove the last element to give the impression that we are moving forward.
            self.snake.pop()

        # 5. update ui and clock
        self._update_ui()
        #Speed is defined in the beginning of this file.
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

    def _update_ui(self):
        self.display.fill(BLACK)

        for pt in self.snake:
            pygame.draw.rect(self.display, BLUE1, pygame.Rect(pt.x, pt.y, BLOCK_SIZE, BLOCK_SIZE))
            pygame.draw.rect(self.display, BLUE2, pygame.Rect(pt.x + 4, pt.y + 4, 12, 12))

        pygame.draw.rect(self.display, RED, pygame.Rect(self.food.x, self.food.y, BLOCK_SIZE, BLOCK_SIZE))

        text = font.render("Score: " + str(self.score), True, WHITE)
        self.display.blit(text, [0, 0])
        pygame.display.flip()
    #self refers to the instance of the SnakeGameAI class and then action represents the movement decisions that the AI
    #makes with [1, 0, 0] coninuing straight, [0, 1, 0] turning right and, [0, 0, 1] turning left.
    def _move(self, action):
        #We need a list for clock_wise function because in coorelation to the snake facing up and down and left and
        #and right can be different
        clock_wise = [Direction.RIGHT, Direction.DOWN, Direction.LEFT, Direction.UP]
        #This find the index of the currect direction within the clock_wise list
        #It works by first getting th direction of the snake which we labeled with an enum in the beginning of this file.
        idx = clock_wise.index(self.direction)
        #np.Array_equal checks if two arrays are equal and the action array is a list that is given from the agent and
        #the second array is the array that we set to go straight ie the snake does nothing when action is [1, 0, 0]
        if np.array_equal(action, [1, 0, 0]):
            new_dir = clock_wise[idx]
        #Same explaination but this is when the action is [0, 1, 0] which would be to move
        elif np.array_equal(action, [0, 1, 0]):
            #next_idx moves to the next direction int he clockwise list ie the snake is going right in coorelation to
            #where the snake is facing. the %4 ensures that the index wraps around meaning that index of 4 goes back to
            #index of 0
            next_idx = (idx + 1) % 4
            new_dir = clock_wise[next_idx]
        else:
            #last option is to go left which is left of the clockwise list.
            next_idx = (idx - 1) % 4
            new_dir = clock_wise[next_idx]
        #This sets the direction of the snake to the new clockwise direction of the snake in coorelation to the snakes
        #pre-existing direction.
        self.direction = new_dir
        #This retrieves the current x and y cords of the snake's head and it will be used to update the new direction
        x = self.head.x
        y = self.head.y
        #if new direction is right then we increase x cord, if left decrease x, if up increase y, if down decrease y
        if self.direction == Direction.RIGHT:
            x += BLOCK_SIZE
        elif self.direction == Direction.LEFT:
            x -= BLOCK_SIZE
        elif self.direction == Direction.DOWN:
            y += BLOCK_SIZE
        elif self.direction == Direction.UP:
            y -= BLOCK_SIZE
        #This creates a new Point object for the snake's head using the updates x and y cords
        self.head = Point(x, y)

