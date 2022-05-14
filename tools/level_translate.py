from json import load, dump
from copy import deepcopy

def main():
    """Used to translate old-style levels to new-style levels."""
    new_levels = []
    level_template = {
        "platforms": [], "spikes": [], "diamonds": [],
        "disks": [], "players": []
    }
    with open("levels.json", "r") as old_level_file:
        old_levels = load(old_level_file)
    levels = ["_One","_Two","_Three"]
    for level in levels:
        level_data_old = old_levels["Round"+level]
        level_data_new = deepcopy(level_template)

        # Platorms Translation
        for index, platformx in enumerate(level_data_old["Platform_x"]):
            platformy = level_data_old["Platform_y"][index]
            platforml = level_data_old["Platform_length"][index]
            platformw = level_data_old["Platform_width"]
            level_data_new["platforms"].append({
                "x": platformx, "y": platformy, "l": platforml, "w": platformw
            })

        # Spikes Translation
        for index, spikex in enumerate(level_data_old["Spikes_x"]):
            try:
                spikey = level_data_old["Spikes_y"][index]
                level_data_new["spikes"].append({
                    "x": spikex, "y": spikey
                })
            except IndexError:
                continue

        # Diamonds Translation
        for index, diamondx in enumerate(level_data_old["Diamond_x"]):
            try:
                diamondy = level_data_old["Diamond_y"][index]
                level_data_new["diamonds"].append({
                    "x": diamondx, "y": diamondy
                })
            except IndexError:
                continue

        # Disks Translation
        for index, diskx in enumerate(level_data_old["Disk_x"]):
            try:
                disky = level_data_old["Disk_y"][index]
                level_data_new["disks"].append({
                    "x": diskx, "y": disky
                })
            except IndexError:
                continue
            
        # Players Translation
        # Player 1
        level_data_new["players"].append({
            "x": level_data_old["Ninja_One_x"],
            "y": level_data_old["Ninja_y"],
        })

        # Player 2
        level_data_new["players"].append({
            "x": level_data_old["Ninja_Two_x"][1],
            "y": level_data_old["Ninja_y"],
        })
        
        new_levels.append(level_data_new)

    
    with open("levels_new.json", "w") as new_level_file:
        dump(new_levels, new_level_file, indent=4)

main()