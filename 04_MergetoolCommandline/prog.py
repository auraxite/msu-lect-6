import cmd
import shlex
import cowsay


def format_output(left, right):
    left_lines = left.splitlines()
    right_lines = right.splitlines()

    h = max(len(left_lines), len(right_lines))
    left_lines = ([""] * (h - len(left_lines))) + left_lines
    right_lines = ([""] * (h - len(right_lines))) + right_lines

    left_width = max((len(line) for line in left_lines), default=0)

    out = []
    for l, r in zip(left_lines, right_lines):
        out.append(l.ljust(left_width) + " " + r)

    return "\n".join(out)


class twocows(cmd.Cmd):
    prompt = "twocows> "

    def do_list_cows(self, arg):
        '''list all cows'''

        if (shlex.split(arg)):
            return
        print(" ".join(cowsay.list_cows()))

    def do_make_bubble(self, arg):
        '''print msg in a bubble'''

        args = shlex.split(arg)
        print(cowsay.make_bubble(" ".join(args)))

    def do_cowsay(self, arg):
        '''cows speak!'''

        args = shlex.split(arg)

        if ("reply" not in args):
            return
        i = args.index("reply")
        left = args[:i]
        right = args[i + 1:]
        if ((len(left) < 1) or (len(right) < 1)):
            return

        msg1, cow1, p1 = self.parse(left)
        msg2, cow2, p2 = self.parse(right)

        if ((msg1 is None) or (msg2 is None)):
            return

        out1 = cowsay.cowsay(
            msg1,
            cow=cow1,
            eyes=p1.get("eyes", "oo"),
            tongue=p1.get("tongue", "  "),
        )

        out2 = cowsay.cowsay(
            msg2,
            cow=cow2,
            eyes=p2.get("eyes", "oo"),
            tongue=p2.get("tongue", "  "),
        )

        print(format_output(out1, out2))

    def do_cowthink(self, arg):
        '''cows think!'''

        args = shlex.split(arg)

        if ("reply" not in args):
            return
        i = args.index("reply")
        left = args[:i]
        right = args[i + 1:]
        if ((len(left) < 1) or (len(right) < 1)):
            return

        msg1, cow1, p1 = self.parse(left)
        msg2, cow2, p2 = self.parse(right)

        if ((msg1 is None) or (msg2 is None)):
            return

        out1 = cowsay.cowthink(
            msg1,
            cow=cow1,
            eyes=p1.get("eyes", "oo"),
            tongue=p1.get("tongue", "  "),
        )

        out2 = cowsay.cowthink(
            msg2,
            cow=cow2,
            eyes=p2.get("eyes", "oo"),
            tongue=p2.get("tongue", "  "),
        )

        print(format_output(out1, out2))

    def parse(self, parts):
        msg = parts[0]
        cow = "default"
        params = {}
        start = 1

        if ((len(parts) >= 2) and ("=" not in parts[1])):
            prefix = parts[1]
            cows = cowsay.list_cows()

            if (prefix in cows):
                cow = prefix
            else:
                matches = [name for name in cows if name.startswith(prefix)]

                if (len(matches) == 1):
                    cow = matches[0]
                else:
                    return None, None, None

            start = 2

        if (start + 1 <= len(parts)):
            for t in parts[start:]:
                if ("=" not in t):
                    return None, None, None

                k, v = t.split("=", 1)

                if (k not in ("eyes", "tongue")):
                    return None, None, None

                params[k] = v

        return msg, cow, params


if (__name__ == "__main__"):
    twocows().cmdloop()