import io
import subprocess
import difflib
from output import print_diff, colorize, print_trouble
from exceptions import DiffError, UnexpectedError

class ExitStatus:
    """Exit status code constants."""
    SUCCESS = 0
    DIFF = 1
    TROUBLE = 2

def make_diff(file, original, reformatted):
    """Generate a unified diff between original and reformatted content."""
    return list(
        difflib.unified_diff(
            original,
            reformatted,
            fromfile=f"{file}\t(original)",
            tofile=f"{file}\t(reformatted)",
            n=3,
        )
    )

def run_cmake_format_diff_wrapper(args, file):
    """Wrapper function to handle exceptions during cmake-format execution."""
    try:
        return run_cmake_format_diff(args, file)
    except DiffError:
        raise
    except Exception as e:
        raise UnexpectedError(f"{file}: {e.__class__.__name__}: {e}", e)

def run_cmake_format_diff(args, file):
    """Run cmake-format on a single file and return the diff."""
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
