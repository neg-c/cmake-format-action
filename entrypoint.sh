#!/bin/sh -l

cd "$GITHUB_WORKSPACE"


pip install cmakelang
python3 /cmake-format/main.py "$@"
