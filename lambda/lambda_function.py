import json
import logging
import os
import pandas as pd
import numpy as np
import boto3
from datetime import datetime
from utils import (
    parse_date, extract_years_since_release, parse_price, parse_tags,
    parse_rating, parse_int, split_systems, parse_tech, parse_change_number
)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

s3 = boto3.client('s3')

BUCKET_NAME = os.environ.get("BUCKET_NAME", "steamdb-storage")
CLEAN_PREFIX = os.environ.get("CLEAN_PREFIX", "cleaned-data")
INPUT_PREFIX = os.environ.get("INPUT_PREFIX", "scrapping_input")

# Load and clean data
def load_data(json_data: dict) -> pd.DataFrame:
    if "results" not in json_data:
        return pd.DataFrame()
    results = json_data["results"]

    if "games" not in results:
        return pd.DataFrame()

    games = results["games"]
    if not isinstance(games, dict):
        return pd.DataFrame()

    records = []
    for game_name, attributes in games.items():
        if not isinstance(attributes, dict):
            continue
        record = {"Game Name": game_name}
        record["App Type"] = attributes.get("App Type", None)
        record["Developer"] = attributes.get("Developer", None)
        record["Publisher"] = attributes.get("Publisher", None)

        release_date_tuple = parse_date(attributes.get("Release Date", None))
        record["Release Date Value"] = release_date_tuple[0]
        record["Real Release Data"] = release_date_tuple[1]
        record["Rating"] = parse_rating(attributes.get("rating", None))
        record["Current Price"] = parse_price(attributes.get("Current Price", None))
        record["Tags"] = parse_tags(attributes.get("Tags", []))

        records.append(record)

    df = pd.DataFrame(records)

    # Filter games released before 2018
    df = df[df["Release Date Value"] < pd.Timestamp("2018-01-01")]

    if df.empty:
        return df

    df["Years Since Release"] = df["Release Date Value"].apply(extract_years_since_release)

    numeric_cols = df.select_dtypes(include=[np.number]).columns
    for col in numeric_cols:
        if df[col].isna().any():
            median_val = df[col].median()
            df[col].fillna(median_val, inplace=True)
    return df

# Lambda handler function
def lambda_handler(event, context):
    try:
        record = event['Records'][0]
        bucket = record['s3']['bucket']['name']
        key = record['s3']['object']['key']

        obj = s3.get_object(Bucket=bucket, Key=key)
        data = obj['Body'].read().decode('utf-8')
        json_data = json.loads(data)

        df = load_data(json_data)

        if df.empty:
            return {
                "statusCode": 204,
                "body": "No data processed (no games released before 2018)"
            }

        json_output = df.to_json(orient="records", indent=4)

        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        output_key = f"{CLEAN_PREFIX}/cleaned_{timestamp}.json"

        s3.put_object(
            Bucket=bucket,
            Key=output_key,
            Body=json_output.encode('utf-8'),
            ContentType='application/json'
        )

        return {
            "statusCode": 200,
            "body": f"File processed and saved to {output_key}"
        }
    except Exception as e:
        logging.error(f"Error with the cleaning and preprocessing: {e}")
        return {
            "statusCode": 500,
            "body": "Internal Server Error"
        }