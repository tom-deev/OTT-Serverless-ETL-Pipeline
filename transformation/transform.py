import json
from pathlib import Path

import pandas as pd


# ============================================================
# FILE PATHS
# ============================================================

RAW_FILE = Path("data/raw/titles.json")
CURATED_DIR = Path("data/curated")
CURATED_FILE = CURATED_DIR / "titles.parquet"


# ============================================================
# READ RAW JSON
# ============================================================

with open(RAW_FILE, "r", encoding="utf-8") as f:
    raw_data = json.load(f)


# ============================================================
# EXTRACT TITLES
# ============================================================

titles = raw_data.get("titles", [])

df = pd.DataFrame(titles)


# ============================================================
# TRANSFORM COLUMNS
# ============================================================

df = df.rename(
    columns={
        "id": "watchmode_id",
        "year": "release_year",
        "type": "content_type",
    }
)


# Keep only the required curated columns
required_columns = [
    "watchmode_id",
    "title",
    "release_year",
    "imdb_id",
    "tmdb_id",
    "content_type",
    "popularity_percentile",
]

df = df[required_columns]


# ============================================================
# DATA TYPE CONVERSION
# ============================================================

df["watchmode_id"] = pd.to_numeric(
    df["watchmode_id"], errors="coerce"
)

df["release_year"] = pd.to_numeric(
    df["release_year"], errors="coerce"
)

df["popularity_percentile"] = pd.to_numeric(
    df["popularity_percentile"], errors="coerce"
)

# ============================================================
# ADD INGESTION TIMESTAMP
# ============================================================

df["ingestion_timestamp"] = pd.Timestamp.now(tz="UTC")

# ============================================================
# DATA QUALITY CHECKS
# ============================================================

record_count = len(df)

# 1. Null watchmode IDs
null_ids = df["watchmode_id"].isna().sum()


# 2. Null or empty titles
null_or_empty_titles = (
    df["title"].isna()
    | df["title"].astype(str).str.strip().eq("")
).sum()


# 3. Invalid release years
#
# A valid release year should be numeric and between
# 1800 and the current year.
current_year = pd.Timestamp.now().year

invalid_years = (
    df["release_year"].isna()
    | (df["release_year"] < 1800)
    | (df["release_year"] > current_year)
).sum()


# 4. Invalid content types
valid_content_types = {
    "movie",
    "tv_series",
}

invalid_content_types = (
    df["content_type"].isna()
    | ~df["content_type"].isin(valid_content_types)
).sum()


# 5. Duplicate watchmode IDs
duplicate_ids = df["watchmode_id"].duplicated().sum()


# 6. Invalid popularity values
#
# Watchmode popularity_percentile should be between 0 and 100.
invalid_popularity_values = (
    df["popularity_percentile"].isna()
    | (df["popularity_percentile"] < 0)
    | (df["popularity_percentile"] > 100)
).sum()


# ============================================================
# OVERALL DATA QUALITY STATUS
# ============================================================

quality_checks = [
    null_ids == 0,
    null_or_empty_titles == 0,
    invalid_years == 0,
    invalid_content_types == 0,
    duplicate_ids == 0,
    invalid_popularity_values == 0,
]

overall_status = "PASS" if all(quality_checks) else "FAIL"


# ============================================================
# PRINT DATA QUALITY REPORT
# ============================================================

print("\nDATA QUALITY REPORT")
print("===================")

print("\ntitles")
print(f"Records: {record_count}")
print(f"Null IDs: {null_ids}")
print(f"Null/Empty Titles: {null_or_empty_titles}")
print(f"Duplicate IDs: {duplicate_ids}")
print(f"Invalid years: {invalid_years}")
print(f"Invalid content types: {invalid_content_types}")
print(f"Invalid popularity values: {invalid_popularity_values}")

print(f"\nOverall Status: {overall_status}")


# ============================================================
# WRITE CURATED PARQUET
# ============================================================

CURATED_DIR.mkdir(parents=True, exist_ok=True)

df.to_parquet(
    CURATED_FILE,
    engine="pyarrow",
    index=False,
)


print(f"\nParquet file created:")
print(CURATED_FILE)
print(f"Records processed: {len(df)}")

# ============================================================
# PROVIDER TRANSFORMATION
# ============================================================

PROVIDER_RAW_FILE = Path("data/raw/sources.json")
PROVIDER_CURATED_FILE = CURATED_DIR / "providers.parquet"


# ============================================================
# READ RAW PROVIDER JSON
# ============================================================

with open(PROVIDER_RAW_FILE, "r", encoding="utf-8") as f:
    provider_data = json.load(f)


# ============================================================
# EXTRACT PROVIDERS
# ============================================================

providers_df = pd.DataFrame(provider_data)


# ============================================================
# TRANSFORM PROVIDER COLUMNS
# ============================================================

providers_df = providers_df.rename(
    columns={
        "id": "provider_id",
        "name": "provider_name",
        "type": "provider_type",
        "logo_100px": "logo_url",
    }
)


# Keep only the required curated provider columns
provider_columns = [
    "provider_id",
    "provider_name",
    "provider_type",
    "host_source_id",
    "host_source",
    "logo_url",
    "ios_appstore_url",
    "android_playstore_url",
    "android_scheme",
    "ios_scheme",
]

providers_df = providers_df[provider_columns]


# ============================================================
# DATA TYPE CONVERSION
# ============================================================

providers_df["provider_id"] = pd.to_numeric(
    providers_df["provider_id"],
    errors="coerce",
)

providers_df["host_source_id"] = pd.to_numeric(
    providers_df["host_source_id"],
    errors="coerce",
)


# ============================================================
# ADD INGESTION TIMESTAMP
# ============================================================

providers_df["ingestion_timestamp"] = pd.Timestamp.now(tz="UTC")

# ============================================================
# PROVIDER DATA QUALITY CHECKS
# ============================================================

provider_record_count = len(providers_df)


# 1. Null provider IDs
provider_null_ids = providers_df["provider_id"].isna().sum()


# 2. Null or empty provider names
provider_null_or_empty_names = (
    providers_df["provider_name"].isna()
    | providers_df["provider_name"].astype(str).str.strip().eq("")
).sum()


# 3. Invalid provider types
#
# Watchmode provider types observed in our raw data:
# sub = subscription
# free = free
valid_provider_types = {
    "sub",
    "free",
}

provider_invalid_types = (
    providers_df["provider_type"].isna()
    | ~providers_df["provider_type"].isin(valid_provider_types)
).sum()


# 4. Duplicate provider IDs
provider_duplicate_ids = providers_df["provider_id"].duplicated().sum()


# ============================================================
# PROVIDER DATA QUALITY STATUS
# ============================================================

provider_quality_checks = [
    provider_null_ids == 0,
    provider_null_or_empty_names == 0,
    provider_invalid_types == 0,
    provider_duplicate_ids == 0,
]

provider_quality_status = (
    "PASS" if all(provider_quality_checks) else "FAIL"
)


# ============================================================
# PRINT PROVIDER DATA QUALITY REPORT
# ============================================================

print("\nPROVIDER DATA QUALITY REPORT")
print("============================")

print(f"Records: {provider_record_count}")
print(f"Null IDs: {provider_null_ids}")
print(f"Null/Empty Names: {provider_null_or_empty_names}")
print(f"Invalid Provider Types: {provider_invalid_types}")
print(f"Duplicate IDs: {provider_duplicate_ids}")

print(f"\nProvider Quality Status: {provider_quality_status}")

# ============================================================
# WRITE CURATED PROVIDER PARQUET
# ============================================================

CURATED_DIR.mkdir(parents=True, exist_ok=True)

providers_df.to_parquet(
    PROVIDER_CURATED_FILE,
    engine="pyarrow",
    index=False,
)


print("\nPROVIDER TRANSFORMATION")
print("=======================")
print(f"Providers processed: {len(providers_df)}")
print(f"Parquet file created:")
print(PROVIDER_CURATED_FILE)

print("\nFirst 5 providers:")
print(providers_df.head())


# ============================================================
# PROVIDER REGIONS TRANSFORMATION
# ============================================================

PROVIDER_REGIONS_CURATED_FILE = (
    CURATED_DIR / "provider_regions.parquet"
)


# ============================================================
# EXTRACT PROVIDER-REGION RELATIONSHIPS
# ============================================================

provider_region_records = []

for provider in provider_data:
    provider_id = provider.get("id")
    regions = provider.get("regions", [])

    for region in regions:
        provider_region_records.append(
            {
                "provider_id": provider_id,
                "region": region,
            }
        )


# Convert to DataFrame
provider_regions_df = pd.DataFrame(
    provider_region_records
)


# ============================================================
# DATA TYPE CONVERSION
# ============================================================

provider_regions_df["provider_id"] = pd.to_numeric(
    provider_regions_df["provider_id"],
    errors="coerce",
)

# ============================================================
# PROVIDER REGIONS DATA QUALITY CHECKS
# ============================================================

provider_region_record_count = len(provider_regions_df)


# 1. Null provider IDs
provider_region_null_ids = (
    provider_regions_df["provider_id"].isna().sum()
)


# 2. Null or empty regions
provider_region_null_or_empty_regions = (
    provider_regions_df["region"].isna()
    | provider_regions_df["region"].astype(str).str.strip().eq("")
).sum()


# 3. Duplicate provider-region pairs
provider_region_duplicate_pairs = (
    provider_regions_df.duplicated(
        subset=["provider_id", "region"]
    ).sum()
)


# ============================================================
# PROVIDER REGIONS DATA QUALITY STATUS
# ============================================================

provider_region_quality_checks = [
    provider_region_null_ids == 0,
    provider_region_null_or_empty_regions == 0,
    provider_region_duplicate_pairs == 0,
]

provider_region_quality_status = (
    "PASS"
    if all(provider_region_quality_checks)
    else "FAIL"
)


# ============================================================
# PRINT PROVIDER REGIONS DATA QUALITY REPORT
# ============================================================

print("\nPROVIDER REGIONS DATA QUALITY REPORT")
print("====================================")

print(
    f"Records: {provider_region_record_count}"
)
print(
    f"Null Provider IDs: {provider_region_null_ids}"
)
print(
    f"Null/Empty Regions: "
    f"{provider_region_null_or_empty_regions}"
)
print(
    f"Duplicate Provider-Region Pairs: "
    f"{provider_region_duplicate_pairs}"
)

print(
    f"\nProvider Regions Quality Status: "
    f"{provider_region_quality_status}"
)

# ============================================================
# WRITE CURATED PROVIDER REGIONS PARQUET
# ============================================================

CURATED_DIR.mkdir(parents=True, exist_ok=True)

provider_regions_df.to_parquet(
    PROVIDER_REGIONS_CURATED_FILE,
    engine="pyarrow",
    index=False,
)


# ============================================================
# PRINT PROVIDER REGIONS TRANSFORMATION RESULT
# ============================================================

print("\nPROVIDER REGIONS TRANSFORMATION")
print("================================")
print(
    f"Provider-region records: "
    f"{len(provider_regions_df)}"
)

print("Parquet file created:")
print(PROVIDER_REGIONS_CURATED_FILE)

print("\nFirst 10 provider-region records:")
print(provider_regions_df.head(10))
