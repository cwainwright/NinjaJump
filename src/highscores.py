from json import dump, load

from assets_fetch import get_highscores


class Highscores():
    def __init__(self) -> None:
        try:
            with open(get_highscores(), "r") as f:
                self.data = (load(f)).get("scores", [])
        except FileNotFoundError:
            self.data = []
            self.save_file()

    def __len__(self) -> int:
        return len(self.data)

    def __getitem__(self, index) -> int:
        return self.data[index]

    def save_file(self) -> bool:
        with open(get_highscores(), "w") as f:
            dump({"scores": self.data}, f)

    def add_highscore(self, highscore: int):
        if highscore > self.top():
            self.data.append(highscore)
        self.save_file()

    def top(self, num:int = 1) -> list:
        self.data.sort(key=lambda x: x, reverse=True)
        if num == 1:
            return self.data[0]
        elif len(self.data) <= num:
            return self.data
        else:
            return self.data[:num]
