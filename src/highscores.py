from json import dump, load

from assets_fetch import get_highscores


class Highscores():
    def __init__(self) -> None:
        try:
            with open(get_highscores(), "r") as f:
                self.data: list[int] = (load(f)).get("scores", [])
        except FileNotFoundError:
            self.data: list[int] = []
            self.save_file()

    def __len__(self) -> int:
        return len(self.data)

    def __getitem__(self, index: int) -> int:
        return int(self.data[index])

    def save_file(self) -> bool:
        with open(get_highscores(), "w") as f:
            dump({"scores": self.data}, f)
        return True

    def add_highscore(self, highscore: int):
        if highscore > self.top()[0]:
            self.data.append(highscore)
        self.save_file()

    def top(self, num:int = 1) -> list[int]:
        self.data.sort(key=lambda x: x, reverse=True)
        if len(self.data) <= num:
            return [int(datapoint) for datapoint in self.data]
        return [int(datapoint) for datapoint in self.data[:num]]
