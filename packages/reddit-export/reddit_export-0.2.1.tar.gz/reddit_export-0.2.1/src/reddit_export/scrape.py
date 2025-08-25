#!/usr/bin/env python3
import json
import argparse
import logging
import os
import requests
import time


def get_modification_date(entry):
    """Return the latest modification timestamp of a Reddit entry."""
    return entry["data"].get("edited", entry["data"]["created_utc"])


def load_existing_data(filepath):
    """Load existing JSON data if the file exists, otherwise return an empty structure."""
    if os.path.exists(filepath):
        with open(filepath, "r") as f:
            return json.load(f)
    return {"t1": {}, "t3": {}}


def get_reddit_data(username, category, limit=100, after=None):
    """Fetch data from Reddit's API."""
    url = f"https://www.reddit.com/user/{username}/{category}.json"
    headers = {"User-Agent": "Mozilla/5.0"}
    params = {"limit": limit, "after": after}

    response = requests.get(url, headers=headers, params=params)
    if response.status_code != 200:
        logging.error(f"Error fetching {category}: {response.status_code}")
        return None

    return response.json()


def save_reddit_data(output_dir, username):
    """Fetch and store Reddit posts and comments idempotently."""
    filepath = os.path.join(output_dir, f"{username}.json")
    os.makedirs(output_dir, exist_ok=True)

    existing_data = load_existing_data(filepath)

    categories = ["submitted", "comments"]

    for category in categories:
        kind = "t3" if category == "submitted" else "t1"
        after = None

        while True:
            logging.debug(f"Fetching {category} after: {after}")
            data = get_reddit_data(username, category, after=after)
            if not data or "data" not in data:
                logging.debug(f"No more {category} received, stopping.")
                break

            fetched_items = data["data"]["children"]
            new_entries = 0

            for entry in fetched_items:
                entry_id = entry["data"]["id"]
                if entry_id in existing_data[kind]:
                    stored_entry = existing_data[kind][entry_id]
                    if get_modification_date(entry) <= get_modification_date(stored_entry):
                        continue  # Skip unchanged entries

                existing_data[kind][entry_id] = entry  # Store/update entry
                new_entries += 1

            after = data["data"].get("after")
            if not after or new_entries == 0:
                logging.debug(f"Stopping {category} fetch, no new entries.")
                break

            time.sleep(2)  # Avoid rate-limiting

    # Sort entries by modification date for consistency
    for kind in existing_data:
        existing_data[kind] = dict(
            sorted(
                existing_data[kind].items(),
                key=lambda item: get_modification_date(item[1]),
            )
        )

    # Write safely to a temporary file before replacing
    temp_filepath = filepath + ".tmp"
    with open(temp_filepath, "w") as f:
        json.dump(existing_data, f, indent=4)
    os.replace(temp_filepath, filepath)

    logging.info(f"Saved data to {filepath}")


def main():
    parser = argparse.ArgumentParser(description="Scrape Reddit posts and comments from a user and save to JSON.")
    parser.add_argument("username", help="Reddit username to scrape")
    parser.add_argument("--output-dir", default="data", help="Directory to save output files")
    parser.add_argument(
        "--log-level",
        default="ERROR",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Set the logging level",
    )
    args = parser.parse_args()

    logging.basicConfig(format="%(levelname)s: %(message)s", level=args.log_level.upper())
    save_reddit_data(args.output_dir, args.username)


if __name__ == "__main__":
    main()
