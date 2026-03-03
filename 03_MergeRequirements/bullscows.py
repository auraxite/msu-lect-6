import argparse
import random
import urllib.request
from collections import Counter
from cowsay import cowsay


def bullscows(guess: str, secret: str) -> tuple[int, int]:
    if len(guess) != len(secret):
        raise ValueError("У слов должна быть одинаковая длина")
    bulls = sum(g == s for g, s in zip(guess, secret))

    g_rest = [g for g, s in zip(guess, secret) if g != s]
    s_rest = [s for g, s in zip(guess, secret) if g != s]
    cows = sum((Counter(g_rest) & Counter(s_rest)).values())

    return bulls, cows


def gameplay(ask, inform, words: list[str]) -> int:
    secret = random.choice(words)
    tries = 0

    while True:
        guess = ask("Введите слово: ", words)
        tries += 1

        try:
            b, c = bullscows(guess, secret)
        except ValueError as e:
            print(e)
            continue
        inform("Быки: {}, Коровы: {}", b, c)

        if guess == secret:
            return tries


def ask(prompt: str, valid: list[str] = None) -> str:
    while True:
        s = input(prompt).strip().lower()
        if (not valid) or (s in valid):
            return s
        print("Недопустимое слово")


def inform(format_string: str, bulls: int, cows: int) -> None:
    msg = cowsay(format_string.format(bulls, cows))
    print(msg)


def main() -> int:
    parser = argparse.ArgumentParser(prog="bullscows")
    parser.add_argument("dictionary")
    parser.add_argument("length", nargs="?", type=int, default=5)
    args = parser.parse_args()

    src = args.dictionary
    if src.startswith("http"):
        with urllib.request.urlopen(src) as r:
            text = r.read().decode("utf-8", errors="replace")
    else:
        with open(src, "r", encoding="utf-8", errors="replace") as f:
            text = f.read()

    raw = [t.strip().lower() for t in text.split() if t.strip()]
    words = []
    seen = set()
    L = args.length
    for w in raw:
        if (len(w) != L) or (w in seen) or (not w.isalpha()):
            continue
        seen.add(w)
        words.append(w)
    if not words:
        print("Список слов пуст")
        return 1

    tries = gameplay(ask, inform, words)
    print(f"Попыток: {tries}")
    return 0


if __name__ == "__main__":
    main()