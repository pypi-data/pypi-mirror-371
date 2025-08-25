#!/usr/bin/env python3
"""
Just collecting vocab from my reddit posts
a bit of fun for https://bitplane.net/usr/share/dict/words
"""

import json
import argparse
import subprocess
import logging
import string


def normalize_text(text):
    """Normalize text by lowercasing, removing punctuation, and filtering words."""
    words = text.split()
    filtered_words = [
        word.lower().translate(str.maketrans("", "", string.punctuation))
        for word in words
        if "://" not in word and "." not in word and not any(char.isdigit() for char in word) and len(word) > 1
    ]
    return filtered_words


def load_words_from_json(filename):
    """Extract words from JSON comments and submitted posts and return a set."""
    with open(filename, "r") as f:
        data = json.load(f)

    words = set()

    for section in ["comments", "submitted"]:
        for entry in data.get(section, []):
            text = entry["data"].get("body", "") or entry["data"].get("title", "") + " " + entry["data"].get(
                "selftext", ""
            )
            words.update(normalize_text(text))

    return words


def load_aspell_dictionary():
    """Load all words from aspell dictionaries into a set."""
    result = subprocess.run(["aspell", "dump", "master"], capture_output=True, text=True)
    if result.returncode != 0:
        logging.error("Failed to load aspell dictionary")
        return set()

    dictionary_words = set(normalize_text(result.stdout))
    return dictionary_words


def find_new_words(json_file):
    """Compare extracted words with dictionary and return new words."""
    user_words = load_words_from_json(json_file)
    dictionary_words = load_aspell_dictionary()

    new_words = user_words - dictionary_words
    return new_words


def main():
    parser = argparse.ArgumentParser(description="Extract unique words from JSON and compare with system dictionary.")
    parser.add_argument(
        "json_file",
        help="Path to the JSON file containing comments and submitted posts.",
    )
    args = parser.parse_args()

    new_words = find_new_words(args.json_file)

    print("\n".join(sorted(new_words)))


if __name__ == "__main__":
    main()
