"""Historical archive lookup for the memory-to-melody flow."""

import json
from pathlib import Path

from app.config import settings


class HistoricalArchiveService:
    """Select bundled historical events from a simple date/region/threshold query."""

    def __init__(self) -> None:
        self.archive_path = Path(settings.DATA_DIR) / "historical_memory_events.json"

    def load_events(self) -> list[dict]:
        with open(self.archive_path, "r", encoding="utf-8") as archive_file:
            return json.load(archive_file)

    def query_events(
        self,
        start_year: int = 1968,
        end_year: int = 1975,
        region: str = "Vietnam USA",
        threshold: str = "farewell",
    ) -> list[dict]:
        events = self.load_events()
        region_terms = {
            term.strip().lower()
            for term in region.replace("/", " ").replace(",", " ").split()
            if term.strip()
        }
        threshold_term = (threshold or "").strip().lower()

        selected = []
        for event in events:
            if not start_year <= int(event["year"]) <= end_year:
                continue

            event_regions = {item.lower() for item in event.get("region", [])}
            context_text = " ".join([
                event.get("title", ""),
                event.get("description", ""),
                event.get("historical_context", ""),
            ]).lower()
            region_matches = not region_terms or bool(region_terms & event_regions)
            region_matches = region_matches or any(term in context_text for term in region_terms)
            threshold_matches = not threshold_term or threshold_term == "knock" or threshold_term in context_text

            if region_matches or threshold_matches:
                selected.append(event)

        if selected:
            return sorted(selected, key=lambda item: item["date"])

        fallback = [
            event for event in events
            if start_year <= int(event["year"]) <= end_year
        ]
        return sorted(fallback or events, key=lambda item: item["date"])
