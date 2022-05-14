from ast import dump
from copy import deepcopy
import pygame
import random
import os
import sys
from json import load, dump
from math import floor

from pygame.locals import *

''' Globals '''
SCREEN_WIDTH = 1566
SCREEN_HEIGHT = 830

SPEED = SCREEN_WIDTH/250

ENEMY_SPEED = SCREEN_WIDTH/500

MAX_SPEED = SCREEN_WIDTH/67

JUMP_SPEED = SCREEN_WIDTH/110

BACKGROUND = (255, 255, 255)

LEVELFILE = "levels.json"


''' Json data loaded '''
def loadLevels(filename=LEVELFILE):
    with open(os.path.join("levels", filename)) as f:
        data = load(f)
    return data


def play_sound(filename):
    pygame.mixer.init()
    pygame.mixer.music.load(os.path.join("sounds", filename))
    pygame.mixer.music.play(0)


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


''' Players '''
class Player(pygame.sprite.Sprite):
    def __init__(self, pos: tuple):
        super().__init__()
        # loading image
        self.surf = pygame.image.load(os.path.join("images", "jumper-1.png"))
        # defines the area image is in
        self.rect = self.surf.get_rect()
        # Sets position
        self.rect.bottomleft = pos

        # Sets the motion vectors
        self.i = 0
        self.j = -MAX_SPEED

        self.alive = True

        self.jumping = False
        self.supported = False

        self.name = "1"
        self.label = Label(self.name, (self.rect.x, self.rect.y - 80), (255, 255, 255))

    # this allows the player to move in both horizontally and vertically
    def move(self):
        pressed_keys = pygame.key.get_pressed()
        if self.alive:
            self.surf = pygame.image.load(os.path.join("images", "jumper-1.png"))
            if pressed_keys[K_UP]:
                self.surf = pygame.image.load(os.path.join("images", "jumper-up.png"))
                self.jumping = True
                play_sound("jump.wav")

            if pressed_keys[K_LEFT]:
                self.surf = pygame.image.load(os.path.join("images", "jumper-left.png"))
                self.i -= SPEED

            if pressed_keys[K_RIGHT]:
                self.surf = pygame.image.load(os.path.join("images", "jumper-right.png"))
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

        # if jumping not supported !
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

    def kill(self):
        if self.alive == True:
            self.alive = False
            play_sound('diskhit.wav')
            self.surf = pygame.image.load(os.path.join("images", "jumper-dead.png"))
        
        
class Player2(Player):
    def __init__(self, pos: tuple):
        super().__init__(pos)
        self.surf = pygame.image.load(os.path.join("images", "jumper-1.png"))
        self.name = "2"
        self.label = Label(self.name, (self.rect.x, self.rect.y - 20), (255, 255, 255))

    # allows the second player to move horizontally and vertically
    def move(self):
        pressed_keys = pygame.key.get_pressed()
        if self.alive:
            self.surf = pygame.image.load(os.path.join("images", "jumper-1.png"))
            if pressed_keys[K_w]:
                self.jumping = True
                self.surf = pygame.image.load(os.path.join("images", "jumper-up.png"))
                play_sound("jump.wav")

            if pressed_keys[K_a]:
                self.surf = pygame.image.load(os.path.join("images", "jumper-left.png"))
                self.i -= SPEED

            if pressed_keys[K_d]:
                self.surf = pygame.image.load(os.path.join("images", "jumper-right.png"))
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


''' Objects '''
class Object(pygame.sprite.Sprite):
    def __init__(self, image, pos: tuple):
        super().__init__()
        self.image = pygame.image.load(os.path.join("images", image)) # MARK: Image must have file extnesion
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
            self.rect.bottomleft = (random.randint(0, SCREEN_WIDTH),0)

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


''' Game '''
class Game():
    def __init__(self):
        pygame.init()

        self.level_data = loadLevels()

        self.score = 0

        self.FPS = 60
        self.FramePerSec = pygame.time.Clock()
        self.DISPLAYSURF = pygame.display.set_mode(
            (SCREEN_WIDTH, SCREEN_HEIGHT)
        )

        self.DISPLAYSURF.fill(BACKGROUND)

        pygame.display.set_caption('Ninja Runner')

        self.start_screen()

    @property
    def level(self):
        try:
            return self.level_data[self.level_index]
        except IndexError:
            return self.level_data[2]

    @property
    def level_index(self):
        return floor(self.score/20)

    def increment_score(self):
        self.score += 1

    # Screen displayed after the player dies
    def game_over_screen(self):
        label = Label("Game Over", (240, 360), (0,0,0) , size=200, shadow=True, shadow_colour=(255, 255, 255))
        label.show_label(self.DISPLAYSURF)
        

        pygame.display.update()
        while True:
            for event in pygame.event.get():
                if event.type == QUIT:
                        exit_condition = False

                if pygame.key.get_pressed()[K_b]:
                        self.start_screen()
                        
    # Screen displayed beteen games and when the game is started
    def start_screen(self):
        self.DISPLAYSURF.blit(pygame.image.load(os.path.join('images', 'loading-background.jpg')), (0,0))

        # q the music
        try:
            pygame.mixer.init()
            pygame.mixer.music.load(os.path.join('sounds', 'game_music.wav'))
            pygame.mixer.music.play(-1)
        except:
            pass                    

        # put text on it using cutsom label class
        label = Label("Press 'h' for help", (10, 780), (255, 0, 0) , size=25)
        label.show_label(self.DISPLAYSURF)

        # put the ninja run game on screen
        self.DISPLAYSURF.blit(pygame.image.load(os.path.join('images', 'ninja-run.png')), (200 ,200))

        #displaying high score
        self.DISPLAYSURF.blit(pygame.image.load(os.path.join('images', 'high-score.png')), (370 ,400))

        # load some data about top 3 high scores   
        try: 
            with open("highscores.json", "r") as f:
                highscores = sorted(load(f).get("scores", []), key=lambda x: x, reverse=True)
        except FileNotFoundError:
            highscores = [0]

        # put text on it using cutsom label class
        high_score_label = Label(highscores[0], (750, 550), (255, 0, 0))
        high_score_label.show_label(self.DISPLAYSURF)
        
        exit_condition = True
        # Set level to 1
        while exit_condition:
            for event in pygame.event.get():
                if event.type == QUIT:
                    exit_condition = False

                if pygame.key.get_pressed()[K_1]:
                    # play the game
                    self.main_loop()

                if pygame.key.get_pressed()[K_2]:
                    # play the game with 2 players
                    self.main_loop(2)

                if pygame.key.get_pressed()[K_h]:
                    # show the help
                    self.help_screen()


                if pygame.key.get_pressed()[K_l]:
                    # show high scores screen
                    self.high_score_screen()

            pygame.display.update()
        pygame.quit()
        sys.exit()

    # The help screen with all of the buttons that have functions
    def help_screen(self):
        # put in picture background
        self.DISPLAYSURF.blit(pygame.image.load(os.path.join("images", "brick-background.jpg")), (0, 0))

        # put text on it using cutsom label class
        # help menu title label
        
        title_label = Label("Help Menu", (360, 60), (0, 0, 0), size=150, shadow=True, shadow_colour=(255, 255, 255))
        title_label.show_label(self.DISPLAYSURF)

        title_label = Label("1 - One Player", (105, 255), (0, 0, 0), size=50, shadow=True, shadow_colour=(255, 255, 255))
        title_label.show_label(self.DISPLAYSURF)
        title_label = Label("B - Back", (585, 255), (0, 0, 0), size=50, shadow=True, shadow_colour=(255, 255, 255))
        title_label.show_label(self.DISPLAYSURF)
        title_label = Label("L - Leaderboard", (1075, 255), (0, 0, 0), size=50, shadow=True, shadow_colour=(255, 255, 255))
        title_label.show_label(self.DISPLAYSURF)
        title_label = Label("2 - Two Player", (105, 355), (0, 0, 0), size=50, shadow=True, shadow_colour=(255, 255, 255))
        title_label.show_label(self.DISPLAYSURF)
        title_label = Label("P - Pause Menu", (1070, 355), (0, 0, 0), size=50, shadow=True, shadow_colour=(255, 255, 255))
        title_label.show_label(self.DISPLAYSURF)
        title_label = Label("H - Help Menu", (585, 355), (0, 0, 0), size=50, shadow=True, shadow_colour=(255, 255, 255))
        title_label.show_label(self.DISPLAYSURF)

        title_label = Label("Player One", (155, 455), (0, 0, 0), size=100, shadow=True, shadow_colour=(255, 255, 255))
        title_label.show_label(self.DISPLAYSURF)
        title_label = Label("^ - Jump", (155, 555), (0, 0, 0), size=50, shadow=True, shadow_colour=(255, 255, 255))
        title_label.show_label(self.DISPLAYSURF)
        title_label = Label("> - Move Right", (155, 655), (0, 0, 0), size=50, shadow=True, shadow_colour=(255, 255, 255))
        title_label.show_label(self.DISPLAYSURF)
        title_label = Label("< - Move Left", (155, 755), (0, 0, 0), size=50, shadow=True, shadow_colour=(255, 255, 255))
        title_label.show_label(self.DISPLAYSURF)

        title_label = Label("Player Two", (905, 455), (0, 0, 0), size=100, shadow=True, shadow_colour=(255, 255, 255))
        title_label.show_label(self.DISPLAYSURF)
        title_label = Label("W - Jump", (905, 555), (0, 0, 0), size=50, shadow=True, shadow_colour=(255, 255, 255))
        title_label.show_label(self.DISPLAYSURF)
        title_label = Label("D - Move Right", (905, 655), (0, 0, 0), size=50, shadow=True, shadow_colour=(255, 255, 255))
        title_label.show_label(self.DISPLAYSURF)
        title_label = Label("A - Move Left", (905, 755), (0, 0, 0), size=50, shadow=True, shadow_colour=(255, 255, 255))
        title_label.show_label(self.DISPLAYSURF)
        title_label = Label("_______________________________________________________________________________", (0, 370), (255, 255, 255), size=50)
        title_label.show_label(self.DISPLAYSURF)

        
        pygame.display.update()

        while True:
            for event in pygame.event.get():
                if pygame.key.get_pressed()[K_b]:
                    self.start_screen()

    # Sets all of the objects and background up to be displayed 
    def level_setup(self, multiplayer) -> tuple:
        # create platforms
        platforms = []
        for platform in self.level["platforms"]:
            platforms.append(Platform(
                (platform["x"], platform["y"]), platform["l"], platform["w"]
            ))

        # create diamonds
        diamonds = []
        diamond_list = deepcopy(self.level["diamonds"])
        for _ in range(5):
            diamond = random.choice(diamond_list)
            try:
                diamond_list.remove(diamond)
            except ValueError:
                pass
            else:
                diamonds.append(Diamond(
                    (diamond["x"], diamond["y"])
                ))

        # create spikes
        spikes = []
        for spike in self.level["spikes"]:
            spikes.append(Spike(
                (spike["x"], spike["y"])
            ))

        # create disks
        disks = []
        for disk in self.level["disks"]:
            disks.append(Disk(
                (disk["x"], disk["y"])
            ))

        # create spears
        spears = []
        for _ in range(2):
            spears.append(Spear((random.randint(0, SCREEN_WIDTH),0)))

        players = [Player((SCREEN_WIDTH/2, SCREEN_HEIGHT-50))]
        if multiplayer:
            players.append(Player2((SCREEN_WIDTH/2 + 100, SCREEN_HEIGHT-50)))

        # return them
        return (players, platforms, diamonds, spears, spikes, disks)

    # main loop of game
    def main_loop(self, multiplayer=False):

        # level selection
        level = 0

        # initialise Player(s)
        self.players = [Player((SCREEN_WIDTH/2, SCREEN_HEIGHT-50))]
        if multiplayer:
            self.players.append(Player2((SCREEN_WIDTH/2 + 100, SCREEN_HEIGHT-50)))
        # initialise Objects
        self.players, self.platforms, self.diamonds, self.spears, self.spikes, self.disks = self.level_setup(multiplayer)

        # main Loop
        while any([player.alive for player in self.players]):
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
            if self.level_index != level:
                self.players, self.platforms, self.diamonds, self.spears, self.spikes, self.disks = self.level_setup(multiplayer)
                
                level = self.level_index
                        
            self.render()

            for player in self.players:
                player.move()

            # check if player is on platform
            for i in self.platforms:
                # get rect
                rectangle = i.get_rect()
                for player in self.players:
                    if player.rect.colliderect(rectangle):
                        player.wallCollision(rectangle)
            
            # move objects
            for disk in self.disks:
                disk.move()
            
            for spear in self.spears:
                spear.move()

            # check collisions
            for player in self.players:
            # spike collisions
                for spike in self.spikes:
                    if player.rect.colliderect(spike.get_rect()):
                        player.kill()

                for spear in self.spears:
                    if player.rect.colliderect(spear.get_rect()):
                        player.kill()

                for disk in self.disks:
                    if player.rect.colliderect(disk.get_rect()):
                        player.kill()

                for diamond in self.diamonds:
                    if player.rect.colliderect(diamond.get_rect()):
                        play_sound('gem.wav')
                        # add player score
                        self.increment_score()

                        # create new diamond in random position
                        new_diamond = random.choice(self.level["diamonds"])
                        while (new_diamond["x"], new_diamond["y"]) in [d.get_position() for d in self.diamonds]:
                            new_diamond = random.choice(self.level["diamonds"])
                        self.diamonds.append(Diamond(
                            (new_diamond["x"], new_diamond["y"])
                        ))

                        # remove diamond
                        self.diamonds.remove(diamond)

        # game over
        self.render()
        self.add_high_score(self.score)
        self.score = 0
        self.game_over_screen()

    def render(self):
        # draw background
        self.DISPLAYSURF.blit(pygame.image.load(os.path.join("images", "brick-background.jpg")), (0, 0))

        # draw objects
        for platform in self.platforms:
            platform.draw(self.DISPLAYSURF)

        for spike in self.spikes:
            spike.draw(self.DISPLAYSURF)
        
        for spear in self.spears:
            spear.draw(self.DISPLAYSURF)
        
        for disk in self.disks:
            disk.draw(self.DISPLAYSURF)
        
        for diamond in self.diamonds:
            diamond.draw(self.DISPLAYSURF)

        # draw players
        for player in self.players:
            player.draw(self.DISPLAYSURF)

        score_label = Label("Score: " + str(self.score), (60, 10), (255, 255, 255))
        score_label.show_label(self.DISPLAYSURF)
        
        # Update Display
        pygame.display.update()
        self.FramePerSec.tick(self.FPS)

    def add_high_score(self, player_score):
        # make highscores.json if none exists
        if "highscores.json" not in os.listdir():
            highscore_data = {
                "scores": [player_score]
            }
            with open("highscores.json", "w") as f:
                dump(highscore_data, f)
        else:
            with open("highscores.json", "r") as f:
                highscore_data = load(f)
            highscore_data["scores"].append(player_score)
            with open("highscores.json", "w") as f:
                dump(highscore_data, f)

    # Leader board screen displayed with the top players
    def high_score_screen(self):

        # get high score(s) from json file (if any)
        self.DISPLAYSURF.blit(pygame.image.load(os.path.join('images', 'brick-background.jpg')), (0,0))

        # load some data about top 3 high scores
        with open("highscores.json", "r") as f:
            highscores = sorted(load(f).get("scores", []), key=lambda x: x, reverse=True)

        # show high scores
        text = ""
        labels = ['First', 'Second', 'Third']
        if len(highscores) < 3:
            for i in range(len(highscores)):
                highscore_label = Label(labels[i] + ":     " + str(highscores[i]), (550, 350 + (162 * i)), (0, 0, 0), size=65, shadow=True, shadow_colour=(255, 255, 255))
                highscore_label.show_label(self.DISPLAYSURF)
                
                
        else:
            for i in range(0, 3):
                highscore_label = Label(labels[i] + ":     " + str(highscores[i]), (550, 350 + (162 * i)), (0, 0, 0), size=65, shadow=True, shadow_colour=(255, 255, 255))
                highscore_label.show_label(self.DISPLAYSURF)
                


        # create title label
        title_label = Label("High Scores", (210, 60), (0, 0, 0), size=200, shadow=True, shadow_colour=(255, 255, 255))
        title_label.show_label(self.DISPLAYSURF)

        pygame.display.update()

        while True:
            for event in pygame.event.get():
                if pygame.key.get_pressed()[K_b]:
                    self.start_screen()

                if event.type == QUIT:
                    pygame.quit()

if __name__ == "__main__":
    game = Game()