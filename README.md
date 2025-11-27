# aoc-tools

Python tooling for **Advent of Code**: fetching inputs, parsing puzzle
pages, extracting code and examples, and submitting answers.

Includes a full CLI (`aoc`) and a Python API suitable for solver
scripts.

## Features

### Core Functionality

-   Fetch puzzle **input** for a given year/day.
-   Fetch puzzle **HTML** for parsing.
-   Extract all `<pre><code>` **code blocks** from the puzzle page.
-   Extract **example blocks** introduced by a `<p>…for example:…</p>`
    marker.
-   Optional selection of a specific block (`--idx`) or custom
    separator (`--sep`).
-   Submit answers programmatically with proper error handling.

### CLI

-   `aoc fetch input`
-   `aoc fetch code [--idx N] [--sep STR]`
-   `aoc fetch example [--idx N] [--sep STR]`
-   `aoc submit 1234`

### Python API

```python
from aoc import (
    fetch_input,
    fetch_code,
    fetch_example,
    submit
)
```

## Installation

### Local development install

```bash
# Editable install for development
pip install -e .
```

### Using inside another project

#### Step 1
Either clone:
```bash
git clone git@github.com:programmeerbeertjes/aoc-tools.git
```
or add as a submodule:
```bash
# O add as submodule inside an existing git project
git submodule add git@github.com:programmeerbeertjes/aoc-tools.git aoc-tools
git submodule init
```

#### Step 2
Add the project as a Python dependency. Inside a `requirements.txt` add:
```
./aoc-tools
```
then install like normal:
```bash
pip install -r requirements.txt
```

## Usage

### Python

```python
import os
os.environ["AOC_YEAR"] = 2023  # Set year 2023
os.environ["AOC_DAY"] = 1  # Set first day

from aoc import fetch_input, fetch_code, fetch_example, submit

puzzle_input = fetch_input()
code_blocks = fetch_code()  # list of code blocks
examples = fetch_example()  # list of example blocks

# Submit to today's puzzle and unsolved part
submit(12345)
```

### CLI

```bash
# Use 2023, day 1 for all commands
export AOC_YEAR=2023
export AOC_DAY=1

# Fetch puzzle input
aoc fetch input

# Fetch code blocks
aoc fetch code

# Fetch the second code block (0-based)
aoc fetch code --idx 1

# Fetch example blocks (code blocks preceded by for example)
aoc fetch example

# Use a custom separator
aoc fetch example --sep "\n---\n"

# Submit single answer
aoc submit 1234

# Submit two answers
aoc submit 1234 5678

# Submit from stdin
echo '1234\nabcd' | aoc submit
```
