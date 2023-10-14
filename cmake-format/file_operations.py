import os
import fnmatch


def list_files(files, exclude=None):
    print(files)
    cmake_files = []
    if exclude is None:
        exclude = []

    exclude.append("build")
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
