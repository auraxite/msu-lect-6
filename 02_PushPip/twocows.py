import argparse
import cowsay


def main() -> None:
    parser = argparse.ArgumentParser(prog="twocows.py")

    parser.add_argument("-f", dest="cow1", default="default")
    parser.add_argument("-e", dest="eyes1", default="oo")
    parser.add_argument("-T", dest="tongue1", default="  ")

    parser.add_argument("-F", dest="cow2", default="default")
    parser.add_argument("-E", dest="eyes2", default="oo")
    parser.add_argument("-N", dest="tongue2", default="  ")

    parser.add_argument("-W", dest="width", type=int, default=40)
    parser.add_argument("-n", dest="wrap_text", action="store_false")

    parser.add_argument("message1")
    parser.add_argument("message2")
    args = parser.parse_args()

    left = cowsay.cowsay(
        message=args.message1,
        cow=args.cow1,
        eyes=args.eyes1,
        tongue=args.tongue1,
        width=args.width,
        wrap_text=args.wrap_text,
    )
    right = cowsay.cowsay(
        message=args.message2,
        cow=args.cow2,
        eyes=args.eyes2,
        tongue=args.tongue2,
        width=args.width,
        wrap_text=args.wrap_text,
    )

    print(left)
    print(right)


if __name__ == "__main__":
    main()