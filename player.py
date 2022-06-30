from constants import *
from objects import Label, pygame
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
            self.label.show_label(surface)

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
