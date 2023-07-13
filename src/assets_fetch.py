from os.path import join

def get_asset(path: str, item: str) -> str:
    return join("assets", path, item)

def get_image(image: str) -> str:
    return get_asset("images", image)

def get_level_file(level: str) -> str:
    return get_asset("levels", level)

def get_sound(sound: str) -> str:
    return get_asset("sounds", sound)

def get_highscores() -> str:
    return get_asset("highscores", "highscores.json")