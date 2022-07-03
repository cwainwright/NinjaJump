from random import randint

import pygame

from assets_fetch import get_image
from constants import SCREEN_WIDTH, ENEMY_SPEED, SCREEN_HEIGHT

from constants import *
from audio import play_sound
from assets_fetch import get_image

from pygame.locals import *

''' Players '''
class Player(pygame.sprite.Sprite):
    def __init__(self, pos: tuple, player=1):
        super().__init__()
        # loading image
        self.set_state()
        # defines the area image is in
        self.rect = self.surf.get_rect()
        # Sets position
        self.rect.bottomleft = pos

        # Input Keys
        input_keys = [
            {"up": K_UP, "left": K_LEFT, "right": K_RIGHT},
            {"up": K_w, "left": K_a, "right": K_d}
        ]
        # Setup input keys:
        self.id = player
        self.up_key = input_keys[player-1]["up"]
        self.left_key = input_keys[player-1]["left"]
        self.right_key = input_keys[player-1]["right"]

        # Sets the motion vectors
        self.i = 0
        self.j = -MAX_SPEED

        self.alive = True

        self.jumping = False
        self.supported = False

        self.name = str(player)
        self.label = Label(self.name, (self.rect.x, self.rect.y - 80), (255, 255, 255))

    # this allows the player to move in both horizontally and vertically
    def move(self):
        pressed_keys = pygame.key.get_pressed()
        if self.alive:
            self.set_state()
            if pressed_keys[self.up_key]:
                if self.supported:
                    play_sound("jump.wav")
                self.set_state("jumping")

            if pressed_keys[self.left_key]:
                self.set_state("left")
                self.i -= SPEED

            if pressed_keys[self.right_key]:
                self.set_state("right")
                self.i += SPEED

        # max speed check
        if self.i > MAX_SPEED:
            self.i = MAX_SPEED
        if self.i < -MAX_SPEED:
            self.i = -MAX_SPEED

        # friction
        if self.i < 0:
            self.i += -self.i/5
        if self.i > 0:
            self.i -= self.i/5

        # roudning down if close to 0
        if self.i > -0.5 and self.i < 0.5:
            self.i = 0

        self.rect.move_ip(self.i, 0)

        # jumping
        if self.jumping:
            self.rect.move_ip(0, self.j)
            if self.j < JUMP_SPEED:
                self.j += SPEED/4

        # edges
        if self.rect.left <= 0:
            self.rect.move_ip(-self.rect.left, 0)
            if self.i < 0:
                self.i = 0

        if self.rect.right >= SCREEN_WIDTH:
            self.rect.move_ip((SCREEN_WIDTH - self.rect.right), 0)
            if self.i > 0:
                self.i = 0

        # bottom
        if self.rect.bottom >= SCREEN_HEIGHT:
            self.rect.move_ip(0, -(self.rect.bottom - SCREEN_HEIGHT))
            self.jumping = False
            self.j = -JUMP_SPEED
            self.supported = True

        # top
        if self.rect.top <= 0:
            self.rect.move_ip(0, -self.rect.top)
            self.j = 1

        # You will never under double negation
        if self.supported == False and self.jumping == False:
            self.j = 0
            self.jumping = True
            self.supported = True

        if self.jumping == False:
            self.supported = False

    def wallCollision(self, platform):
        if self.rect.right > platform.left and self.rect.left < platform.right:
            if self.rect.bottom > platform.top and self.rect.top < platform.top:
                self.rect.move_ip(0, platform.top - self.rect.bottom)
                self.supported = True
                if self.j > 0:
                    self.jumping = False
                    self.j = -JUMP_SPEED

    def get_location(self):
        return(self.rect.x, self.rect.y)

    def set_location(self, location):
        self.rect.center = location

    def draw(self, surface):
        surface.blit(self.surf, self.rect)
        # move label
        self.label.change_location((self.rect.x, self.rect.y - 80))
        # draw label
        if self.alive:
            self.label.show(surface)

    def set_state(self, state = ""):
        if state == "dead":
            self.alive = False
            state_surf = "jumper-dead.png"
        elif state == "jumping":
            self.jumping = True
            state_surf = "jumper-up.png"
        elif state == "left":
            state_surf = "jumper-left.png"
        elif state == "right":
            state_surf = "jumper-right.png"
        else:
            state_surf = "jumper-1.png"
        self.surf = pygame.image.load(get_image(state_surf))

    def kill(self):
        if self.alive == True:
            play_sound('diskhit.wav')
            self.set_state("dead")

    def reset_location(self):
        self.rect.bottomleft = (SCREEN_WIDTH/2 + 100*(self.id-1), SCREEN_HEIGHT-50)


class Label:
    # This instantiates each label, with it's pixel coordinates, it's contents, which is always turned into a string, to make things
    # easier, as well as a colour, which is given a default value of black.
    def __init__(self, contents:str, location:tuple=None, colour:tuple=None, size=round(SCREEN_WIDTH/31.25), shadow:bool=False, shadow_colour:tuple=None, shadow_offset:tuple=None):
        if pygame.font.get_init:
            pygame.font.init()
        if location is None:
            location = (0, 0)
        if colour is None:
            colour = (255, 255, 255)
        if shadow_colour is None:
            shadow_colour = (255 - colour[0], 255 - colour[1], 255 - colour[2])
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
    def show(self, screen):
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

    # This is the alternative to show. It re-renders every time, meaning that if the contents has changed, it will
    # change the label.
    def update(self):
        if self.shadow:
            self.shadow_pre_render = self.shadow_pre_render = self.font.render(self.contents, True, self.shadow_colour)
            self.screen.blit(self.shadow_pre_render, self.shadow_location)
        self.pre_render = self.font.render(self.contents, True, self.colour)
        self.screen.blit(self.pre_render, self.location)

class Image:
    def __init__(self, image: str, location: tuple = None):
        self.image = pygame.image.load(get_image(image))
        self.location = (0, 0) if location is None else location

    def show(self, screen):
        self.screen = screen
        self.screen.blit(self.image, self.location)


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
        # change colour to write
        self.surf.fill((125, 249, 255))
        surface.blit(self.surf, self.rect)

    def get_rect(self):
        return self.rect