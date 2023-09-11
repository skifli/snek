#include <stdlib.h>

#include "utils/array.c"

#if defined(_WIN32) || defined(_WIN64)
#define OS 1
#elif defined(__linux__)
#define OS 2
#endif

static char *chars[2] = {"\u2588", "\u2592"};
static int terminal_height, terminal_width;

void clearTerminal(void) { system(OS == 1 ? "cls" : "clear"); }

void moveCursorToTop(void) { printf("\033[%dA\033[2K", terminal_height); }

void startGame(void) { clearTerminal(); }

int main(void) {
	startGame();

	return 0;
}
