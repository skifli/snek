import colorama
import pynput
import time
import os
import random
import math
import typing

colorama.init()

terminal = os.get_terminal_size()

world_width = terminal.columns // 2 - 2
world_height = terminal.lines - 4

old_world = None
world_updating = False
world = [["" for _ in range(world_width)] for _ in range(world_height)]
world[0][0] = "*"

snake_data = {
    "vertices": [[0, 0]],
    "number": 1,
    "high_score": 1,
    "direction": "RIGHT",
    "last_direction": "RIGHT",
    "last_update": time.perf_counter(),
}

apple_data = {
    "vertices": [[random.randrange(0, world_width), random.randrange(0, world_height)]],
    "number": 1,
}
world[apple_data["vertices"][0][1]][apple_data["vertices"][0][0]] = "+"


def print_world() -> None:
    score_string = f"Score: {snake_data['number']}"
    high_score_string = f"High Score: {snake_data['high_score']}"

    print(f"\033[{terminal.lines}A\033[2K", end="")

    print(
        f"\r{'██' * (world_width+2)}\n██{score_string}██{high_score_string}{'██' * (world_width - math.ceil((len(score_string) + len(high_score_string)) / 2))}█\n{'██' * (world_width+2)}"
    )

    for row in world:
        print(
            f"██{''.join([f'{colorama.Fore.RED}██{colorama.Fore.RESET}' if entity == '*' else f'{colorama.Fore.RED}██{colorama.Fore.RESET}' if entity == '+' else f'{colorama.Fore.GREEN}██{colorama.Fore.RESET}' if entity == '@' else '▒▒' for entity in row])}██"
        )

    print(f"{'██' * (world_width+2)}", end="")


def update_world() -> typing.Optional[bool]:
    global apple_data

    for vertice in snake_data["vertices"]:
        world[vertice[1]][vertice[0]] = ""

    for vertice in apple_data["vertices"]:
        world[vertice[1]][vertice[0]] = ""

    last_block_vertices = None

    for index in range(snake_data["number"], 0, -1):
        if last_block_vertices:
            snake_data["vertices"][index - 1], last_block_vertices = (
                last_block_vertices[:],
                snake_data["vertices"][index - 1][:],
            )
        else:
            last_block_vertices = snake_data["vertices"][index - 1][:]

            snake_data["vertices"][index - 1][0] += (
                1
                if snake_data["direction"] == "RIGHT"
                else -1
                if snake_data["direction"] == "LEFT"
                else 0
            )
            snake_data["vertices"][index - 1][1] += (
                1
                if snake_data["direction"] == "DOWN"
                else -1
                if snake_data["direction"] == "UP"
                else 0
            )

            if (
                snake_data["vertices"][index - 1][0] < 0
                or snake_data["vertices"][index - 1][0] >= world_width
                or snake_data["vertices"][index - 1][1] < 0
                or snake_data["vertices"][index - 1][1] >= world_height
            ):  # Out of World
                snake_data["vertices"] = [[0, 0]]
                snake_data["number"] = 1
                snake_data["direction"] = "RIGHT"

                apple_data = {
                    "vertices": [
                        [
                            random.randrange(0, world_width),
                            random.randrange(0, world_height),
                        ]
                    ],
                    "number": 1,
                }

                break

    for vertice in snake_data["vertices"]:
        if [vertice[0], vertice[1]] in apple_data["vertices"]:
            apple_data["vertices"].remove([vertice[0], vertice[1]])
            apple_data["number"] += random.randint(1, 2)

            snake_data["number"] += 1

            if snake_data["number"] > snake_data["high_score"]:
                snake_data["high_score"] = snake_data["number"]

            new_vertice = [
                snake_data["vertices"][0][0]
                - (
                    1
                    if snake_data["direction"] == "RIGHT"
                    else +1
                    if snake_data["direction"] == "LEFT"
                    else 0
                ),
                snake_data["vertices"][0][1]
                - (
                    1
                    if snake_data["direction"] == "DOWN"
                    else +1
                    if snake_data["direction"] == "UP"
                    else 0
                ),
            ]

            if snake_data["vertices"].index([vertice[0], vertice[1]]) != 0:
                snake_data["vertices"].insert(0, new_vertice)
            else:
                snake_data["vertices"].append(new_vertice)

            for _ in range(len(apple_data["vertices"]), apple_data["number"] + 1):
                new_vertice = [
                    random.randrange(0, world_width),
                    random.randrange(0, world_height),
                ]

                apple_data["vertices"].append(new_vertice)

    for index, vertice in enumerate(snake_data["vertices"]):
        world[vertice[1]][vertice[0]] = (
            "@" if index == snake_data["number"] - 1 else "*"
        )

    for vertice in apple_data["vertices"]:
        world[vertice[1]][vertice[0]] = "+"

    snake_data["last_update"] = time.perf_counter()


def trigger_world_update() -> typing.Optional[bool]:
    global world_updating, world, old_world

    if not world_updating:
        world_updating = True
        update_world()

        if world != old_world:
            print_world()

            old_world = [row[:] for row in world]

        world_updating = False


def update_snake_direction(
    key: typing.Union[pynput.keyboard.Key, pynput.keyboard.KeyCode]
) -> None:
    try:
        char = key.char
    except AttributeError:
        char = key

    last_direction = snake_data["direction"]

    if char in ["w", pynput.keyboard.Key.up]:
        snake_data["direction"] = "UP"
    elif char in ["s", pynput.keyboard.Key.down]:
        snake_data["direction"] = "DOWN"
    elif char in ["a", pynput.keyboard.Key.left]:
        snake_data["direction"] = "LEFT"
    elif char in ["d", pynput.keyboard.Key.right]:
        snake_data["direction"] = "RIGHT"

    if last_direction != snake_data["direction"]:
        snake_data["last_direction"] = last_direction
        trigger_world_update()


pynput.keyboard.Listener(on_press=update_snake_direction).start()
os.system("cls" if os.name == "nt" else "clear")

while True:
    if time.perf_counter() - snake_data["last_update"] > 0.25:
        trigger_world_update()
