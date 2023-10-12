#!/usr/bin/env python
from arg_parser import parse_cmake_format_args
from file_operations import list_files
from cmake_format import run_cmake_format_diff_wrapper, ExitStatus, print_diff
from output import print_trouble
from functools import partial
import sys
import signal
import multiprocessing


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
