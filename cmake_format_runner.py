#!/usr/bin/env python
"""A wrapper script around cmake-format for linting multiple CMake files.

This script runs cmake-format on multiple CMake files, producing a diff output and a sensible exit code.

"""

import argparse
import difflib
import fnmatch
import io
import os
import subprocess
import sys
import traceback
import signal
import multiprocessing
from functools import partial
from distutils.util import strtobool


class ExitStatus:
    SUCCESS = 0
    DIFF = 1
    TROUBLE = 2


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


class DiffError(Exception):
    def __init__(self, message, errs=None):
        super(DiffError, self).__init__(message)
        self.errs = errs or []


class UnexpectedError(Exception):
    def __init__(self, message, exc=None):
        super(UnexpectedError, self).__init__(message)
        self.formatted_traceback = traceback.format_exc()
        self.exc = exc


def make_diff(file, original, reformatted):
    return list(
        difflib.unified_diff(
            original,
            reformatted,
            fromfile="{}\t(original)".format(file),
            tofile="{}\t(reformatted)".format(file),
            n=3,
        )
    )


def list_files(files, recursive=False, exclude=None):
    cmake_files = []

    if exclude is None:
        exclude = []

    for root, dirs, files in os.walk(files):
        dirs[:] = [
            d
            for d in dirs
            if not any(fnmatch.fnmatch(d, pattern) for pattern in exclude)
        ]
        files[:] = [
            f
            for f in files
            if not any(fnmatch.fnmatch(f, pattern) for pattern in exclude)
        ]

        for file in files:
            if file.lower().endswith(".cmake") or file == "CMakeLists.txt":
                cmake_files.append(os.path.join(root, file))

    return cmake_files


def run_cmake_format_diff_wrapper(args, file):
    try:
        ret = run_cmake_format_diff(args, file)
        return ret
    except DiffError:
        raise
    except Exception as e:
        raise UnexpectedError(f"{file}: {e.__class__.__name__}: {e}", e)


def run_cmake_format_diff(args, file):
    with io.open(file, "r", encoding="utf-8") as f:
        original = f.read()

    invocation = ["cmake-format", file]
    if args.inplace:
        invocation.append("-i")

    try:
        result = subprocess.run(
            invocation,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
            input=original,
            check=True,
        )
        outs = result.stdout.splitlines()
        errs = result.stderr.splitlines()
    except subprocess.CalledProcessError as exc:
        errs = exc.stderr.splitlines()
        raise DiffError(
            f"Command '{subprocess.list2cmdline(invocation)}' returned non-zero exit status {exc.returncode}",
            errs,
        )
    return make_diff(file, original.splitlines(), outs), errs


import argparse


def parse_cmake_format_args():
    parser = argparse.ArgumentParser(
        description="Parse cmake-format command line arguments"
    )

    parser.add_argument(
        "--in-place", action="store_true", help="Modify input file(s) in place"
    )
    parser.add_argument(
        "--recursive",
        action="store_true",
        help="Recursively process files in directories",
    )
    parser.add_argument(
        "--check", action="store_true", help="Check formatting without making changes"
    )
    parser.add_argument(
        "--inconclusive",
        action="store_true",
        help="Display inconclusive formatting rules",
    )
    parser.add_argument(
        "--line-width",
        type=int,
        metavar="WIDTH",
        help="Set maximum line width for formatting",
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
        "--style", help="Formatting style to use (default: file)", default="file"
    )

    parser.add_argument(
        "-i",
        "--inplace",
        type=lambda x: bool(strtobool(x)),
        default=False,
        help="Just fix files (`clang-format -i`) instead of returning a diff",
    )

    parser.add_argument("files", metavar="file")

    args = parser.parse_args()
    return args


def main():
    args = parse_cmake_format_args()

    signal.signal(signal.SIGINT, signal.SIG_DFL)
    try:
        signal.SIGPIPE
    except AttributeError:
        # compatibility, SIGPIPE does not exist on Windows
        pass
    else:
        signal.signal(signal.SIGPIPE, signal.SIG_DFL)

    colored_stdout = False
    colored_stderr = False
    if args.color == "always":
        colored_stdout = True
        colored_stderr = True
    elif args.color == "auto":
        colored_stdout = sys.stdout.isatty()
        colored_stderr = sys.stderr.isatty()

    retcode = ExitStatus.SUCCESS

    excludeDir = ["build"]
    files = list_files(args.files, recursive=True, exclude=excludeDir)

    if not files:
        print_trouble("No files found", use_colors=colored_stderr)
        return ExitStatus.TROUBLE

    if not args.quiet:
        print("Processing %s files: %s" % (len(files), ", ".join(files)))

    njobs = args.j
    if njobs == 0:
        njobs = multiprocessing.cpu_count() + 1
    njobs = min(len(files), njobs)

    if njobs == 1:
        # execute directly instead of in a pool,
        # less overhead, simpler stacktraces
        it = (run_cmake_format_diff_wrapper(args, file) for file in files)
        pool = None
    else:
        pool = multiprocessing.Pool(njobs)
        it = pool.imap_unordered(partial(run_cmake_format_diff_wrapper, args), files)
    while True:
        try:
            outs, errs = next(it)
        except StopIteration:
            break
        except DiffError as e:
            print_trouble(str(e), use_colors=colored_stderr)
            retcode = ExitStatus.TROUBLE
            sys.stderr.writelines(e.errs)
        except UnexpectedError as e:
            print_trouble(str(e), use_colors=colored_stderr)
            sys.stderr.write(e.formatted_traceback)
            retcode = ExitStatus.TROUBLE
            # stop at the first unexpected error,
            # something could be very wrong,
            # don't process all files unnecessarily
            if pool:
                pool.terminate()
            break
        else:
            sys.stderr.writelines(errs)
            if outs == []:
                continue
            if not args.inplace:
                if not args.quiet:
                    print_diff(outs, use_color=colored_stdout)
                if retcode == ExitStatus.SUCCESS:
                    retcode = ExitStatus.DIFF

    return retcode


if __name__ == "__main__":
    sys.exit(main())
