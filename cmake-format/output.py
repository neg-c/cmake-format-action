import sys
from typing import List, Iterator, Union

class ColorCodes:
    """ANSI color codes for terminal output."""
    RESET = "\x1b[0m"
    BOLD = "\x1b[1m"
    RED = "\x1b[31m"
    GREEN = "\x1b[32m"
    CYAN = "\x1b[36m"
    YELLOW = "\x1b[33m"

def print_trouble(message: str, use_colors: bool = False) -> None:
    """Print an error message to stderr.
    
    Args:
        message: The error message to print
        use_colors: Whether to use colored output
    """
    error_text = "error:"
    if use_colors:
        error_text = f"{ColorCodes.BOLD}{ColorCodes.RED}{error_text}{ColorCodes.RESET}"
    
    print(f"{error_text} {message}", file=sys.stderr)

def print_diff(diff_lines: List[str], use_color: bool = False) -> None:
    """Print a diff to stdout with optional coloring.
    
    Args:
        diff_lines: The lines of the diff to print
        use_color: Whether to use colored output
    """
    if use_color:
        diff_lines = list(colorize(diff_lines))
    
    if diff_lines:
        header = "\nRequired formatting changes:\n" + "=" * 50 + "\n"
        if use_color:
            header = f"{ColorCodes.YELLOW}{header}{ColorCodes.RESET}"
        sys.stdout.write(header)
    
    if sys.version_info[0] < 3:
        sys.stdout.writelines((line.encode("utf-8") for line in diff_lines))
    else:
        sys.stdout.writelines(diff_lines)
    
    if diff_lines:
        sys.stdout.write("\n")

def colorize(diff_lines: List[str]) -> Iterator[str]:
    """Add ANSI color codes to diff lines.
    
    Args:
        diff_lines: The lines to colorize
        
    Returns:
        Iterator of colorized lines
        
    Note:
        - Diff headers are bold
        - Added lines are green
        - Removed lines are red
        - Changed sections are cyan
    """
    for line in diff_lines:
        if line.startswith(("--- ", "+++ ")):
            yield f"{ColorCodes.YELLOW}{ColorCodes.BOLD}{line}{ColorCodes.RESET}\n"
        elif line.startswith("@@"):
            yield f"{ColorCodes.CYAN}{line}{ColorCodes.RESET}\n"
        elif line.startswith("+"):
            yield f"{ColorCodes.GREEN}{line.rstrip()}{ColorCodes.RESET}\n"
        elif line.startswith("-"):
            yield f"{ColorCodes.RED}{line.rstrip()}{ColorCodes.RESET}\n"
        else:
            yield f"{line}\n"
