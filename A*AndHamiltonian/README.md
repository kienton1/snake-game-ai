---

## Overview

This project is a modern implementation of the classic Snake game, written in Python using the **Pygame** library. It features:

- A **basic Snake game** with food placement and increasing difficulty.
- An **Improved AI system** with Hamiltonian Cycle navigation and A* search for efficient decision-making.
- A modular and extensible codebase for further enhancements.

## Summary:
This code uses both A*, hamiltonian cycle, and a survival mode to keep the snake alive. The A* works in a way that the snake uses a modified A* where the snake calculates if the A* path to the apple exists and if the A* path to the apples 
results in the snake being able to reach 80% of the grid after reaching the apple to try to ensure that the snake doesn't trap itself just to get the apple. On the late game the snake relies more on the hamiltonian cycle to ensure that the snake plays it safe
when more squares in the grid are danger squares. During the calculation of A*, if the snake can not find a path that follows the requirements of A* then the snake will enter a survival mode where the snake will wonder around trying not to die until an A* path is found to the next apple.

---

## Requirements

- **Python 3.7+**
- **Pygame Library**

Install Pygame using pip:
```bash
pip install pygame
```

---

## How to Run

1. Clone the repository or copy the code to your local machine.
2. Run the Python script:
   ```bash
   python snake_game.py
   ```

3. Use the arrow keys to control the snake's movement.

---

## Game Features

- **Dynamic Gameplay:** The snake grows as it eats food, and the game ends when the snake collides with itself or the walls.
- **Customizable Settings:** Change the game window dimensions, block size, or speed by modifying the `SnakeGame` class's initialization parameters.
- **Real-Time UI Updates:** Displays the current score and visually distinct snake segments.

---

## AI Features

### Hamiltonian Cycle
- The AI uses a precomputed Hamiltonian Cycle to navigate the grid efficiently, ensuring the snake always has a path to follow.

### A* Search Algorithm
- The AI employs an A* algorithm to find the shortest path to the food while considering the snake's length and grid constraints.
- Integrates reachability checks to ensure that the snake doesn't trap itself.

### Safety Checks
- The AI ensures that any move made keeps the snake safe from collisions and maximizes reachable squares.

---

## Code Structure

- **`SnakeGame` Class:** 
  - Core gameplay mechanics (snake movement, food placement, collision detection).
  - UI updates and event handling.

- **`ImprovedAI` Class:** 
  - Implements Hamiltonian Cycle and A* search for optimal gameplay.
  - Contains utility functions for safe move checks, pathfinding, and grid traversal.

---

## Future Enhancements

- **Adaptive Difficulty:** Adjust game speed and AI decision-making based on score.
- **Multiplayer Mode:** Add support for two-player gameplay.
- **Enhanced AI:** Integrate machine learning techniques for dynamic decision-making.
- **Level Variations:** Introduce obstacles and dynamic game environments.

---

## This code does not work because the A* is too greedy and although this is the coolest looking algorithm, this code results in an average of 90 to 100 score as the snake will trap itself in the mid to late game
