#!/usr/bin/env python
import sys
import signal
import multiprocessing
from functools import partial
from typing import Optional

from arg_parser import parse_cmake_format_args
from file_operations import list_files
from cmake_format import (
    run_cmake_format_diff_wrapper,
    ExitStatus,
    DiffError,
    UnexpectedError
)
from output import print_diff, print_trouble

def setup_signal_handlers() -> None:
    """Configure signal handlers for graceful termination."""
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    try:
        signal.SIGPIPE
    except AttributeError:
        # SIGPIPE does not exist on Windows
        pass
    else:
        signal.signal(signal.SIGPIPE, signal.SIG_DFL)

def determine_color_output(args) -> tuple[bool, bool]:
    """Determine if stdout and stderr should use colors.
    
    Args:
        args: Parsed command line arguments
        
    Returns:
        Tuple of (use_color_stdout, use_color_stderr)
    """
    if args.color == "always":
        return True, True
    elif args.color == "auto":
        return sys.stdout.isatty(), sys.stderr.isatty()
    return False, False

def process_files(args, files: list[str], colored_stdout: bool, colored_stderr: bool) -> int:
    """Process all files with cmake-format.
    
    Args:
        args: Parsed command line arguments
        files: List of files to process
        colored_stdout: Whether to use colors in stdout
        colored_stderr: Whether to use colors in stderr
        
    Returns:
        Exit status code
    """
    if not files:
        print_trouble("No files found", use_colors=colored_stderr)
        return ExitStatus.TROUBLE

    if not args.quiet:
        print(f"Processing {len(files)} files: {', '.join(files)}")

    # Determine number of parallel jobs
    njobs = min(len(files), args.j if args.j > 0 else multiprocessing.cpu_count() + 1)

    retcode = ExitStatus.SUCCESS
    if njobs == 1:
        # Single process mode - better for debugging
        it = (run_cmake_format_diff_wrapper(args, file) for file in files)
        pool = None
    else:
        # Parallel processing mode
        pool = multiprocessing.Pool(njobs)
        it = pool.imap_unordered(partial(run_cmake_format_diff_wrapper, args), files)

    try:
        for outs, errs in it:
            sys.stderr.writelines(errs)
            if not outs:
                continue
            if not args.inplace:
                if not args.quiet:
                    print_diff(outs, use_color=colored_stdout)
                if retcode == ExitStatus.SUCCESS:
                    retcode = ExitStatus.DIFF
    except DiffError as e:
        print_trouble(str(e), use_colors=colored_stderr)
        sys.stderr.writelines(e.errs)
        retcode = ExitStatus.TROUBLE
    except UnexpectedError as e:
        print_trouble(str(e), use_colors=colored_stderr)
        sys.stderr.write(e.formatted_traceback)
        retcode = ExitStatus.TROUBLE
        if pool:
            pool.terminate()
    finally:
        if pool:
            pool.close()
            pool.join()

    return retcode

def main() -> int:
    """Main entry point for cmake-format.
    
    Returns:
        Exit status code
    """
    args = parse_cmake_format_args()
    setup_signal_handlers()
    
    colored_stdout, colored_stderr = determine_color_output(args)
    files = list_files(args.files, exclude=args.exclude)
    
    return process_files(args, files, colored_stdout, colored_stderr)

if __name__ == "__main__":
    sys.exit(main())
