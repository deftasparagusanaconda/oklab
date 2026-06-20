import argparse, oklab

def oklab_main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", required=True)
    parser.add_argument("-o", required=True)
    parser.add_argument("colour", nargs="+")

    args = parser.parse_args()

    func = getattr(oklab, f"{args.i}_to_{args.o}")

    if len(args.colour) == 1:
        colour = args.colour[0]
    else:
        colour = tuple(map(float, args.colour))

    print(func(colour))

def oklch_main():
    parser = argparse.ArgumentParser()
    parser.add_argument("colour", nargs="+")

    args = parser.parse_args()

    if len(args.colour) == 1:
        print(f"({' '.join(map(str, oklab.hex_to_lch(args.colour[0])))})")
    else:
        print(oklab.lch_to_hex(tuple(map(float, args.colour))))
