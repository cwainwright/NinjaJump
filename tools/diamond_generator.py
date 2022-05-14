from random import randint, choice
import json

def main():
    """Used to generate additional diamonds for new-style levels."""
    inp = ""
    lst = []
    while inp == "":
        gen_x = randint(30, 1536)
        gen_y = choice([150, 235, 315, 397, 479, 561, 643, 725, 810])
        inp = input()
        lst.append({"x": gen_x, "y": gen_y})
    print(json.dumps(lst))

main()