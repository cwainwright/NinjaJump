from __future__ import annotations
from json import load

import sys
from pyclbr import Function
from typing import List, Union

import pygame
from pygame.locals import *
from assets_fetch import get_level_file

from constants import TITLESIZE, HEADERSIZE, BODYSIZE, HIGHSCORES, SCREEN_HEIGHT, SCREEN_WIDTH
from levels import Level
from objects import Image, Label, Player


"""
Contains all scenes appearing in game:
Start Screen
Main Loop (Game)
Help Screen
Leaderboard
"""

class Scene:

    def __init__(self, background: Image, labels: List[Label] = None, images: List[Image] = None):
        self.background = background
        self.labels = [] if labels is None else labels
        self.images = [] if images is None else images
        self.keypresses = {}

    def __call__(self, DISPLAYSURF) -> Union[Scene, Function]:
        self.background.show(DISPLAYSURF)
        for label in self.labels:
            label.show(DISPLAYSURF)
        for image in self.images:
            image.show(DISPLAYSURF)
        pygame.display.update()
        while True:
            for event in pygame.event.get():
                if event.type == QUIT:
                    return close_game
                for key, funcattr in self.keypresses.items():
                    if pygame.key.get_pressed()[key]:
                        func = funcattr["func"]
                        attr = funcattr["attr"]
                        return func(DISPLAYSURF, *attr)


# Similar to Scene, takes more inputs to initialise (and more actively updates)
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
        return self.score//20

    @property
    def current_level(self):
        try:
            return Level(self.level_data[self.level_index])
        except IndexError:
            return Level(self.levels)

    def increment_score(self):
        self.score += 1

    def __call__(self, DISPLAYSURF, multiplayer) -> Scene:
        self.players = [Player((SCREEN_WIDTH/2, SCREEN_HEIGHT-50))]
        if multiplayer:
            self.players.append(Player((SCREEN_WIDTH/2 + 100, SCREEN_HEIGHT-50), 2))

        self.level = self.current_level
        current_level_index = 0

        # While any player is alive
        while any([player.alive for player in self.players]):
            for event in pygame.event.get():
                if event.type == QUIT:
                    close_game()
            # Reload new level if index changes
            if current_level_index != self.level_index:
                current_level_index = self.level_index
                self.level = self.current_level
                for player in self.players:
                    player.reset_location()
            


        return GameOverScreen

def close_game():
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
        Label("_______________________________________________________________________________", (0, 370), None, size=BODYSIZE)
    ]
)

StartScreen = Scene(
    Image("loading-background.jpg"),
    [
        Label("Press 'h' for help", (10, 780), (255, 0, 0) , size=25),
        Label(HIGHSCORES.top(1), (750, 550), (255, 0, 0))
    ],
    [
        Image("ninja-run.png", (200 ,200)),
        Image("high-score.png", (370 ,400))
    ]
)

GameScreen = Game(
    Image("brick-background.jpg")
)

GameOverScreen = Scene(
    Image("loading-background.jpg"),
    [
        Label("Game Over", (240, 360), (0, 0, 0), TITLESIZE, True)
    ]
)

# Keypress Object Extensions
HelpScreen.keypresses.update({K_b: {"func":StartScreen, "attr":[]}})
StartScreen.keypresses.update({K_h: {"func":HelpScreen, "attr":[]}})
StartScreen.keypresses.update({K_1: {"func":GameScreen, "attr":[False]}})
StartScreen.keypresses.update({K_2: {"func":GameScreen, "attr":[True]}})