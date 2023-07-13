import sys

import pygame
import pygame.locals
from audio import play_music

from constants import SCREEN_HEIGHT, SCREEN_WIDTH
from scenes import Scene, StartScreen


def main():
    """
    main() -> None
    Initialises pygame, display and begins playback of background music
    """
    pygame.init()
    pygame.display.set_caption("Ninja Runner")
    play_music("game_music.wav")
    DISPLAYSURF = pygame.display.set_mode(
        (SCREEN_WIDTH, SCREEN_HEIGHT)
    )
    current_scene: Scene = StartScreen
    exit = False
    while not exit:
        current_scene = current_scene(DISPLAYSURF)
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()