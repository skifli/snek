import colorama, os, pynput, random, time, typing

colorama.init()

terminal = os.get_terminal_size()

CHARS: typing.Final[dict] = {"full_shade": "\u2588", "medium_shade": "\u2592"}

world = {
    "grid": [],
    "height": terminal.lines - 4,
    "width": (terminal.columns // 2) - 2,
    "last_update": time.perf_counter(),
    "updating": False,
}

snake = {
    "vertices": [{"x": 0, "y": 0}],
    "score": 1,
    "high_score": 1,
    "direction": "RIGHT",
    "last_direction": "RIGHT",
}

apples = {
    "vertices": [
        {
            "x": random.randrange(0, world["width"]),
            "y": random.randrange(0, world["height"]),
        }
    ],
}

world["grid"] = [
    ["" for _ in range(world["width"])] for _ in range(world["height"])
]  # Create grid

world["grid"][snake["vertices"][0]["y"]][
    snake["vertices"][0]["x"]
] = "H"  # Add initial snake to grid
world["grid"][apples["vertices"][0]["y"]][
    apples["vertices"][0]["x"]
] = "A"  # Add initial apple to grid

def clear_terminal() -> None:
    os.system(
        "cls" if os.name == "nt" else "clear"
    )  # Clear the terminal to get a clear screen to print the world to
    
def move_cursor_to_top() -> None:
    print(f"\033[{terminal.lines}A\033[2K", end="")

def print_world(print_score: bool=True) -> None:
    move_cursor_to_top()
    print(f"\r{CHARS['full_shade']*terminal.columns}")
    
    if print_score:
        SCORE_STRING: typing.Final[str] = f"Score: {snake['score']}"
        HIGH_SCORE_STRING: typing.Final[str] = f"High Score: {snake['high_score']}"
        print(
            f"{CHARS['full_shade']*2}{SCORE_STRING}{CHARS['full_shade']*2}{HIGH_SCORE_STRING}{(CHARS['full_shade'] * (terminal.columns - 4 - len(SCORE_STRING) - len(HIGH_SCORE_STRING)))}"
        )
    else:
        print(f"\r{CHARS['full_shade']*terminal.columns}")      
        
    print(f"\r{CHARS['full_shade']*terminal.columns}")

    for row in world["grid"]:
        print(f"{CHARS['full_shade']*2}", end="")
        print(
            "".join(
                [
                    f"{colorama.Fore.RED}{CHARS['full_shade']*2}{colorama.Fore.RESET}"
                    if entity in ["A", "S"]  # Apple / Snake
                    else f"{colorama.Fore.GREEN}{CHARS['full_shade']*2}{colorama.Fore.RESET}"
                    if entity == "H"  # Snake Head
                    else CHARS["medium_shade"] * 2
                    for entity in row
                ]
            ),
            end="",
        )
        print(f"{CHARS['full_shade']*(2 if terminal.columns % 2 == 0 else 3)}")

    print(f"\r{CHARS['full_shade']*terminal.columns}", end="")


def vertex_in_world(vertex) -> bool:
    return (vertex["x"] >= 0 and vertex["x"] < world["width"]) and (
        vertex["y"] >= 0 and vertex["y"] < world["height"]
    )


def restart_world(full_reset: typing.Optional[bool] = True) -> None:
    world["updating"] = False
    world["last_update"] = time.perf_counter()

    for vertex in apples["vertices"]:
        if vertex_in_world(vertex):
            # Remove all previous apple vertices from the world
            world["grid"][vertex["y"]][vertex["x"]] = ""

    for vertex in snake["vertices"]:
        if vertex_in_world(vertex):
            # Remove all previous snake vertices from the world
            world["grid"][vertex["y"]][vertex["x"]] = ""

    snake["vertices"] = [{"x": -1 if full_reset else 0, "y": 0}]  # Reset snake
    snake["score"] = 1
    snake["direction"] = "RIGHT"
    snake["last_direction"] = "RIGHT"

    apples["vertices"] = [
        {
            "x": random.randrange(0, world["width"]),
            "y": random.randrange(0, world["height"]),
        }
    ]  # Reset apples

    world["grid"][apples["vertices"][0]["y"]][
        apples["vertices"][0]["x"]
    ] = "A"  # Add apple to grid

    world["grid"][snake["vertices"][0]["y"]][
        snake["vertices"][0]["x"]
    ] = "A"  # Add snake to grid


def update_world() -> None:
    if world["updating"]:
        return

    world["updating"] = True
    last_vertex = None

    for index, vertex in enumerate(snake["vertices"]):
        world["grid"][vertex["y"]][vertex["x"]] = ""

        if last_vertex is not None:
            snake["vertices"][index], last_vertex = last_vertex, vertex.copy()
        else:
            last_vertex = vertex.copy()

            vertex["x"] += (
                1
                if snake["direction"] == "RIGHT"
                else -1
                if snake["direction"] == "LEFT"
                else 0
            )

            vertex["y"] += (
                1
                if snake["direction"] == "DOWN"
                else -1
                if snake["direction"] == "UP"
                else 0
            )

            if not vertex_in_world(vertex):
                restart_world(False)

                break

    for vertex in snake["vertices"]:
        if vertex in apples["vertices"]:
            apples["vertices"].remove(vertex)  # Remove *eaten* apple from the world.

            for _ in range(2):
                new_apple = {
                    "x": random.randrange(0, world["width"]),
                    "y": random.randrange(0, world["height"]),
                }

                apples["vertices"].append(new_apple)
                world["grid"][new_apple["y"]][new_apple["x"]] = "A"

            snake["score"] += 1

            if snake["score"] > snake["high_score"]:  # New high score
                snake["high_score"] = snake["score"]

            snake["vertices"].append(last_vertex)

    snake_length = len(snake["vertices"])

    for index, vertex in enumerate(snake["vertices"][::-1]):
        world["grid"][vertex["y"]][vertex["x"]] = (
            "H" if index == snake_length - 1 else "S"
        )

        if index == snake_length - 1:
            if vertex in snake["vertices"][1:]:
                restart_world()
                return update_world()

    print_world()

    world["updating"] = False
    world["last_update"] = time.perf_counter()


def update_snake_direction(
    key: typing.Union[pynput.keyboard.Key, pynput.keyboard.KeyCode]
) -> None:
    try:
        char = key.char
    except AttributeError:
        char = key

    last_direction = snake["direction"]

    if char in ["w", pynput.keyboard.Key.up]:
        snake["direction"] = "UP"
    elif char in ["s", pynput.keyboard.Key.down]:
        snake["direction"] = "DOWN"
    elif char in ["a", pynput.keyboard.Key.left]:
        snake["direction"] = "LEFT"
    elif char in ["d", pynput.keyboard.Key.right]:
        snake["direction"] = "RIGHT"

    if last_direction != snake["direction"]:
        snake["last_direction"] = last_direction
        update_world()

def start_game() -> None:
    pynput.keyboard.Listener(on_press=update_snake_direction).start()
    clear_terminal()

    while True:
        if time.perf_counter() - world["last_update"] > 0.25:
            update_world()

start_game()