# OTT Serverless ETL Pipeline

An end-to-end serverless data engineering pipeline that collects OTT streaming data from the Watchmode API, stores raw API responses in Amazon S3, transforms and validates the data using Python and Pandas, creates curated Parquet datasets, catalogs them with AWS Glue, and performs SQL analytics using Amazon Athena.

The pipeline also uses Amazon EventBridge to automatically trigger the ingestion Lambda on a daily schedule.

---

## Architecture

```text
Watchmode API
      |
      v
AWS Lambda (Python)
ott-watchmode-ingestion
      |
      v
Amazon S3 - Raw Layer
      |
      +----------------------+
      |                      |
      v                      v
raw/titles/             raw/sources/
      |                      |
      +----------+-----------+
                 |
                 v
      Python + Pandas
      Transformation
                 |
                 v
        Data Quality Checks
                 |
                 v
       Amazon S3 - Curated
                 |
       +---------+---------+
       |         |         |
       v         v         v
    titles   providers   provider_regions
    Parquet   Parquet       Parquet
       \         |           /
        \        |          /
         +-------+---------+
                 |
                 v
       AWS Glue Data Catalog
                 |
                 v
          Amazon Athena
                 |
                 v
          SQL Analytics

Amazon EventBridge
        |
        v
Daily Lambda Trigger
        |
        v
ott-watchmode-ingestion

```

### Project Overview

This project demonstrates an end-to-end serverless ETL pipeline built using AWS services and Python.

The pipeline retrieves OTT movie, TV series, and streaming provider information from the Watchmode API.

The raw API responses are stored in Amazon S3 as JSON files. The data is then transformed and validated using Python and Pandas before being stored as Parquet files in the curated layer.

AWS Glue Data Catalog provides metadata for the datasets, while Amazon Athena is used to perform analytical SQL queries directly on the curated Parquet data.

Amazon EventBridge automates the ingestion process by triggering the Lambda function on a daily schedule.

## AWS Services Used

- AWS Lambda
- Amazon S3
- AWS Glue Data Catalog
- Amazon Athena
- Amazon EventBridge
- AWS IAM
- Amazon CloudWatch

## Technology Stack

- Python
- Pandas
- PyArrow
- SQL
- JSON
- Apache Parquet
- AWS Serverless Services

## AWS Region
````
 ap-south-1` — Asia Pacific (Mumbai)
````

## S3 Bucket
````
`s3://ott-v-pipeline-data/`
````

## Data Lake Structure

````
ott-v-pipeline-data/
|
+-- raw/
|   +-- titles/
|   +-- sources/
|
+-- curated/
|   +-- titles/
|   |   +-- titles.parquet
|   |
|   +-- providers/
|   |   +-- providers.parquet
|   |
|   +-- provider_regions/
|       +-- provider_regions.parquet
|
+-- athena-results/

````

## Raw Data Layer
```
Raw Titles:
s3://ott-v-pipeline-data/raw/titles/

Raw Sources:
s3://ott-v-pipeline-data/raw/sources/
```

## Transformation Layer

transformation/transform.py

## Curated Datasets

Titles: s3://ott-v-pipeline-data/curated/titles/titles.parquet
Providers: s3://ott-v-pipeline-data/curated/providers/providers.parquet
Providers Region: s3://ott-v-pipeline-data/curated/provider_regions/provider_regions.parquet

## AWS Glue Data Catalog

Database: ott_streaming
Tables: titles
        providers
        provider_regions

## Amazon Athena Analytics

sql/analytics.sql

## EventBridge Automation

ott-watchmode-ingestion
Rule: ott-pipeline-daily
Schedule: Fixed rate: 1 day

## CloudWatch Monitoring

AWS CloudWatch is used to monitor Lambda execution and ingestion logs.

Successful ingestion executions produce logs confirming completion of the ingestion process.

## Project Results

The pipeline successfully processes:

50 title records
25 provider records
517 provider-region records

## Project Structure

ott-streaming-data-pipeline/
|
+-- architecture/
|
+-- data/
|   +-- raw/
|   +-- curated/
|       +-- titles.parquet
|       +-- providers.parquet
|       +-- provider_regions.parquet
|
+-- ingestion/
|   +-- lambda_function.py
|
+-- sql/
|   +-- analytics.sql
|
+-- tests/
|
+-- transformation/
|   +-- transform.py
|
+-- .env.example
+-- .gitignore
+-- README.md
+-- requirements.txt

## Project Outcome

Watchmode API
      ↓
AWS Lambda
      ↓
S3 Raw JSON
      ↓
Python + Pandas
      ↓
Data Quality
      ↓
S3 Curated Parquet
      ↓
AWS Glue Data Catalog
      ↓
Amazon Athena
      ↓
SQL Analytics

Amazon EventBridge
      ↓
Daily Lambda Trigger