from datetime import datetime
from typing import Any

from packages.domain.discovery.entities import DiscoveredJob


def map_greenhouse_job(
    payload: dict[str, Any],
) -> DiscoveredJob:
    """Map a Greenhouse API job into the domain representation."""

    company = payload.get("company_name")
    title = payload.get("title")
    source_url = payload.get("absolute_url")

    if not isinstance(company, str) or not company.strip():
        raise ValueError("Greenhouse job is missing company_name.")

    if not isinstance(title, str) or not title.strip():
        raise ValueError("Greenhouse job is missing title.")

    if not isinstance(source_url, str) or not source_url.strip():
        raise ValueError("Greenhouse job is missing absolute_url.")

    location = _extract_location(payload)
    employment_type = _extract_employment_type(payload)

    return DiscoveredJob(
        company=company.strip(),
        title=title.strip(),
        source="greenhouse",
        source_url=source_url.strip(),
        description=_optional_string(payload.get("content")),
        location=location,
        employment_type=employment_type,
        discovered_at=datetime.now(),
    )


def _optional_string(value: Any) -> str | None:
    if not isinstance(value, str):
        return None

    value = value.strip()

    return value or None


def _extract_location(payload: dict[str, Any]) -> str | None:
    location = payload.get("location")

    if not isinstance(location, dict):
        return None

    name = location.get("name")

    return _optional_string(name)


def _extract_employment_type(
    payload: dict[str, Any],
) -> str | None:
    metadata = payload.get("metadata")

    if not isinstance(metadata, list):
        return None

    for item in metadata:
        if not isinstance(item, dict):
            continue

        name = item.get("name")

        if isinstance(name, str) and name.lower() in {
            "employment type",
            "employment",
            "job type",
        }:
            value = item.get("value")

            return _optional_string(value)

    return None
