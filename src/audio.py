from os import listdir

import pygame

from assets_fetch import get_asset, get_sound

def play_music(filename):
    if pygame.mixer.get_init() is None:
        pygame.mixer.init()
    pygame.mixer.music.load(get_sound(filename))
    pygame.mixer.music.play(-1)

def play_sound(filename):
    if pygame.mixer.get_init() is None:
        pygame.mixer.init()
    try:
        id=listdir(get_sound()).index(filename)
    except IndexError:
        id=1
    sound = pygame.mixer.Sound(get_sound(filename))
    pygame.mixer.Channel(id).play(sound)

