import argparse
from distutils.util import strtobool


def _split_list(value):
    """Split a string into a list of paths/patterns."""
    return [item for line in value.split("\n") for item in line.split()]


def parse_cmake_format_args():
    """Parse and return command line arguments for cmake-format."""
    parser = argparse.ArgumentParser(
        description="Parse cmake-format command line arguments"
    )

    # Formatting options
    formatting_group = parser.add_argument_group('Formatting Options')
    formatting_group.add_argument(
        "--line-width",
        type=int,
        metavar="WIDTH",
        help="Set maximum line width for formatting",
    )
    formatting_group.add_argument(
        "--tab-size",
        type=int,
        metavar="SIZE",
        help="Set the number of spaces for indentation",
    )
    formatting_group.add_argument(
        "--no-tab-indentation",
        action="store_true",
        help="Use spaces for indentation"
    )
    formatting_group.add_argument(
        "--comment-style",
        metavar="STYLE",
        help="Specify comment style for formatting"
    )
    formatting_group.add_argument(
        "--remove-empty",
        action="store_true",
        help="Remove empty lines"
    )

    # Operation mode options
    mode_group = parser.add_argument_group('Operation Mode')
    mode_group.add_argument(
        "--in-place",
        action="store_true",
        help="Modify input file(s) in place"
    )
    mode_group.add_argument(
        "--check",
        action="store_true",
        help="Check formatting without making changes"
    )
    mode_group.add_argument(
        "-i",
        "--inplace",
        type=lambda x: bool(strtobool(x)),
        default=False,
        help="Just fix files (`clang-format -i`) instead of returning a diff",
    )

    # Output options
    output_group = parser.add_argument_group('Output Options')
    output_group.add_argument(
        "--color",
        default="auto",
        choices=["auto", "always", "never"],
        help="show colored diff (default: auto)",
    )
    output_group.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        help="disable output, useful for the exit code",
    )

    # Processing options
    processing_group = parser.add_argument_group('Processing Options')
    processing_group.add_argument(
        "-j",
        metavar="N",
        type=int,
        default=0,
        help="run N clang-format jobs in parallel (default: number of CPUs + 1)",
    )
    processing_group.add_argument(
        "-e",
        "--exclude",
        type=_split_list,
        default=[],
        help="Folders to exclude from formatting check",
    )
    processing_group.add_argument(
        "--config",
        type=lambda x: bool(strtobool(x)),
        default=False,
        help="Use .cmake-format style configuration",
    )

    # Positional arguments
    parser.add_argument(
        "files",
        type=_split_list,
        metavar="file",
        help="Files or directories to process",
    )

    return parser.parse_args()
