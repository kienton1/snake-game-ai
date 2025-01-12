---

# Snake Game with Safe Hamiltonian AI

This project is a Python implementation of the classic Snake game, enhanced with an AI player that uses a safe Hamiltonian cycle to guide the snake's movement. The AI ensures the snake follows a predetermined cycle that avoids collisions, making it virtually unbeatable
The code has no calculations or care for where the apples are spawned in. By representing each coordinate or square as a vertex, we can use a hamiltonian cycle to ensure that the snake never visits one node twice per cycle. This means that the snake will follow the same cycle
over and over again without deviating from it the ensure its safety. The snake doesn't try to find the apple but more so the apple is just on one of the vertex that the snake will pass ever once and a while while it follws the cycle.

## Features
- **Classic Snake Gameplay**: Move the snake to collect food and grow while avoiding collisions.
- **Dynamic Speed Control**: Adjust game speed in real time using `Q` and `A` keys.
- **Safe Hamiltonian AI**: An AI module that calculates a Hamiltonian cycle to navigate the snake safely.
- **Customizable Game Settings**: Modify game window dimensions, snake speed, and block size.

## Requirements
- Python 3.7 or higher
- `pygame` library

Install `pygame` using:
```bash
pip install pygame
```

---

## Setup and Installation
1. Clone this repository or download the script file.
2. Ensure `arial.ttf` is in the same directory for text rendering.
3. Run the script using Python.

---

## Gameplay Instructions
- **Start the Game**: The snake will begin moving automatically, controlled by the AI.
- **Adjust Speed**:
  - Press `Q` to increase the game speed by 10x.
  - Press `A` to decrease the game speed to 1/10th of its current value.
- **Game Objective**: Collect food (red blocks) to grow the snake and increase your score.
- **Game Over**: The game ends if the snake collides with itself or the wall.

---

## Code Overview
### 1. **SnakeGame Class**
Handles the game mechanics, rendering, and input handling.
- **Attributes**:
  - `w`, `h`: Window dimensions.
  - `snake`: List representing the snake's body.
  - `food`: Coordinates of the food.
  - `speed_multiplier`: Adjusts the game speed.
- **Methods**:
  - `_place_food`: Randomly places food on the grid.
  - `play_step`: Processes game logic for each frame.
  - `_is_collision`: Checks for collisions.
  - `_update_ui`: Renders the game window and updates the score.
  - `_move`: Moves the snake based on the current direction.

### 2. **SafeHamiltonianAI Class**
Implements the AI logic using a Hamiltonian cycle.
- **Attributes**:
  - `hamiltonian_cycle`: A 2D list representing the cycle for safe navigation.
- **Methods**:
  - `generate_hamiltonian_cycle`: Recursively computes the cycle.
  - `get_next_move`: Determines the next move based on the current position.
  - `get_direction`: Converts a position into a direction (up, down, left, right).

### 3. **Direction Enum**
Defines constants for snake movement: `UP`, `DOWN`, `LEFT`, and `RIGHT`.

### 4. **Constants**
- `BLOCK_SIZE`: Size of each grid cell.
- `SPEED`: Base game speed.
- RGB color codes for snake, food, and background.

---

## AI Logic Explanation
The **Safe Hamiltonian AI** uses a Hamiltonian cycle, ensuring the snake visits every grid cell exactly once before repeating. 
- The cycle is computed using a depth-first search (DFS) algorithm.
- The AI determines the snake's next move based on the cycle's sequence, avoiding collisions and ensuring safety even as the snake grows.

This approach guarantees the snake can continue indefinitely unless the board's dimensions make the cycle generation impossible.

---

## How to Run
1. Run the script:
   ```bash
   python snake_game.py
   ```
2. Watch as the AI controls the snake to collect food and grow.

---

## Customization
You can modify the following attributes for different gameplay experiences:
- **Window Dimensions**:
  Change the `w` and `h` parameters in the `SnakeGame` constructor.
- **Speed**:
  Adjust the `SPEED` constant or use `Q` and `A` keys during the game.
- **Block Size**:
  Change the `BLOCK_SIZE` constant for larger or smaller grid cells.

---

## Acknowledgments
- **Pygame**: A powerful library for game development in Python.
- **Inspiration**: The classic Snake game and its endless variations.

--- 

**This code is not the finished product and will the the bases of the finisheed project as the finsihed project uses a modified version of this hamiltonian cycle.**

