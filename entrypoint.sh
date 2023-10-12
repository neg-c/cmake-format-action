#!/bin/sh -l

cd "$GITHUB_WORKSPACE" || exit

/cmake_format_runner.py $@
