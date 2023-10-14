# cmake-format lint GitHub Action

GitHub Action to check if your code is formatted correctly using cmake-format.

This action also provides a Git diff display, making it easy to review code formatting changes.


## Usage

### Inputs

- `source` (optional): Source file/folder to check formatting or directory path. Defaults to "." (current directory). You can specify multiple values separated by spaces.
- `exclude` (optional): Folders to exclude from the formatting check. Defaults to "none." You can specify multiple values separated by spaces.
- `config` (optional): Use .cmake-format style. Defaults to False.
- `inplace` (optional): Just fix files (`cmake-format -i`) instead of returning a diff. Defaults to False.

### Example Workflow

Here's an example of how to use this action in your GitHub Actions workflow:

```yaml
name: Check Code Formatting

on:
  push:
    branches:
      - main

jobs:
  format-check:
    runs-on: ubuntu-latest
    steps:
    - name: Checkout code
      uses: actions/checkout@v2
    - name: cmake-format lint
      uses: neg-c/cmake-format-action@v0.1
      with:
        source: "src/module1 src/module2"
        exclude: "thirdparty external"
        config: true
        inplace: true

```