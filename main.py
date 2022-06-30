import random
import sys
from ast import dump
from copy import deepcopy
from json import dump, load
from math import floor
from threading import local

from assets_fetch import get_image, get_level
from audio import play_music, play_sound
from constants import *
from objects import Diamond, Disk, Label, Platform, Spear, Spike
from player import *

""" Json data loaded """
def loadLevels(filename=LEVELFILE):
    with open(get_level(filename)) as f:
        data = load(f)
    return data




""" Game """
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

        pygame.display.set_caption("Ninja Runner")

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
        self.DISPLAYSURF.blit(pygame.image.load(get_image("loading-background.jpg")), (0,0))

        # q the music
        play_music("game_music.wav")                 

        # put text on it using cutsom label class
        label = Label("Press 'h' for help", (10, 780), (255, 0, 0) , size=25)
        label.show_label(self.DISPLAYSURF)

        # put the ninja run game on screen
        self.DISPLAYSURF.blit(pygame.image.load(get_image("ninja-run.png")), (200 ,200))

        #displaying high score
        self.DISPLAYSURF.blit(pygame.image.load(get_image("high-score.png")), (370 ,400))

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
        self.DISPLAYSURF.blit(pygame.image.load(get_image("brick-background.jpg")), (0, 0))

        # put text on it using cutsom label class
        # help menu title label

        # TODO: Fix this mess
        
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
            players.append(Player((SCREEN_WIDTH/2 + 100, SCREEN_HEIGHT-50), 2))

        # return them
        return (players, platforms, diamonds, spears, spikes, disks)

    # main loop of game
    def main_loop(self, multiplayer=False):

        # level selection
        level = 0

        # initialise Player(s)
        self.players = [Player((SCREEN_WIDTH/2, SCREEN_HEIGHT-50))]
        if multiplayer:
            self.players.append(Player((SCREEN_WIDTH/2 + 100, SCREEN_HEIGHT-50), 2))
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
                        play_sound("gem.wav")
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
        self.DISPLAYSURF.blit(pygame.image.load(get_image("brick-background.jpg")), (0, 0))

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
        try:
            with open("highscores.json", "r") as f:
                highscore_data = load(f)
            highscore_data["scores"].append(player_score)
            with open("highscores.json", "w") as f:
                dump(highscore_data, f)
        except:
            highscore_data = {
                "scores": [player_score]
            }
            with open("highscores.json", "w") as f:
                dump(highscore_data, f)

    # Leader board screen displayed with the top players
    def high_score_screen(self):

        # get high score(s) from json file (if any)
        self.DISPLAYSURF.blit(pygame.image.load(get_image("brick-background.jpg")), (0,0))

        # load some data about top 3 high scores
        with open("highscores.json", "r") as f:
            highscores = sorted(load(f).get("scores", []), key=lambda x: x, reverse=True)

        # show high scores
        text = ""
        labels = ["First", "Second", "Third"]
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
