"""
Data Ingestion Service.
Handles CSV/JSON file parsing, cleaning, and validation.
"""

import io
import json
import pandas as pd
from typing import Optional

from app.core.data_transforms import validate_war_date


# Required columns for the pipeline
REQUIRED_COLUMNS = ["date", "title", "category"]
OPTIONAL_COLUMNS = ["location", "sentiment", "casualties"]
VALID_CATEGORIES = ["conflict", "peace_talks", "civilian_impact", "political_transition", "uncertainty"]


class DataIngestionService:
    """Parse and validate uploaded historical war data."""

    def parse_csv(self, file_content: bytes) -> pd.DataFrame:
        """Parse CSV file content into a cleaned DataFrame."""
        try:
            df = pd.read_csv(io.BytesIO(file_content))
        except Exception as e:
            raise ValueError(f"Failed to parse CSV: {str(e)}")

        return self._clean_and_validate(df)

    def parse_json(self, file_content: bytes) -> pd.DataFrame:
        """Parse JSON file content into a cleaned DataFrame."""
        try:
            data = json.loads(file_content.decode("utf-8"))
            if isinstance(data, list):
                df = pd.DataFrame(data)
            elif isinstance(data, dict) and "events" in data:
                df = pd.DataFrame(data["events"])
            else:
                raise ValueError("JSON must be an array or an object with 'events' key")
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON: {str(e)}")

        return self._clean_and_validate(df)

    def load_sample_data(self, sample_path: str) -> pd.DataFrame:
        """Load the bundled sample dataset."""
        df = pd.read_csv(sample_path)
        return self._clean_and_validate(df)

    def _clean_and_validate(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Validate required columns, clean data, fill defaults.
        """
        # Normalize column names
        df.columns = df.columns.str.strip().str.lower()

        # Check required columns
        missing = [col for col in REQUIRED_COLUMNS if col not in df.columns]
        if missing:
            raise ValueError(f"Missing required columns: {missing}")

        # --- Date processing ---
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
        df = df.dropna(subset=["date"])

        # Filter to Vietnam War era (with some tolerance)
        df["year"] = df["date"].dt.year
        df = df[df["year"].apply(validate_war_date)]
        df["date_str"] = df["date"].dt.strftime("%Y-%m-%d")

        # --- Category validation ---
        if "category" in df.columns:
            df["category"] = df["category"].str.strip().str.lower()
            df.loc[~df["category"].isin(VALID_CATEGORIES), "category"] = "uncertainty"
        else:
            df["category"] = "uncertainty"

        # --- Sentiment (default to 0 if missing) ---
        if "sentiment" not in df.columns:
            df["sentiment"] = 0.0
        else:
            df["sentiment"] = pd.to_numeric(df["sentiment"], errors="coerce").fillna(0.0)
            df["sentiment"] = df["sentiment"].clip(-1.0, 1.0)

        # --- Casualties (default to 0 if missing) ---
        if "casualties" not in df.columns:
            df["casualties"] = 0
        else:
            df["casualties"] = pd.to_numeric(df["casualties"], errors="coerce").fillna(0).astype(int)
            df["casualties"] = df["casualties"].clip(lower=0)

        # --- Location (default to "Unknown") ---
        if "location" not in df.columns:
            df["location"] = "Unknown"
        else:
            df["location"] = df["location"].fillna("Unknown").str.strip()

        # --- Title cleanup ---
        df["title"] = df["title"].str.strip()
        df = df.dropna(subset=["title"])

        # Sort by date
        df = df.sort_values("date").reset_index(drop=True)

        if len(df) == 0:
            raise ValueError("No valid records found after cleaning")

        return df
