from os.path import join

def get_asset(path, item):
    return join("assets", path, item)

def get_image(image):
    return get_asset("images", image)

def get_level(level):
    return get_asset("levels", level)

def get_sound(sound):
    return get_asset("sounds", sound)

def get_highscores():
    return get_asset("highscores", "highscores.json")