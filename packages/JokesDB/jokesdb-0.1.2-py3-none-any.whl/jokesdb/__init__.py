"""
JokesDB - A simple Python module to fetch jokes from a list of categories.
This module fetches jokes from a remote JSON database hosted at https://code2craft.xyz
Made by Code2Craft
"""

import requests
import random

BASE_URL = "https://code2craft.xyz/jokesdb/"
CAT_FILE = "cat.json"
JOKE_OF_THE_DAY = "jokeoftheday.json"

def _load_json(filename):
    """Helper to download JSON from website"""
    try:
        response = requests.get(BASE_URL + filename)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.Timeout:
        print(f"Timeout loading {filename}")
        return []
    except requests.exceptions.RequestException as e:
        print(f"Error loading {filename}: {e}")
        return []
    except Exception as e:
        print(f"Error loading {filename}: {e}")
        return []

def get_jokes(number=1, category="all"):
    """
    If number = 1, then returned a string, else a list.
    Default number = 1, category = "all".
    """
    cat_map = _load_json(CAT_FILE)
    if not cat_map:
        return "" if number == 1 else []

    if category == "all":
        files_to_load = list(cat_map.keys())
    else:
        files_to_load = [f for f, c in cat_map.items() if c == category]
        if not files_to_load:
            return "" if number == 1 else []

    all_jokes = []
    for f in files_to_load:
        jokes = _load_json(f)
        if jokes:
            all_jokes.extend(jokes)

    if not all_jokes:
        return "" if number == 1 else []

    selected = random.sample(all_jokes, min(number, len(all_jokes)))

    if number == 1:
        return selected[0]
    return selected

def joke_of_the_day():
    jokes = _load_json(JOKE_OF_THE_DAY)
    if not jokes:
        print("No joke of the day available.")
        return None
    return random.choice(jokes)

def catfile():
    """
    Returns the category file content. Use it to see all available categories.
    Another way to see all available categories is to go to https://code2craft.xyz/jokesdb/cat.json
    (there is a missing 'category' which is the joke of the day file available at https://code2craft.xyz/jokesdb/jokeoftheday.json)
    """
    return _load_json(CAT_FILE)