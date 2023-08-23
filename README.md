# snek

![Lines of Code](https://img.shields.io/github/languages/code-size/skifli/snek)

- [snek](#snek)
  - [Installation](#installation)
    - [Running from source](#running-from-source)
  - [Usage](#usage)
  - [Known Bugs](#known-bugs)

![Cover](assets/cover.png)

It's snake. But _snek_. In **C**. It supports all OSes that C can run on, and was designed to look like a retro game from the early 80s. It runs entirely in your terminal, no GUI libraries required. It is written in just over 200 lines of code, and if you remove the fancy formatting while maintaining readability it would be around 150 lines of code.

The world width and height is automatically set to the maximum it can be for the size of terminal it is running in, so please don't make the terminal size smaller while playing. Currently the only ways to die are by hitting the world borders, or hitting the snake's body, in which case the score (but not high score), will reset.

## Installation

> [!NOTE]\
> Please make sure you have support for Unicode fonts enabled in your system's settings. If you don't, the game will not look as it should.

### Running from source

- Make sure you have [Clang](https://llvm.org/) installed and is in your system environment variables. If you do not have clang installed, you can install it from [here](https://clang.llvm.org/get_started.html).
- Download and extract the repository from [here](https://github.com/skifli/snek/archive/refs/heads/master.zip). Alternatively, you can clone the repository with [Git](https://git-scm.com/) by running `git clone https://github.com/skifli/snek` in a terminal.
- Navigate into the root directory of your clone of this repository.

## Usage

- Run the command `clang snek.c -o snek.exe` if on Windows, otherwise `clang snek.c - snek`, in the root of your clone of this repository.
- Run the command `snek.exe` if on Windows, else `chmod u+x ./snek && ./snek`

## Known Bugs

Please see [**`bugs.md`**](bugs.md).
