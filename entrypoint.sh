#!/bin/sh -l

cd "$GITHUB_WORKSPACE"

python3 /cmake-format/main.py "$@"
