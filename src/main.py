import sys

import pygame
from pygame.locals import *
from audio import play_music

from constants import SCREEN_HEIGHT, SCREEN_WIDTH
from scenes import StartScreen


def main():
    pygame.init()
    pygame.display.set_caption("Ninja Runner")
    play_music("game_music.wav")
    DISPLAYSURF = pygame.display.set_mode(
        (SCREEN_WIDTH, SCREEN_HEIGHT)
    )
    current_scene = StartScreen
    exit = False
    while not exit:
        try:
            current_scene = current_scene(DISPLAYSURF)
        except ValueError:
            current_scene = current_scene(DISPLAYSURF)
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
