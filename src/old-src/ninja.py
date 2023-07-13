import pygame
import random
import os
import sys
import json

from pygame.locals import *

''' Globals '''
SCREEN_WIDTH = 1566
SCREEN_HEIGHT = 800

SPEED = SCREEN_WIDTH/250

ENEMY_SPEED = SCREEN_WIDTH/500

MAX_SPEED = SCREEN_WIDTH/67

JUMP_SPEED = SCREEN_WIDTH/110

BACKGROUND = (255, 255, 255)


''' Json data loaded '''
def loadLevels(filename = "levels.json"):
    with open(filename) as f:
        data = json.load(f)
    return data


def play_sound(filename):
    pygame.mixer.init()
    pygame.mixer.music.load(os.path.join("sounds", filename))
    pygame.mixer.music.play(0)


class Label:
    # This instantiates each label, with it's pixel coordinates, it's contents, which is always turned into a string, to make things
    # easier, as well as a colour, which is given a default value of black.
    def __init__(self, contents, location=(0, 0), colour=(0, 0, 0), size=round(SCREEN_WIDTH/31.25)):
        # This print statement is simply here for debugging, and has been commented out.
        #print("Label Init")
        self.location = location
        self.contents = str(contents)
        # This is one of the built in fonts for pygame. As this does function adequatly I will not be changing it.
        self.font = pygame.font.Font("freesansbold.ttf", size)
        self.colour = colour
        # This stores a rendering of the label, to be used when bliting.
        self.pre_render = self.font.render(str(self.contents), True, self.colour)

    # This is the simple one time show. If the label will never need to change, this puts it on the screen.
    def show_label(self, screen):
        # print("Rendered")
        self.screen = screen
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
        self.pre_render = self.font.render(str(self.contents), True, self.colour)
        self.screen.blit(self.pre_render, self.location)


''' Players '''
class Player(pygame.sprite.Sprite):
    def __init__(self, pos: tuple):
        super().__init__()
        # loading image
        self.surf = pygame.image.load(os.path.join("images", "jumper-1.png"))
        # defines area image is in
        self.rect = self.surf.get_rect()
        # Sets position
        self.rect.bottomleft = pos

        # Sets motion vectors
        self.i = 0
        self.j = -MAX_SPEED

        self.jumping = False
        self.supported = False

        self.score = 0

        self.name = "1"
        self.label = Label(self.name, (self.rect.x, self.rect.y - 80), (255, 0, 0))

    def get_score(self):
        return self.score

    def add_score(self, points=1):
        self.score += points

    def move(self):
        pressed_keys = pygame.key.get_pressed()

        if pressed_keys[K_UP]:
            self.jumping = True
            play_sound("jump.wav")

        if pressed_keys[K_LEFT]:
            self.i -= SPEED

        if pressed_keys[K_RIGHT]:
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
        self.label.show_label(surface)
        
        
class Player2(Player):
    def __init__(self, pos: tuple):
        super().__init__(pos)
        self.surf = pygame.image.load(os.path.join("images", "jumper-1.png"))
        self.name = "2"
        self.label = Label(self.name, (self.rect.x, self.rect.y - 20), (255, 0, 0))

    def move(self):
        pressed_keys = pygame.key.get_pressed()

        if pressed_keys[K_w]:
            self.jumping = True
            play_sound("jump.wav")

        if pressed_keys[K_a]:
            self.i -= SPEED

        if pressed_keys[K_d]:
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


''' Objects '''
class Object(pygame.sprite.Sprite):
    def __init__(self, image, pos: tuple):
        super().__init__()
        self.image = pygame.image.load(os.path.join("images", image)) # MARK: Image must have file extnesion
        self.rect = self.image.get_rect()
        self.rect.bottomleft = pos

    def draw(self, surface):
        surface.blit(self.image, self.rect)

    def get_position(self):
        return self.rect.bottomLeft

    def get_rect(self):
        return self.rect


class Disc(Object):
    def __init__(self, pos: tuple):
            super().__init__('ninja_star.png', pos)
            self.i = ENEMY_SPEED  # speed of stars

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

    def move(self):
        self.rect.move_ip(0, self.j)
        if self.rect.top > SCREEN_HEIGHT:
            self.rect.bottomleft = (random.randint(0, SCREEN_WIDTH),0)


class Diamond(Object):
    def __init__(self, pos: tuple):
        super().__init__('diamond.png', pos)


class Platform:
    def __init__(self, pos: tuple, length, width):
        self.surf = pygame.Surface((length, width))
        self.rect = self.surf.get_rect()
        self.rect.bottomleft = pos

    def draw(self, surface):
        # change color to write
        self.surf.fill((255, 255, 255))
        surface.blit(self.surf, self.rect)

    def get_rect(self):
        return self.rect


''' Game '''
class Game():
    def __init__(self):
        pygame.init()
        self.level_index = 0
        self.levels = ['Round_One', 'Round_Two', 'Round_Three']
        self.level_data = loadLevels()

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
        return self.level_data[self.levels[self.level_index]]

    def start_screen(self):
        self.DISPLAYSURF.blit(pygame.image.load(os.path.join('images', 'loading-background.jpg')), (0,0))

        # q the music
        #try:
            #pygame.mixer.init()
            #pygame.mixer.music.load(os.path.join('sounds', 'game_music.wav'))
            #pygame.mixer.music.play(-1)
        #except:
            #pass                    

        # put text on it using cutsom label class
        label = Label("Press 'h' for help", (10, 750), (255, 0, 0))
        label.show_label(self.DISPLAYSURF)

        # put the ninja run game on screen
        self.DISPLAYSURF.blit(pygame.image.load(os.path.join('images', 'ninja-run.png')), (200 ,200))

        #displaying high score
        self.DISPLAYSURF.blit(pygame.image.load(os.path.join('images', 'high-score.png')), (370 ,400))

        # load some data about top 3 high scores    
        with open("highscores.json", "r") as f:
            highscores = sorted(json.load(f).get("scores", []), key=lambda x: x, reverse=True)

        # put text on it using cutsom label class
        high_score_label = Label(highscores[0], (750, 550), (255, 0, 0))
        high_score_label.show_label(self.DISPLAYSURF)
        
        exit_condition = True
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

    def help_screen(self):
        # put in picture background
        self.DISPLAYSURF.blit(pygame.image.load(os.path.join("images", "brick-background.jpg")), (0, 0))

        # put text on it using cutsom label class
        # help menu title label
        title_label = Label("Help Menu", (SCREEN_WIDTH/2, SCREEN_HEIGHT/2 - 100), (255, 255, 255))
        title_label.show_label(self.DISPLAYSURF)
        
        # TODO: @ETHAN!!!!! Copy and paste whats above for each label needed in help menu

        pygame.display.update()


    def level_setup(self) -> tuple:
        # create platforms
        platforms = []
        for i in range(25):
            platforms.append(Platform(
                (int(json.dumps(self.level['Platform_x'][i])),
                int(json.dumps(self.level['Platform_y'][i]))),
                int(json.dumps(self.level['Platform_length'][i])),
                int(json.dumps(self.level['Platform_width'])))
            )

        # create diamonds
        diamonds = []
        for i in range(5):
            diamonds.append(Diamond((
                int(random.choice(self.level['Diamond_x'])),
                int(self.level['Diamond_y'][random.randint(i, i+1)]))
            ))

        # create spears
        spears = []
        for _ in range(2):
            spears.append(Spear((random.randint(0, SCREEN_WIDTH),0)))

        # create spikes
        spikes = []
        for i in range(3):
            spikes.append(Spike((
                int(json.dumps(self.level['Spikes_x'][i])),
                int(json.dumps(self.level['Spikes_y'][i])))
            ))

        # create discs
        discs = [Disc((100,213)), Disc((600,379)), Disc((900,545)), Disc((1000,711))]

        # return them
        return (platforms, diamonds, spears, spikes, discs)

    # main loop of game
    def main_loop(self, player_count=1):
        
        # initialise Player(s)
        players = [Player((SCREEN_WIDTH/2, SCREEN_HEIGHT-50))]
        if player_count == 2:
            players.append(Player2((SCREEN_WIDTH/2 + 100, SCREEN_HEIGHT-50)))
        # initialise Objects
        platforms, diamonds, spears, spikes, discs = self.level_setup()

        alive = True

        # main Loop
        while alive:
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
            for player in players:
                if player.score >= 20:
                    if player.score >= 40:
                        self.level_index = 2
                    else:
                        self.level_index = 1

            self.DISPLAYSURF.blit(pygame.image.load(os.path.join("images", "brick-background.jpg")), (0, 0))

            for player in players:
                player.move()

            # check if player is on platform
            for i in platforms:
                # get rect
                rectangle = i.get_rect()
                for player in players:
                    if player.rect.colliderect(rectangle):
                        player.wallCollision(rectangle)
            
            # move objects
            for disc in discs:
                disc.move()
            
            for spear in spears:
                spear.move()

            # draw objects
            for platform in platforms:
                platform.draw(self.DISPLAYSURF)

            for spike in spikes:
                spike.draw(self.DISPLAYSURF)
            
            for spear in spears:
                spear.draw(self.DISPLAYSURF)
            
            for disc in discs:
                disc.draw(self.DISPLAYSURF)
            
            for diamond in diamonds:
                diamond.draw(self.DISPLAYSURF)

            # draw Player
            for player in players:
                player.draw(self.DISPLAYSURF)

            # check collisions
            for player in players:
            # spike collisions
                for spike in spikes:
                    if player.rect.colliderect(spike.get_rect()):
                        alive = False
                        play_sound('diskhit.wav')

                for spear in spears:
                    if player.rect.colliderect(spear.get_rect()):
                        alive = False
                        play_sound('diskhit.wav')

                for disc in discs:
                    if player.rect.colliderect(disc.get_rect()):
                        alive = False
                        play_sound('diskhit.wav')

                for diamond in diamonds:
                    if player.rect.colliderect(diamond.get_rect()):
                        play_sound('gem.wav')
                        # add player score
                        player.add_score()

                        # remove diamond
                        diamonds.remove(diamond)

                        # create new diamond and kina random position
                        diamonds.append(Diamond((
                            int(random.choice(self.level['Diamond_x'])),
                            int(random.choice(self.level['Diamond_y']))
                        )))
            
            score_label = Label("Player Two: " + str(players[0].score), (60, 10), (255, 255, 255))
            score_label.show_label(self.DISPLAYSURF)

            if player_count == 2:
                score_label_2 = Label("Player One: " + str(players[1].score), (1150, 10), (255, 255, 255))
                score_label_2.show_label(self.DISPLAYSURF)

            pygame.display.update()
            self.FramePerSec.tick(self.FPS)

        # game over
        for player in players:
            self.add_high_score(player.get_score())
        self.start_screen()

    def add_high_score(self, player_score):
        # make highscores.json if none exists
        if "highscores.json" not in os.listdir():
            highscore_data = {
                "scores": [player_score]
            }
            with open("highscores.json", "w") as f:
                json.dump(highscore_data, f)
        else:
            with open("highscores.json", "r") as f:
                highscore_data = json.load(f)
            highscore_data["scores"].append(player_score)
            with open("highscores.json", "w") as f:
                json.dump(highscore_data, f)

    def high_score_screen(self):

        # get high score(s) from json file (if any)
        self.DISPLAYSURF.blit(pygame.image.load(os.path.join('images', 'brick-background.jpg')), (0,0))

        # load some data about top 3 high scores    
        with open("highscores.json", "r") as f:
            highscores = sorted(json.load(f).get("scores", []), key=lambda x: x, reverse=True)

        # show high scores
        text = ""
        labels = ['First', 'Second', 'Third']
        if len(highscores) < 3:
            for i in range(len(highscores)):
                highscore_label = Label(labels[i] + ". " + str(highscores[i]), (700, 400 + (100 * i)), (255, 255, 255))
                highscore_label.show_label(self.DISPLAYSURF)
        else:
            for i in range(0, 3):
                highscore_label = Label(labels[i] + ". " + str(highscores[i]), (700, 400 + (100 * i)), (255, 255, 255))
                highscore_label.show_label(self.DISPLAYSURF)


        # create title label
        title_label = Label("High Scores", (210, 110), (0, 0, 0), size=200)
        title_label.show_label(self.DISPLAYSURF)
        title_label = Label("High Scores", (200, 100), (255, 255, 255), size=200)
        title_label.show_label(self.DISPLAYSURF)


game = Game()
