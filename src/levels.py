from copy import deepcopy
from random import choice, randint
from typing import List
from audio import play_sound

from constants import SCREEN_HEIGHT, SCREEN_WIDTH
from objects import Diamond, Disk, Platform, Player, Spear, Spike

""" Json data loaded """
class Level:
    def __init__(self, level_data: dict, multiplayer):
        self.level_data = level_data

        # create platforms
        self.platforms: List[Platform] = []
        for platform in self.level_data.get("platforms"):
            self.platforms.append(Platform(
                (platform["x"], platform["y"]), platform["l"], platform["w"]
            ))

        # create diamonds
        self.diamonds: List[Diamond] = []
        diamond_list = deepcopy(self.level_data.get("diamonds"))
        for _ in range(5):
            diamond = choice(diamond_list)
            try:
                diamond_list.remove(diamond)
            except ValueError:
                pass
            else:
                self.diamonds.append(Diamond(
                    (diamond["x"], diamond["y"])
                ))
        del diamond_list

        # create spikes
        self.spikes: List[Spike] = []
        for spike in self.level_data["spikes"]:
            self.spikes.append(Spike(
                (spike["x"], spike["y"])
            ))

        # create disks
        self.disks: List[Disk] = []
        for disk in self.level_data["disks"]:
            self.disks.append(Disk(
                (disk["x"], disk["y"])
            ))

        # create spears
        self.spears: List[Spear] = []
        for _ in range(2):
            self.spears.append(Spear((randint(0, SCREEN_WIDTH),0)))


        self.players = [Player((SCREEN_WIDTH/2, SCREEN_HEIGHT-50))]
        if multiplayer:
            self.players.append(Player((SCREEN_WIDTH/2 + 100, SCREEN_HEIGHT-50), 2))
            
    def new_diamond(self, old_diamond):
        self.diamonds.remove(old_diamond)
        play_sound("gem.wav")
        diamond = choice(self.level_data.get("diamonds"))
        self.diamonds.append(Diamond(
            (diamond["x"], diamond["y"])
        ))