import pandas as pd
import numpy as np
from datetime import datetime
from typing import Any, List

def parse_date(date_str: str) -> (pd.Timestamp, str):
    if date_str is None:
        return pd.NaT, ""
    clean_date = date_str.split("–")[0].strip()
    possible_formats = [
        "%Y-%m-%d %H:%M:%S.%f",
        "%d %B %Y – %H:%M:%S UTC",
        "%d %B %Y",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d"
    ]
    for fmt in possible_formats:
        try:
            return pd.to_datetime(datetime.strptime(clean_date, fmt)), clean_date
        except (ValueError, TypeError):
            continue
    return pd.NaT, ""

def extract_years_since_release(release_date: pd.Timestamp, reference_date: pd.Timestamp = pd.Timestamp.now()) -> float:
    if pd.isnull(release_date):
        return np.nan
    delta = reference_date - release_date
    return delta.days / 365.25

def parse_price(price_str: str) -> float:
    if not price_str or price_str.strip() in ["N/A", "-"]:
        return 0.0
    cleaned = price_str.replace(",", ".")
    allowed_chars = "0123456789."
    filtered = "".join(c for c in cleaned if c in allowed_chars)
    try:
        return float(filtered)
    except ValueError:
        if "free" in price_str.lower():
            return 0.0
        return 0.0

def parse_tags(tags: List[str]) -> List[str]:
    cleaned_tags = []
    for t in tags:
        if t and t.strip():
            parts = t.strip().split(" ", 1)
            if len(parts) > 1:
                tag_part = parts[1].strip().lower()
                if tag_part:
                    cleaned_tags.append(tag_part)
            else:
                cleaned_tags.append(t.strip().lower())
    seen = set()
    unique_tags = []
    for tag in cleaned_tags:
        if tag not in seen:
            seen.add(tag)
            unique_tags.append(tag)
    return unique_tags

def parse_rating(r: Any) -> float:
    if r is None or pd.isnull(r):
        return np.nan
    r_str = str(r).replace("%", "").strip()
    try:
        return float(r_str)
    except ValueError:
        return np.nan

def parse_int(val: Any) -> float:
    if val is None or val == "-" or pd.isnull(val):
        return np.nan
    val_str = str(val).replace(",", "")
    if val_str.isdigit():
        return int(val_str)
    filtered_val = "".join([c for c in val_str if c.isdigit()])
    return int(filtered_val) if filtered_val else np.nan

def split_systems(s: Any) -> List[str]:
    if not s or pd.isnull(s):
        return []
    return [x.strip().lower() for x in str(s).split() if x.strip()]

def parse_tech(t: Any) -> str:
    if not t or pd.isnull(t):
        return None
    return str(t).lower()

def parse_change_number(cn: Any) -> float:
    if not cn or pd.isnull(cn):
        return np.nan
    try:
        return float(str(cn))
    except ValueError:
        return np.nan