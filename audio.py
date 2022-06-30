from assets_fetch import get_sound

import pygame


def play_music(filename):
    if pygame.mixer.get_init() is None:
        pygame.mixer.init()
    pygame.mixer.music.load(get_sound(filename))
    pygame.mixer.music.play(-1)

def play_sound(filename):
    if pygame.mixer.get_init() is None:
        pygame.mixer.init()
    sound = pygame.mixer.Sound(get_sound(filename))
    if not pygame.mixer.find_channel(force=True).get_busy():
        pygame.mixer.find_channel(force=True).play(sound, loops=0)
