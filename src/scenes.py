from __future__ import annotations
from json import load

import sys
from pyclbr import Function
from typing import List, Union

import pygame
from pygame.locals import *
from assets_fetch import get_level_file

from constants import LEVELUPNUM, TITLESIZE, HEADERSIZE, BODYSIZE, HIGHSCORES
from levels import Level
from objects import Image, Label


"""
Contains all scenes appearing in game:
Start Screen
Game
Help Screen
Leaderboard
"""

class Scene:

    def __init__(self, background: Image = None, views: List[Label] = None):
        self.background = background
        self.views = [] if views is None else views
        self.keypresses = {}

    def __call__(self, DISPLAYSURF) -> Union[Scene, Function]:
        if self.background is not None:
            self.background.show(DISPLAYSURF)
        for view in self.views:
            view.show(DISPLAYSURF)
        pygame.display.update()
        while True:
            for event in pygame.event.get():
                if event.type == QUIT:
                    return close_game
                for key, funcattr in self.keypresses.items():
                    if pygame.key.get_pressed()[key]:
                        func = funcattr["func"]
                        attr = funcattr.get("attr", [])
                        return func(DISPLAYSURF, *attr)

class Game:
    
    def __init__(self, background: Image):
        self.background = background
        self.score = 0
        
        with open(get_level_file("levels.json")) as f:
            self.level_data = load(f)
        
        try:
            with open(get_level_file("custom.json")) as f:
                self.custom_level_data = load(f)
        except FileNotFoundError:
            self.custom_level_data = None

        self.FPS = 60
        self.FramePerSec = pygame.time.Clock()

    @property
    def level_index(self):
        return self.score//LEVELUPNUM

    def current_level(self, multiplayer):
        try:
            return Level(self.level_data[self.level_index], multiplayer)
        except IndexError:
            if self.custom_level_data is None:
                return Level(self.level_data[len(self.level_data)-1], multiplayer)
            else:
                return Level(self.custom_level_data[self.level_index-len(self.level_data)], multiplayer)

    def increment_score(self):
        self.score += 1

    def __call__(self, DISPLAYSURF, multiplayer) -> Scene:

        self.score = 0

        self.level = self.current_level(multiplayer)
        current_level_index = 0

        # While any player is alive
        while any([player.alive for player in self.level.players]):
            for event in pygame.event.get():
                if event.type == QUIT:
                    close_game()
            # Reload new level if index changes
            if current_level_index != self.level_index:
                current_level_index = self.level_index
                self.level = self.current_level(multiplayer)
                for player in self.level.players:
                    player.reset_location()
            
            self.render(DISPLAYSURF)

            for player in self.level.players:
                player.move()

            for disk in self.level.disks:
                disk.move()

            for spear in self.level.spears:
                spear.move()

            self.check_collisions()

        HIGHSCORES.add_highscore(self.score)
        return GameOverScreen

    def check_collisions(self):
        for player in self.level.players:
            # Platform collisions
            for platform in self.level.platforms:
                rect = platform.get_rect()
                if player.rect.colliderect(rect):
                    player.wallCollision(rect)
            
            for spike in self.level.spikes:
                if player.rect.colliderect(spike.get_rect()):
                    player.kill()

            for spear in self.level.spears:
                if player.rect.colliderect(spear.get_rect()):
                    player.kill()

            for disk in self.level.disks:
                if player.rect.colliderect(disk.get_rect()):
                    player.kill()

            for diamond in self.level.diamonds:
                if player.rect.colliderect(diamond.get_rect()):
                    self.increment_score()
                    self.level.new_diamond(diamond)

    def render(self, DISPLAYSURF):
        self.background.show(DISPLAYSURF)

        for platform in self.level.platforms:
            platform.draw(DISPLAYSURF)

        for spike in self.level.spikes:
            spike.draw(DISPLAYSURF)
        
        for spear in self.level.spears:
            spear.draw(DISPLAYSURF)

        for disk in self.level.disks:
            disk.draw(DISPLAYSURF)

        for diamond in self.level.diamonds:
            diamond.draw(DISPLAYSURF)

        for player in self.level.players:
            player.draw(DISPLAYSURF)

        Label(f"Score: {self.score}", (60, 60)).show(DISPLAYSURF)

        pygame.display.update()
        self.FramePerSec.tick(self.FPS)

def close_game(*args):
    pygame.quit
    sys.exit()

# Scenes
HelpScreen = Scene(
    Image("brick-background.jpg"),
    [
        Label("Help Menu", (360, 60), (0, 0, 0), size=TITLESIZE, shadow=True),
        Label("1 - One Player", (105, 255), (0, 0, 0), size=BODYSIZE, shadow=True),
        Label("B - Back", (585, 255), (0, 0, 0), size=BODYSIZE, shadow=True),
        Label("L - Leaderboard", (1075, 255), (0, 0, 0), size=BODYSIZE, shadow=True),
        Label("2 - Two Player", (105, 355), (0, 0, 0), size=BODYSIZE, shadow=True),
        Label("P - Pause Menu", (1070, 355), (0, 0, 0), size=BODYSIZE, shadow=True),
        Label("H - Help Menu", (585, 355), (0, 0, 0), size=BODYSIZE, shadow=True),
        Label("Player One", (155, 455), (0, 0, 0), size=HEADERSIZE, shadow=True),
        Label("^ - Jump", (155, 555), (0, 0, 0), size=BODYSIZE, shadow=True),
        Label("> - Move Right", (155, 655), (0, 0, 0), size=BODYSIZE, shadow=True),
        Label("< - Move Left", (155, 755), (0, 0, 0), size=BODYSIZE, shadow=True),
        Label("Player Two", (905, 455), (0, 0, 0), size=HEADERSIZE, shadow=True),
        Label("W - Jump", (905, 555), (0, 0, 0), size=BODYSIZE, shadow=True),
        Label("D - Move Right", (905, 655), (0, 0, 0), size=BODYSIZE, shadow=True),
        Label("A - Move Left", (905, 755), (0, 0, 0), size=BODYSIZE, shadow=True),
    ]
)

StartScreen = Scene(
    Image("loading-background.jpg"),
    [
        Label("Press 'h' for help", (10, 780), (255, 0, 0) , size=25),
        Label(HIGHSCORES.top(1), (750, 550), (255, 0, 0)),
        Image("ninja-run.png", (200 ,200)),
        Image("high-score.png", (370 ,400))
    ]
)

GameScreen = Game(
    Image("brick-background.jpg")
)

GameOverScreen = Scene(
    None,
    [
        Label("Game Over", (300, 360), (0, 0, 0), TITLESIZE, True)
    ]
)

LeaderboardScreen = Scene(
    Image("brick-background.jpg"),
    [
        Label(f"{i+1}:     {highscore}", (550, 350 + (162 * i)), None, HEADERSIZE)
        for i, highscore in enumerate(HIGHSCORES.top(3))
    ]
    + [
        Label("Highscores", (350, 60), (0, 0, 0), TITLESIZE, True)
    ]
)

# Keypress Object Extensions
StartScreen.keypresses.update({
    K_h: {"func":HelpScreen},
    K_l: {"func":LeaderboardScreen},
    K_1: {"func":GameScreen, "attr":[False]},
    K_2: {"func":GameScreen, "attr":[True]}
})
HelpScreen.keypresses.update({
    K_b: {"func":StartScreen},
    K_l: {"func":LeaderboardScreen},
    K_1: {"func":GameScreen, "attr":[False]},
    K_2: {"func":GameScreen, "attr":[True]}
})
LeaderboardScreen.keypresses.update({
    K_b: {"func":StartScreen},
    K_h: {"func":HelpScreen},
    K_1: {"func":GameScreen, "attr":[False]},
    K_2: {"func":GameScreen, "attr":[True]}
})
GameOverScreen.keypresses.update({K_b: {"func":StartScreen}})
