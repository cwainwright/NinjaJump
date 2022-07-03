from os.path import join

def get_asset(path, item = None):
    if item is None:
        return join("assets", path)
    else:
        return join("assets", path, item)

def get_image(image=None):
    return get_asset("images", image)

def get_level_file(level=None):
    return get_asset("levels", level)

def get_sound(sound=None):
    return get_asset("sounds", sound)

def get_highscores():
    return get_asset("highscores", "highscores.json")