from __future__ import annotations

from random import randint
from typing import Protocol

# import pygame
from pygame import font, key, rect, sprite, surface
from pygame.image import load
from pygame.locals import K_LEFT, K_RIGHT, K_UP, K_a, K_d, K_w

from assets_fetch import get_image
from audio import play_sound
from constants import *
from constants import ENEMY_SPEED, SCREEN_HEIGHT, SCREEN_WIDTH

font.init()

''' Game Object Protocol '''
class GameObject(Protocol):
    def draw(self, surf: surface.Surface) -> None: ...

''' Players '''
class Player(sprite.Sprite, GameObject):
    """Player Character class

    Inherits:
        pygame.sprite.Sprite: used for draw calls and collision detection
    """
    def __init__(self, pos: tuple[int, int], player: int = 1):
        """Initialise new instance of Player object

        Args:
            pos (tuple): initial position as tuple
            player (int, optional): player 1 or 2 (or more). Defaults to 1.
        """
        super().__init__()
        # loading image
        self.set_state()
        # defines the area image is in
        self.rect: rect.Rect = self.surf.get_rect()
        # Sets position
        self.rect.bottomleft = pos

        # Input Keys
        input_keys: list[dict[str, int]] = [
            {"up": K_UP, "left": K_LEFT, "right": K_RIGHT},
            {"up": K_w, "left": K_a, "right": K_d}
        ]
        # Setup input keys:
        self.id = player
        self.up_key = input_keys[player-1]["up"]
        self.left_key = input_keys[player-1]["left"]
        self.right_key = input_keys[player-1]["right"]

        # Sets the motion vectors
        self.i: float = 0
        self.j: float = -MAX_SPEED

        self.state_alive: bool = True

        self.state_jumping: bool = False
        self.supported: bool = False

        self.name: str = str(player)
        self.label: Label = Label(self.name, (self.rect.x, self.rect.y - 80), (255, 255, 255))

    # this allows the player to move in both horizontally and vertically
    def move(self):
        """Move player
        
        (check for keypresses -> apply acceleration to player object)
        """
        pressed_keys = key.get_pressed()
        if self.state_alive:
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
        if self.state_jumping:
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
            self.state_jumping = False
            self.j = -JUMP_SPEED
            self.supported = True

        # top
        if self.rect.top <= 0:
            self.rect.move_ip(0, -self.rect.top)
            self.j = 1

        # You will never under double negation
        if self.supported == False and self.state_jumping == False:
            self.j = 0
            self.state_jumping = True
            self.supported = True

        if self.state_jumping == False:
            self.supported = False

    def wallCollision(self, platform: rect.Rect):
        """Wall Collision
        
        If collision is detected -> apply suitable acceleration

        Args:
            platform (pygame.rect): platform dimension vectors
        """
        if self.rect.right > platform.left and self.rect.left < platform.right:
            if self.rect.bottom > platform.top and self.rect.top < platform.top:
                self.rect.move_ip(0, platform.top - self.rect.bottom)
                self.supported = True
                if self.j > 0:
                    self.state_jumping = False
                    self.j = -JUMP_SPEED

    def get_location(self) -> tuple[int, int]:
        """Get Location
        
        Get player location as (x, y) tuple
        """
        return(self.rect.x, self.rect.y)

    def set_location(self, location: tuple[int, int]):
        """Set Location
        
        Set player location to (x, y) tuple

        Args:
            location (tuple): location to set player to (x, y)
        """
        self.rect.center = location

    def draw(self, surf: surface.Surface):
        """Draw
        
        Draw player to display object passed in by reference
        
        Once player is dead, player label is not drawn

        Args:
            display (pygame.surface.Surface): display object to draw player to
        """
        surf.blit(self.surf, self.rect)
        # move label
        self.label.change_location((self.rect.x, self.rect.y - 80))
        # draw label
        if self.state_alive:
            self.label.draw(surf)

    def set_state(self, state: str = ""):
        """Set Player State

        Args:
            state (str, optional): state to set player to. Defaults to "".
        """
        if state == "dead":
            self.state_alive = False
            state_surf = "jumper-dead.png"
        elif state == "jumping":
            self.state_jumping = True
            state_surf = "jumper-up.png"
        elif state == "left":
            state_surf = "jumper-left.png"
        elif state == "right":
            state_surf = "jumper-right.png"
        else:
            state_surf = "jumper-1.png"
        self.surf: surface.Surface = load(get_image(state_surf))

    def kill(self):
        """Kill Player
        
        If alive, update player state to dead, play 'diskhit.wav' sound effect
        """
        if self.state_alive == True:
            play_sound('diskhit.wav')
            self.set_state("dead")

    def reset_location(self):
        """Reset Location of Player
        
        Resets location to default starting location
        """
        self.rect.bottomleft = (int(SCREEN_WIDTH/2 + 100*(self.id-1)), int(SCREEN_HEIGHT-50))


class Label(GameObject):
    """Object to print text to display
    """
    # This instantiates each label, with it's pixel coordinates, it's contents, which is always turned into a string, to make things
    # easier, as well as a colour, which is given a default value of black.
    def __init__(self, contents:str, location:tuple[int, int] = (0, 0), colour: tuple[int, int, int] = (255, 255, 255), size:int=BODYSIZE, shadow: bool = False, shadow_colour: tuple[int, int, int] = (-1, -1, -1), shadow_offset: tuple[int, int] = (1, 1)):
        """Initialise new instance of Label

        Args:
            contents (str): string to print
            location (tuple, optional): where to display text ondisplay. Defaults to None.
            colour (tuple, optional): what colour the text should have. Defaults to None.
            size (int, optional): what size the text should be. Defaults to BODYSIZE constant.
            shadow (bool, optional): whether a shadow (copy) should be displayed behind the text. Defaults to False.
            shadow_colour (tuple, optional): what colour the shadow should be. Defaults to None.
            shadow_offset (tuple, optional): how offset the shadow should be as an (x, y) tuple. Defaults to None.
        """
        if shadow_colour == (-1, -1, -1):
            shadow_colour = (255 - colour[0], 255 - colour[1], 255 - colour[2])
        # This is one of the built in fonts for pygame. As this does function adequatly I will not be changing it.
        self.font = font.Font("freesansbold.ttf", size)
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

    # This is the simple one time draw. If the label will never need to change, this puts it on the display.
    def draw(self, surf: surface.Surface) -> None:
        """Displays text once ondisplay, used when string displayed remains constant

        Args:
            display (pygame.surface.Surface): the display object to draw the text onto
        """
        # print("Rendered")
        self.surf = surf
        if self.shadow:
            self.surf.blit(self.shadow_pre_render, self.shadow_location)
        self.surf.blit(self.pre_render, self.location)

    # This is the quick way of changing the contents
    def change_contents(self, new_contents: str):
        """Change Contents

        Args:
            new_contents (str): new contents of the label (updated on next draw() call)
        """
        self.contents = str(new_contents)

    # This is the quick way of changing the location
    def change_location(self, new_location: tuple[int, int]):
        """Change Label Location
        
        Move label to provided locaiton

        Args:
            new_location (tuple): new location for label to move to
        """
        self.location = new_location

    # This is the alternative to draw. It re-renders every time, meaning that if the contents has changed, it will
    # change the label.
    def update(self):
        """Update Prerendered Details
        """
        if self.shadow:
            self.shadow_pre_render = self.shadow_pre_render = self.font.render(self.contents, True, self.shadow_colour)
            self.surf.blit(self.shadow_pre_render, self.shadow_location)
        self.pre_render = self.font.render(self.contents, True, self.colour)
        self.surf.blit(self.pre_render, self.location)

class Image(GameObject):
    def __init__(self, image: str, location: tuple[int, int] = (-1, -1)):
        self.image: surface.Surface = load(get_image(image))
        self.location: tuple[int, int] = (0, 0) if location == (-1, -1) else location

    def draw(self, surf: surface.Surface):
        self.surf = surf
        self.surf.blit(self.image, self.location)


''' Objects '''
class Sprite(sprite.Sprite):
    def __init__(self, image: str, pos: tuple[int, int]):
        super().__init__()
        self.image: surface.Surface = load(get_image(image)) # MARK: Image must have file extnesion
        self.rect: rect.Rect = self.image.get_rect()
        self.rect.bottomleft = pos

    # displaying the object on the display 
    def draw(self, surf: surface.Surface):
        surf.blit(self.image, self.rect)

    def get_position(self):
        return self.rect.bottomleft

    def get_rect(self):
        return self.rect


''' Enemy Objects '''
class Disk(Sprite):
    def __init__(self, pos: tuple[int, int]):
            super().__init__('ninja_star.png', pos)
            self.i = ENEMY_SPEED  # speed of stars

    # Moves the object horizontally accross the display
    def move(self):
        self.rect.move_ip(self.i, 0)
        if self.rect.left < 0 or self.rect.right > SCREEN_WIDTH:
            self.i *= -1


class Spike(Sprite):
    def __init__(self, pos: tuple[int, int]):
        super().__init__('spikes.png', pos)


class Spear(Sprite):
    def __init__(self, pos: tuple[int, int]):
        super().__init__('spear.png', pos)
        self.j = ENEMY_SPEED

    # Moves the object vertically down the display
    def move(self):
        self.rect.move_ip(0, self.j)
        if self.rect.top > SCREEN_HEIGHT:
            self.rect.bottomleft = (randint(0, SCREEN_WIDTH),0)

''' Collectables '''
class Diamond(Sprite):
    def __init__(self, pos: tuple[int, int]):
        super().__init__('diamond.png', pos)


class Platform(Sprite):
    def __init__(self, pos: tuple[int, int], length: int, width: int):
        self.surf = surface.Surface((length, width))
        self.rect: rect.Rect = self.surf.get_rect()
        self.rect.bottomleft = pos

    # displays the playforms on the surf 
    def draw(self, surf: surface.Surface):
        # change colour to write
        self.surf.fill((125, 249, 255))
        surf.blit(self.surf, self.rect)

    def get_rect(self) -> rect.Rect:
        return self.rect
