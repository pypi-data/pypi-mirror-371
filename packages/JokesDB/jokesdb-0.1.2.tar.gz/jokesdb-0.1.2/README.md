# JokesDB

A simple Python module to fetch jokes from my website.

## Chapters
- [Links](#links)
- [Installation](#installation)
- [Usage](#usage)
  - [1. Get jokes randomly](#1-get-jokes-randomly)
  - [2. Get today's joke](#2-get-todays-joke)
  - [3. Get cat.json file](#3-get-catjson-file)
- [Requirements](#requirements)
- [License](#license)

## Links
- [PyPI Project Page](https://pypi.org/project/JokesDB/)
- [Docs](https://code2craft.xyz/jokesdb/docs.html)
- [Website](https://code2craft.xyz)
- [Source code](https://github.com/gamercristi11/jokesdb)

## Installation

```sh
pip install jokesdb
```

## Usage

### 1. Get jokes randomly

```python
get_jokes(number=1, category="all")
```
Parameters:**
- `number`: Number of random jokes to get (Default = 1)
- `category`: Category to get jokes from. Categories: all, or those available at [cat.json](https://code2craft.xyz/jokesdb/cat.json) or via `catfile()` (Default = "all")

Example of use:
```python
from jokesdb import get_jokes

joke = get_jokes()
print(joke)
```
### 2. Get todays joke

```python
joke_of_the_day()
```
Example of use:
```python
from jokesdb import joke_of_the_day

todays_joke = joke_of_the_day()
print(todays_joke)
```

### 3. Get cat.json file
```python
catfile()
```

Example of use:
```python
from jokesdb import catfile

catfile = catfile()
print(catfile)
```

## Requirements

- Python 3.6+
- requests

## License
MIT License