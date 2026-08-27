import json
import os
from datetime import datetime, timezone
from pathlib import Path

import requests
from dotenv import load_dotenv


# ---------------------------------------------------------
# Configuration
# ---------------------------------------------------------

load_dotenv()

API_KEY = os.getenv("WATCHMODE_API_KEY")
REGION = os.getenv("WATCHMODE_REGION", "IN")

BASE_URL = "https://api.watchmode.com/v1"

RAW_DATA_DIR = Path("data/raw")


# ---------------------------------------------------------
# Validate configuration
# ---------------------------------------------------------

if not API_KEY:
    raise ValueError(
        "WATCHMODE_API_KEY is missing. "
        "Please add it to your .env file."
    )


# ---------------------------------------------------------
# API request helper
# ---------------------------------------------------------

def get_from_watchmode(endpoint, params=None):
    """
    Send a GET request to the Watchmode API.
    """

    url = f"{BASE_URL}/{endpoint}"

    headers = {
        "X-API-Key": API_KEY
    }

    response = requests.get(
        url,
        headers=headers,
        params=params,
        timeout=30
    )

    response.raise_for_status()

    return response.json()


# ---------------------------------------------------------
# Check API account
# ---------------------------------------------------------

def get_api_status():
    """
    Check the Watchmode API account and remaining quota.
    """

    return get_from_watchmode("status")


# ---------------------------------------------------------
# Get supported regions
# ---------------------------------------------------------

def get_regions():
    """
    Retrieve countries supported by the API.
    """

    return get_from_watchmode("regions")


# ---------------------------------------------------------
# Get OTT providers
# ---------------------------------------------------------

def get_streaming_sources():
    """
    Retrieve subscription and free streaming providers
    available for our selected region.
    """

    return get_from_watchmode(
        "sources",
        params={
            "regions": REGION,
            "types": "sub,free"
        }
    )


# ---------------------------------------------------------
# Get OTT titles
# ---------------------------------------------------------

def get_titles(page=1, limit=50):
    """
    Retrieve movies and TV series available through
    subscription/free streaming services in our region.
    """

    return get_from_watchmode(
        "list-titles",
        params={
            "types": "movie,tv_series",
            "regions": REGION,
            "source_types": "sub,free",
            "sort_by": "popularity_desc",
            "page": page,
            "limit": limit
        }
    )


# ---------------------------------------------------------
# Save raw API response
# ---------------------------------------------------------

def save_raw_data(data, filename):
    """
    Save the original API response without transformation.

    This is our RAW data layer.
    """

    RAW_DATA_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    file_path = RAW_DATA_DIR / filename

    with open(
        file_path,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            data,
            file,
            indent=2,
            ensure_ascii=False
        )

    return file_path


# ---------------------------------------------------------
# Main pipeline
# ---------------------------------------------------------

def main():

    print("=" * 60)
    print("OTT STREAMING DATA PIPELINE")
    print("=" * 60)

    print(f"Region: {REGION}")
    print()

    # -----------------------------------------------------
    # 1. Check API status
    # -----------------------------------------------------

    print("Checking Watchmode API...")

    status = get_api_status()

    print("API connection successful!")
    print(f"API quota: {status.get('quota')}")
    print(f"API requests used: {status.get('quotaUsed')}")
    print()

    # -----------------------------------------------------
    # 2. Get streaming providers
    # -----------------------------------------------------

    print("Fetching OTT providers...")

    sources = get_streaming_sources()

    print(
        f"Providers returned: {len(sources)}"
    )

    # -----------------------------------------------------
    # 3. Get titles
    # -----------------------------------------------------

    print("Fetching OTT titles...")

    titles_response = get_titles(
        page=1,
        limit=50
    )

    titles = titles_response.get(
        "titles",
        []
    )

    print(
        f"Titles returned: {len(titles)}"
    )

    print(
        f"Total titles available: "
        f"{titles_response.get('total_results')}"
    )

    print()

    # -----------------------------------------------------
    # 4. Save raw responses
    # -----------------------------------------------------

    run_timestamp = datetime.now(
        timezone.utc
    ).strftime("%Y%m%dT%H%M%SZ")

    providers_file = save_raw_data(
        sources,
        f"providers_{run_timestamp}.json"
    )

    titles_file = save_raw_data(
        titles_response,
        f"titles_{run_timestamp}.json"
    )

    # -----------------------------------------------------
    # 5. Display sample data
    # -----------------------------------------------------

    print("Sample titles:")
    print("-" * 60)

    for title in titles[:10]:

        print(
            f"{title.get('id')} | "
            f"{title.get('title')} | "
            f"{title.get('year')} | "
            f"{title.get('type')}"
        )

    print()
    print("Raw data saved successfully.")
    print(f"Providers: {providers_file}")
    print(f"Titles:    {titles_file}")

    print()
    print("=" * 60)
    print("INGESTION COMPLETED")
    print("=" * 60)


if __name__ == "__main__":
    main()