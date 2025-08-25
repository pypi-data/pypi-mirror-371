# Learn Simple Regular Expressions

[![pr-checks](https://github.com/rohit1998/lsre/actions/workflows/pr-checks.yml/badge.svg)](https://github.com/rohit1998/lsre/actions/workflows/pr-checks.yml)
[![PyPI version](https://img.shields.io/pypi/v/lsre.svg)](https://pypi.org/project/lsre/)
[![Python versions](https://img.shields.io/pypi/pyversions/lsre.svg)](https://pypi.org/project/lsre/)
A project to learn simple regular expressions.

## Overview

Create a package to do simple regular expressions. Also publish package to pypi to learn automated publishing.

## Docker Setup

1. Reopen in Container
1. Run all verification

    ```bash
    j ad
    ```

## Commands Non Docker

1. Follow [this](docs/getting-started/vm-setup.md) to setup your VM
1. Run these commands to install `uv, just`

    ```bash
    curl -LsSf https://astral.sh/uv/install.sh | sh
    curl --proto '=https' --tlsv1.2 -sSf https://just.systems/install.sh | bash -s -- --to ~/.local/bin
    ```

1. Run all verification

    ```bash
    j ah
    ```

## Useful Just Commands

```bash
j # lists all just commands
jf <str> # finds <str> in just --list
jf alias #  gets all alias
```

## Development

### For quick changes

1. make your changes
1. check and put them in staging area
1. `j pr branch-name commit-message=branch-name` to create branch and pull request run
1. Wait for github actions to pass.
1. Optional, `j pu commit-message` on issue, make changes
1. `j mpr`, finally merge on actions and features success.

### For proper features

1. `j b branch-name`, make a branch off main
1. Do changes
1. check and put them in staging area
1. `j pu commit-message`
1. Keep doing until feature is developed.
1. `j cpr` to create pr.
1. Wait for github actions to pass.
1. Optional, `j pu commit-message` on issue, make changes
1. `j mpr`, finally merge on actions and features success.

## Pyright node error

Try installing nvm and updating node version

```bash
# https://github.com/nvm-sh/nvm?tab=readme-ov-file#installing-and-updating
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.3/install.sh | bash

# add this to .bashrc/.zshrc
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
[ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion"

nvm install --lts
nvm use --lts
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.
