from packages.infrastructure.discovery.greenhouse.mapper import (
    map_greenhouse_job,
)


def test_map_greenhouse_job_maps_required_fields() -> None:
    payload = {
        "company_name": "Acme",
        "title": "Senior Python Engineer",
        "absolute_url": "https://example.com/jobs/123",
    }

    job = map_greenhouse_job(payload)

    assert job.company == "Acme"
    assert job.title == "Senior Python Engineer"
    assert job.source == "greenhouse"
    assert job.source_url == "https://example.com/jobs/123"


def test_map_greenhouse_job_maps_optional_fields() -> None:
    payload = {
        "company_name": "Acme",
        "title": "Python Engineer",
        "absolute_url": "https://example.com/jobs/123",
        "content": "<p>Build backend systems.</p>",
        "location": {
            "name": "Bengaluru, India",
        },
        "metadata": [
            {
                "name": "Employment Type",
                "value": "Full-time",
            },
        ],
    }

    job = map_greenhouse_job(payload)

    assert job.description == "<p>Build backend systems.</p>"
    assert job.location == "Bengaluru, India"
    assert job.employment_type == "Full-time"


def test_map_greenhouse_job_strips_strings() -> None:
    payload = {
        "company_name": "  Acme  ",
        "title": "  Python Engineer  ",
        "absolute_url": "  https://example.com/jobs/123  ",
        "content": "  Description  ",
        "location": {
            "name": "  Bengaluru  ",
        },
    }

    job = map_greenhouse_job(payload)

    assert job.company == "Acme"
    assert job.title == "Python Engineer"
    assert job.source_url == "https://example.com/jobs/123"
    assert job.description == "Description"
    assert job.location == "Bengaluru"


def test_map_greenhouse_job_supports_missing_optional_fields() -> None:
    payload = {
        "company_name": "Acme",
        "title": "Python Engineer",
        "absolute_url": "https://example.com/jobs/123",
    }

    job = map_greenhouse_job(payload)

    assert job.description is None
    assert job.location is None
    assert job.employment_type is None


def test_map_greenhouse_job_rejects_missing_company() -> None:
    payload = {
        "title": "Python Engineer",
        "absolute_url": "https://example.com/jobs/123",
    }

    try:
        map_greenhouse_job(payload)
    except ValueError as exc:
        assert "company_name" in str(exc)
    else:
        raise AssertionError("Expected ValueError")


def test_map_greenhouse_job_rejects_missing_title() -> None:
    payload = {
        "company_name": "Acme",
        "absolute_url": "https://example.com/jobs/123",
    }

    try:
        map_greenhouse_job(payload)
    except ValueError as exc:
        assert "title" in str(exc)
    else:
        raise AssertionError("Expected ValueError")


def test_map_greenhouse_job_rejects_missing_source_url() -> None:
    payload = {
        "company_name": "Acme",
        "title": "Python Engineer",
    }

    try:
        map_greenhouse_job(payload)
    except ValueError as exc:
        assert "absolute_url" in str(exc)
    else:
        raise AssertionError("Expected ValueError")


def test_map_greenhouse_job_ignores_unknown_employment_metadata() -> None:
    payload = {
        "company_name": "Acme",
        "title": "Python Engineer",
        "absolute_url": "https://example.com/jobs/123",
        "metadata": [
            {
                "name": "Department",
                "value": "Engineering",
            },
        ],
    }

    job = map_greenhouse_job(payload)

    assert job.employment_type is None
