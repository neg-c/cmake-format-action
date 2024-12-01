import os
import fnmatch
from typing import List, Optional

def list_files(paths: List[str], exclude: Optional[List[str]] = None) -> List[str]:
    """Find all CMake files in the given paths while respecting exclusions.
    
    Args:
        paths: List of file or directory paths to search
        exclude: List of patterns to exclude from the search
        
    Returns:
        List of found CMake file paths
        
    Note:
        Always excludes 'build' directory by default
    """
    cmake_files = []
    exclude_patterns = list(exclude) if exclude else []
    exclude_patterns.append('build')  # Always exclude build directory

    for path in paths:
        if os.path.isfile(path):
            if _is_cmake_file(path):
                cmake_files.append(path)
            continue

        for root, dirs, files in os.walk(path):
            # Filter directories based on exclude patterns
            dirs[:] = [
                d for d in dirs
                if not any(fnmatch.fnmatch(d, pattern) for pattern in exclude_patterns)
            ]

            # Filter and add CMake files
            cmake_files.extend(
                os.path.join(root, f) for f in files
                if _is_cmake_file(f) and not any(
                    fnmatch.fnmatch(f, pattern) for pattern in exclude_patterns
                )
            )

    return sorted(cmake_files)  # Sort for consistent ordering

def _is_cmake_file(filename: str) -> bool:
    """Check if a file is a CMake file.
    
    Args:
        filename: Name of the file to check
        
    Returns:
        True if the file is a CMake file, False otherwise
    """
    return filename.lower().endswith('.cmake') or filename == 'CMakeLists.txt'
