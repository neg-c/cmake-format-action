import sys


def bold_red(s):
    return "\x1b[1m\x1b[31m" + s + "\x1b[0m" + "\n"


def print_trouble(message, use_colors):
    error_text = "error:"
    if use_colors:
        error_text = bold_red(error_text)
    print("{} {}".format(error_text, message), file=sys.stderr)


def print_diff(diff_lines, use_color):
    if use_color:
        diff_lines = colorize(diff_lines)
    if sys.version_info[0] < 3:
        sys.stdout.writelines((l.encode("utf-8") for l in diff_lines))
    else:
        sys.stdout.writelines(diff_lines)


def colorize(diff_lines):
    def bold(s):
        return "\x1b[1m" + s + "\x1b[0m"

    def cyan(s):
        return "\x1b[36m" + s + "\x1b[0m"

    def green(s):
        return "\x1b[32m" + s + "\x1b[0m" + "\n"

    def red(s):
        return "\x1b[31m" + s + "\x1b[0m" + "\n"

    for line in diff_lines:
        if line[:4] in ["--- ", "+++ "]:
            yield bold(line)
        elif line.startswith("@@ "):
            yield cyan(line)
        elif line.startswith("+"):
            yield green(line)
        elif line.startswith("-"):
            yield red(line)
        else:
            yield line + "\n"
