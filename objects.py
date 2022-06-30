from random import randint

import pygame

from assets_fetch import get_image
from constants import SCREEN_WIDTH, ENEMY_SPEED, SCREEN_HEIGHT

class Label:
    # This instantiates each label, with it's pixel coordinates, it's contents, which is always turned into a string, to make things
    # easier, as well as a colour, which is given a default value of black.
    def __init__(self, contents:str, location:tuple=None, colour:tuple=None, size=round(SCREEN_WIDTH/31.25), shadow:bool=False, shadow_colour:tuple=None, shadow_offset:tuple=None):
        if location is None:
            location = (0, 0)
        if colour is None:
            colour = (255, 255, 255)
        if shadow_colour is None:
            shadow_colour = (0, 0, 0)
        if shadow_offset is None:
            shadow_offset = (1, 1)
        # This is one of the built in fonts for pygame. As this does function adequatly I will not be changing it.
        self.font = pygame.font.Font("freesansbold.ttf", size)
        # This print statement is simply here for debugging, and has been commented out.
        #print("Label Init")
        self.contents = str(contents)
        self.location = location
        self.colour = colour
        self.shadow = shadow
        self.shadow_location = (location[0] + round((size/20)*shadow_offset[0]), location[1] + round((size/20)*shadow_offset[1]))
        self.shadow_colour = shadow_colour
        # This stores a rendering of the label, to be used when blitting.
        self.pre_render = self.font.render(self.contents, True, self.colour)
        if self.shadow:
            self.shadow_pre_render = self.font.render(self.contents, True, self.shadow_colour)

    # This is the simple one time show. If the label will never need to change, this puts it on the screen.
    def show_label(self, screen):
        # print("Rendered")
        self.screen = screen
        if self.shadow:
            self.screen.blit(self.shadow_pre_render, self.shadow_location)
        self.screen.blit(self.pre_render, self.location)

    # This is the quick way of changing the contents
    def change_contents(self, new_contents):
        self.contents = str(new_contents)

    # This is the quick way of changing the location
    def change_location(self, new_location):
        self.location = new_location

    # This is the alternative to show_label. It re-renders every time, meaning that if the contents has changed, it will
    # change the label.
    def update(self):
        if self.shadow:
            self.shadow_pre_render = self.shadow_pre_render = self.font.render(self.contents, True, self.shadow_colour)
            self.screen.blit(self.shadow_pre_render, self.shadow_location)
        self.pre_render = self.font.render(self.contents, True, self.colour)
        self.screen.blit(self.pre_render, self.location)

''' Objects '''
class Object(pygame.sprite.Sprite):
    def __init__(self, image, pos: tuple):
        super().__init__()
        self.image = pygame.image.load(get_image(image)) # MARK: Image must have file extnesion
        self.rect = self.image.get_rect()
        self.rect.bottomleft = pos

    # displaying the object on the screen 
    def draw(self, surface):
        surface.blit(self.image, self.rect)

    def get_position(self):
        return self.rect.bottomleft

    def get_rect(self):
        return self.rect

''' Enemy Objects '''
class Disk(Object):
    def __init__(self, pos: tuple):
            super().__init__('ninja_star.png', pos)
            self.i = ENEMY_SPEED  # speed of stars

    # Moves the object horizontally accross the screen
    def move(self):
        self.rect.move_ip(self.i, 0)
        if self.rect.left < 0 or self.rect.right > SCREEN_WIDTH:
            self.i *= -1


class Spike(Object):
    def __init__(self, pos: tuple):
        super().__init__('spikes.png', pos)


class Spear(Object):
    def __init__(self, pos: tuple):
        super().__init__('spear.png', pos)
        self.j = ENEMY_SPEED

    # Moves the object vertically down the screen
    def move(self):
        self.rect.move_ip(0, self.j)
        if self.rect.top > SCREEN_HEIGHT:
            self.rect.bottomleft = (randint(0, SCREEN_WIDTH),0)

''' Collectables '''
class Diamond(Object):
    def __init__(self, pos: tuple):
        super().__init__('diamond.png', pos)


class Platform:
    def __init__(self, pos: tuple, length, width):
        self.surf = pygame.Surface((length, width))
        self.rect = self.surf.get_rect()
        self.rect.bottomleft = pos

    # displays the playforms on the screen 
    def draw(self, surface):
        # change color to write
        self.surf.fill((125, 249, 255))
        surface.blit(self.surf, self.rect)

    def get_rect(self):
        return self.rect