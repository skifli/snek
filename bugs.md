# Bugs

- [Bugs](#bugs)
  - [*Bug No.1* - Width is one too little on odd sized column terminals.](#bug-no1---width-is-one-too-little-on-odd-sized-column-terminals)
  - [*Bug No.2* - Game bugs out when hitting the right hand top wall.](#bug-no2---game-bugs-out-when-hitting-the-right-hand-top-wall)



## *Bug No.1* - Width is one too little on odd sized column terminals.

* **Status:** *In Progress*.

## *Bug No.2* - Game bugs out when hitting the right hand top wall.

* **Status:** *Fixed*.
* **Fixed In:** *[c91a948](https://github.com/skifli/snek/commit/c91a948691b26a7b523e59e09240d4f3c104693f)*.
* **Bug Explanation:** It was actually just when hitting the right hand wall or bottom wall. The coordinate would increment and then the program would realise it was out of bounds, but in the *`reset_world`* function it still tried to remove the snake at that out-of-bounds index from the grid. This would result in an **`IndexOutOfRange`** error.
* **Fix:** I ended up introducing a function called *`vertex_in_world`* that would check if a given vertex is in the world. Then in the *`reset_world`* function I made program only remove the index from the grid if it is valid.
* **Notes:** It turns out there was **another bug** which happens when the snake hits *any wall*. The index would be set to *`-1`* and so for **one frame the snake would be on the right-most vertex on the x axis** (because *`-1`* means goes to the end of the list). I fixed this by adding a flag to *`reset_world`* called **full_reset** because setting the index to *`-1`* **was correct for the other application of the function**. If *`full_reset`* is **`True`** then the index is set to *`-1`* since that is what it is set to when the program first starts, otherwise *`0`*.