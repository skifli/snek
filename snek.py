import os
import random
import sys
import termios
import time
import tty
from typing import List, Dict, Optional
import select
import signal

import colorama


colorama.init()

# Constants
CHARS = {"full_shade": "\u2588", "medium_shade": "\u2592"}
CHAR_WIDTH = 2
INITIAL_SNAKE_LENGTH = 1
INITIAL_SCORE = 1
INITIAL_HIGH_SCORE = 1
GRID_HEIGHT_OFFSET = (
    4  # Offset for the grid height (terminal.lines - GRID_HEIGHT_OFFSET)
)
GRID_WIDTH_OFFSET = (
    2  # Offset for the grid width ((terminal.columns // 2) - GRID_WIDTH_OFFSET)
)
APPLE_DENSITY = 100  # Adjust for apple density (grid_area // APPLE_DENSITY)
MIN_APPLES = 1  # Minimum number of apples
SNAKE_GROWTH_RATE = 1  # Number of segments added when eating an apple
SNAKE_MOVE_DELAY = 0.25  # Delay between snake movements (in seconds)
APPLE_SPACING = 3  # Minimum distance between apples and snake/other apples

# Configurable variables (can be changed programmatically)
config = {
    "apple_density": APPLE_DENSITY,
    "initial_snake_length": INITIAL_SNAKE_LENGTH,
    "snake_growth_rate": SNAKE_GROWTH_RATE,
    "snake_move_delay": SNAKE_MOVE_DELAY,
    "apple_spacing": APPLE_SPACING,
}


class Snake:
    def __init__(self, world: "GameWorld") -> None:
        """Initialize the Snake object."""
        self.world = world
        self.vertices: List[Dict[str, int]] = []
        self.score = INITIAL_SCORE
        self.high_score = INITIAL_HIGH_SCORE
        self.direction = "RIGHT"
        self.last_direction = "RIGHT"
        self.growth_queue: List[Dict[str, int]] = []

        # Initialize the snake with the correct length
        start_x = self.world.width // 2
        start_y = self.world.height // 2
        for i in range(config["initial_snake_length"]):
            self.vertices.append({"x": start_x - i, "y": start_y})

    def reset(self) -> None:
        """Reset the snake to its initial state."""
        self.vertices = []
        self.score = INITIAL_SCORE
        self.direction = "RIGHT"
        self.last_direction = "RIGHT"
        self.growth_queue = []

        # Initialize the snake with the correct length
        start_x = self.world.width // 2
        start_y = self.world.height // 2
        for i in range(config["initial_snake_length"]):
            self.vertices.append({"x": start_x - i, "y": start_y})

    def update_direction(self, char: Optional[str]) -> bool:
        """Update the direction of the snake based on input character."""
        if char is not None:
            last_direction = self.direction

            if char == "w" and last_direction != "DOWN":
                self.direction = "UP"
            elif char == "s" and last_direction != "UP":
                self.direction = "DOWN"
            elif char == "a" and last_direction != "RIGHT":
                self.direction = "LEFT"
            elif char == "d" and last_direction != "LEFT":
                self.direction = "RIGHT"

            if last_direction != self.direction:
                self.last_direction = last_direction
                return True  # Direction changed

        return False  # Direction unchanged


class Apples:
    def __init__(self, world: "GameWorld") -> None:
        """Initialize the Apples object."""
        self.world = world
        self.vertices: List[Dict[str, int]] = []
        self.calculate_initial_apples()

    def calculate_initial_apples(self) -> None:
        """Calculate the initial number of apples based on the grid area."""
        grid_area = self.world.width * self.world.height
        self.num_apples = max(MIN_APPLES, grid_area // config["apple_density"])
        self.reset()

    def reset(self) -> None:
        """Reset the apples to their initial state."""
        self.vertices = []
        for _ in range(self.num_apples):
            self.add_apple()

    def add_apple(self) -> None:
        """Add a new apple to the grid."""
        attempts = 0
        while attempts < 100:  # Limit attempts to avoid infinite loops
            new_apple = {
                "x": random.randrange(0, self.world.width),
                "y": random.randrange(0, self.world.height),
            }

            if self.is_position_valid(new_apple):
                self.vertices.append(new_apple)
                if (
                    0 <= new_apple["y"] < self.world.height
                    and 0 <= new_apple["x"] < self.world.width
                ):
                    self.world.grid[new_apple["y"]][new_apple["x"]] = "A"
                break
            attempts += 1

    def is_position_valid(self, position: Dict[str, int]) -> bool:
        """Check if the position is valid for placing an apple."""
        for vertex in self.world.snake.vertices:
            if (
                abs(vertex["x"] - position["x"]) < config["apple_spacing"]
                and abs(vertex["y"] - position["y"]) < config["apple_spacing"]
            ):
                return False

        for apple in self.vertices:
            if (
                abs(apple["x"] - position["x"]) < config["apple_spacing"]
                and abs(apple["y"] - position["y"]) < config["apple_spacing"]
            ):
                return False

        return True


class GameWorld:
    def __init__(self) -> None:
        """Initialize the GameWorld object."""
        self.terminal = os.get_terminal_size()
        self.height = self.terminal.lines - GRID_HEIGHT_OFFSET
        self.width = (self.terminal.columns // CHAR_WIDTH) - GRID_WIDTH_OFFSET
        self.grid: List[List[str]] = []
        self.last_update = time.perf_counter()
        self.updating = False

        self.initialize_grid()

        self.snake = Snake(self)
        self.apples = Apples(self)

        self.reset_world()

        # Handle terminal resizing
        signal.signal(signal.SIGWINCH, self.handle_resize)

    def initialize_grid(self) -> None:
        """Initialize the grid with empty values."""
        self.grid = [["" for _ in range(self.width)] for _ in range(self.height)]

    def clear_terminal(self) -> None:
        """Clear the terminal screen."""
        os.system("cls" if os.name == "nt" else "clear")

    def move_cursor_to_top(self) -> None:
        """Move the cursor to the top of the terminal."""
        print(f"\033[{self.terminal.lines}A\033[2K", end="")

    def print_world(self, print_score: bool = True) -> None:
        """Print the current state of the game world."""
        self.move_cursor_to_top()
        print(f"\r{CHARS['full_shade']*self.terminal.columns}", end="\r\n")

        if print_score:
            score_string = f"Score: {self.snake.score}"
            high_score_string = f"High Score: {self.snake.high_score}"
            print(
                f"{CHARS['full_shade']*CHAR_WIDTH}{score_string}{CHARS['full_shade']*CHAR_WIDTH}{high_score_string}{(CHARS['full_shade'] * (self.terminal.columns - GRID_HEIGHT_OFFSET - len(score_string) - len(high_score_string)))}",
                end="\r\n",
            )
        else:
            print(f"\r{CHARS['full_shade']*self.terminal.columns}", end="\r\n")

        print(f"\r{CHARS['full_shade']*self.terminal.columns}", end="\r\n")

        for row in self.grid:
            print(f"{CHARS['full_shade']*CHAR_WIDTH}", end="")
            print(
                "".join(
                    [
                        (
                            f"{colorama.Fore.RED}{CHARS['full_shade']*2}{colorama.Fore.RESET}"
                            if entity in ["A", "S"]  # Apple / Snake
                            else (
                                f"{colorama.Fore.GREEN}{CHARS['full_shade']*2}{colorama.Fore.RESET}"
                                if entity == "H"  # Snake Head
                                else CHARS["medium_shade"] * 2
                            )
                        )
                        for entity in row
                    ]
                ),
                end="",
            )
            print(
                f"{CHARS['full_shade']*(2 if self.terminal.columns % 2 == 0 else 3)}",
                end="\r\n",
            )

        print(f"\r{CHARS['full_shade']*self.terminal.columns}", end="")

    def vertex_in_world(self, vertex: Dict[str, int]) -> bool:
        """Check if a vertex is within the bounds of the world."""
        return (vertex["x"] >= 0 and vertex["x"] < self.width) and (
            vertex["y"] >= 0 and vertex["y"] < self.height
        )

    def reset_world(self) -> None:
        """Reset the game world to its initial state."""
        self.updating = False
        self.last_update = time.perf_counter()

        # Clear the grid
        self.initialize_grid()

        # Reset the snake and apples
        self.snake.reset()
        self.apples.reset()

        # Place the snake head on the grid
        if (
            0 <= self.snake.vertices[0]["y"] < self.height
            and 0 <= self.snake.vertices[0]["x"] < self.width
        ):
            self.grid[self.snake.vertices[0]["y"]][self.snake.vertices[0]["x"]] = "H"

    def update_world(self) -> None:
        """Update the game world state."""
        if self.updating:
            return

        self.updating = True
        last_vertex = None

        # Move the snake
        for index, vertex in enumerate(self.snake.vertices):
            if 0 <= vertex["y"] < self.height and 0 <= vertex["x"] < self.width:
                self.grid[vertex["y"]][vertex["x"]] = ""

            if last_vertex is not None:
                self.snake.vertices[index], last_vertex = last_vertex, vertex.copy()
            else:
                last_vertex = vertex.copy()
                vertex["x"] += (
                    1
                    if self.snake.direction == "RIGHT"
                    else -1 if self.snake.direction == "LEFT" else 0
                )
                vertex["y"] += (
                    1
                    if self.snake.direction == "DOWN"
                    else -1 if self.snake.direction == "UP" else 0
                )

                if not self.vertex_in_world(vertex):
                    self.reset_world()
                    break

        # Check for apple collisions
        for vertex in self.snake.vertices:
            if vertex in self.apples.vertices:
                self.apples.vertices.remove(vertex)
                self.snake.score += config["snake_growth_rate"]

                if self.snake.score > self.snake.high_score:
                    self.snake.high_score = self.snake.score

                # Add new vertices to the growth queue
                for _ in range(config["snake_growth_rate"]):
                    self.snake.growth_queue.append(last_vertex.copy())

                self.apples.add_apple()

        # Handle snake growth
        while self.snake.growth_queue:
            self.snake.vertices.append(self.snake.growth_queue.pop(0))

        # Update the grid with the new snake positions
        snake_length = len(self.snake.vertices)
        for index, vertex in enumerate(self.snake.vertices[::-1]):
            if 0 <= vertex["y"] < self.height and 0 <= vertex["x"] < self.width:
                self.grid[vertex["y"]][vertex["x"]] = (
                    "H" if index == snake_length - 1 else "S"
                )

            if index == snake_length - 1:
                if vertex in self.snake.vertices[1:]:
                    self.reset_world()
                    return self.update_world()

        self.print_world()

        self.updating = False
        self.last_update = time.perf_counter()

    def handle_resize(self, _signum: int, _frame: Optional[object]) -> None:
        """Handle terminal resize events."""
        # Update terminal size and grid dimensions
        self.terminal = os.get_terminal_size()
        self.height = self.terminal.lines - GRID_HEIGHT_OFFSET
        self.width = (self.terminal.columns // 2) - GRID_WIDTH_OFFSET

        # Reinitialize the grid
        self.initialize_grid()

        # Reposition the snake and apples
        self.reset_world()

    def start_game(self) -> None:
        """Start the game loop."""
        self.clear_terminal()

        while True:
            if time.perf_counter() - self.last_update > config["snake_move_delay"]:
                self.update_world()

            char = getchar()
            if char:  # If a key is pressed
                if self.snake.update_direction(char):  # Update snake direction
                    self.update_world()  # Immediately update the world if direction changes


def getchar() -> Optional[str]:
    """Get a single character from standard input."""
    if select.select([sys.stdin], [], [], 0.0)[0]:
        return sys.stdin.read(1)
    return None


def main() -> None:
    """Main function to start the game."""
    fd = sys.stdin.fileno()
    attr = termios.tcgetattr(fd)

    tty.setraw(fd)

    world = GameWorld()
    world.start_game()

    termios.tcsetattr(fd, termios.TCSANOW, attr)


if __name__ == "__main__":
    main()
