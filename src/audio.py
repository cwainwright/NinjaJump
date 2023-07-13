from os import listdir, path

import pygame

from assets_fetch import get_sound

pygame.mixer.init()

def play_music(filename: str):
    pygame.mixer.music.load(get_sound(filename))
    pygame.mixer.music.play(-1)

def play_sound(filename: str):
    id: int
    try:
        soundFiles: list[str] = listdir(path.join("assets", "sounds"))
        id = soundFiles.index(filename)
    except IndexError:
        return
    sound = pygame.mixer.Sound(get_sound(filename))
    pygame.mixer.Channel(id).play(sound)
