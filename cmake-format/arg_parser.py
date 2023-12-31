import argparse
from distutils.util import strtobool


def parse_cmake_format_args():
    parser = argparse.ArgumentParser(
        description="Parse cmake-format command line arguments"
    )

    parser.add_argument(
        "--in-place", action="store_true", help="Modify input file(s) in place"
    )
    parser.add_argument(
        "--check", action="store_true", help="Check formatting without making changes"
    )
    parser.add_argument(
        "--line-width",
        type=int,
        metavar="WIDTH",
        help="Set maximum line width for formatting",
    )
    parser.add_argument(
        "-e",
        "--exclude",
        type=lambda x: [pattern for line in x.split("\n") for pattern in line.split()],
        default=[],
    )
    parser.add_argument(
        "--tab-size",
        type=int,
        metavar="SIZE",
        help="Set the number of spaces for indentation",
    )
    parser.add_argument(
        "--no-tab-indentation", action="store_true", help="Use spaces for indentation"
    )
    parser.add_argument(
        "--comment-style", metavar="STYLE", help="Specify comment style for formatting"
    )
    parser.add_argument(
        "--remove-empty", action="store_true", help="Remove empty lines"
    )
    parser.add_argument(
        "--color",
        default="auto",
        choices=["auto", "always", "never"],
        help="show colored diff (default: auto)",
    )
    parser.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        help="disable output, useful for the exit code",
    )
    parser.add_argument(
        "-j",
        metavar="N",
        type=int,
        default=0,
        help="run N clang-format jobs in parallel" " (default number of cpus + 1)",
    )

    parser.add_argument(
        "--config",
        type=lambda x: bool(strtobool(x)),
        default=False,
        help="Formatting style to use (default: file)",
    )

    parser.add_argument(
        "-i",
        "--inplace",
        type=lambda x: bool(strtobool(x)),
        default=False,
        help="Just fix files (`clang-format -i`) instead of returning a diff",
    )

    parser.add_argument(
        "files",
        type=lambda x: [path for line in x.split("\n") for path in line.split()],
        metavar="file",
    )

    args = parser.parse_args()
    return args
