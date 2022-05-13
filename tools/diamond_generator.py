from random import randint, choice

def main():
    inp = ""
    lst = []
    while inp == "":
        gen_x = randint(30, 1536)
        gen_y = choice([150, 235, 315, 397, 479, 561, 643, 725, 810])
        inp = input()
        lst.append({"x": gen_x, "y": gen_y})
    print(lst)

main()