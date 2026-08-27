import json
import os
from datetime import datetime, timezone
from urllib.request import Request, urlopen
from urllib.parse import urlencode

import boto3


# ---------------------------------------------------------
# AWS S3 client
# ---------------------------------------------------------

s3_client = boto3.client("s3")


# ---------------------------------------------------------
# Configuration
# ---------------------------------------------------------

API_KEY = os.environ["WATCHMODE_API_KEY"]
REGION = os.environ.get("WATCHMODE_REGION", "IN")
S3_BUCKET = os.environ["S3_BUCKET"]

BASE_URL = "https://api.watchmode.com/v1"


# ---------------------------------------------------------
# Watchmode API helper
# ---------------------------------------------------------

def get_from_watchmode(endpoint, params=None):
    """
    Send a GET request to the Watchmode API
    and return the JSON response.
    """

    if params is None:
        params = {}

    params["apiKey"] = API_KEY

    query_string = urlencode(params)

    url = f"{BASE_URL}/{endpoint}/?{query_string}"

    request = Request(
        url,
        method="GET"
    )

    with urlopen(request, timeout=30) as response:

        response_body = response.read()

        return json.loads(
            response_body.decode("utf-8")
        )


# ---------------------------------------------------------
# Save data to S3
# ---------------------------------------------------------

def save_to_s3(data, key):
    """
    Save JSON data into our S3 raw layer.
    """

    s3_client.put_object(
        Bucket=S3_BUCKET,
        Key=key,
        Body=json.dumps(
            data,
            ensure_ascii=False,
            indent=2
        ).encode("utf-8"),
        ContentType="application/json"
    )

    return f"s3://{S3_BUCKET}/{key}"


# ---------------------------------------------------------
# Lambda handler
# ---------------------------------------------------------

def lambda_handler(event, context):

    print("=" * 60)
    print("OTT STREAMING DATA INGESTION")
    print("=" * 60)

    print(f"Region: {REGION}")
    print(f"S3 Bucket: {S3_BUCKET}")

    # -----------------------------------------------------
    # 1. Fetch streaming providers
    # -----------------------------------------------------

    print("Fetching OTT streaming providers...")

    sources = get_from_watchmode(
        "sources",
        {
            "regions": REGION,
            "types": "sub,free"
        }
    )

    print(
        f"Providers received: {len(sources)}"
    )

    # -----------------------------------------------------
    # 2. Fetch OTT titles
    # -----------------------------------------------------

    print("Fetching OTT titles...")

    titles_response = get_from_watchmode(
        "list-titles",
        {
            "types": "movie,tv_series",
            "regions": REGION,
            "source_types": "sub,free",
            "sort_by": "popularity_desc",
            "page": 1,
            "limit": 50
        }
    )

    titles = titles_response.get(
        "titles",
        []
    )

    print(
        f"Titles received: {len(titles)}"
    )

    # -----------------------------------------------------
    # 3. Create ingestion timestamp
    # -----------------------------------------------------

    timestamp = datetime.now(
        timezone.utc
    ).strftime(
        "%Y%m%dT%H%M%SZ"
    )

    # -----------------------------------------------------
    # 4. Create S3 object keys
    # -----------------------------------------------------

    titles_key = (
        f"raw/titles/"
        f"titles_{timestamp}.json"
    )

    sources_key = (
        f"raw/sources/"
        f"sources_{timestamp}.json"
    )

    # -----------------------------------------------------
    # 5. Store raw titles
    # -----------------------------------------------------

    titles_location = save_to_s3(
        titles_response,
        titles_key
    )

    print(
        f"Titles saved to: {titles_location}"
    )

    # -----------------------------------------------------
    # 6. Store raw providers
    # -----------------------------------------------------

    sources_location = save_to_s3(
        sources,
        sources_key
    )

    print(
        f"Sources saved to: {sources_location}"
    )

    # -----------------------------------------------------
    # 7. Create pipeline result
    # -----------------------------------------------------

    result = {
        "status": "success",
        "region": REGION,
        "titles_received": len(titles),
        "providers_received": len(sources),
        "titles_location": titles_location,
        "sources_location": sources_location,
        "ingestion_timestamp": timestamp
    }

    print("=" * 60)
    print("INGESTION COMPLETED SUCCESSFULLY")
    print("=" * 60)

    print(
        json.dumps(
            result,
            indent=2
        )
    )

    return {
        "statusCode": 200,
        "body": json.dumps(result)
    }