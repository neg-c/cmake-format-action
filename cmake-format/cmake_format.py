import io
import subprocess
import difflib
from output import print_diff
from output import colorize
from output import bold_red
from output import print_trouble
from argparse import Namespace
import multiprocessing


class DiffError(Exception):
    def __init__(self, message, errs=None):
        super(DiffError, self).__init__(message)
        self.errs = errs or []


class UnexpectedError(Exception):
    def __init__(self, message, exc=None):
        super(UnexpectedError, self).__init__(message)
        self.formatted_traceback = traceback.format_exc()
        self.exc = exc


class ExitStatus:
    SUCCESS = 0
    DIFF = 1
    TROUBLE = 2


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
    if args.config:
        invocation.append("--config=.cmake-format")
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
