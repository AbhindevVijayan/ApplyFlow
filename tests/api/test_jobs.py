from uuid import uuid4

from httpx import ASGITransport, AsyncClient

from packages.api.app import app


async def test_create_job() -> None:
    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as client:
        payload = {
            "company": "Acme Technologies",
            "title": "Python Backend Developer",
            "source": "LinkedIn",
            "source_url": f"https://linkedin.com/jobs/{uuid4()}",
            "description": "Build backend services with Python.",
            "location": "Bangalore",
            "employment_type": "Full-time",
            "discovered_at": "2026-08-21T10:00:00Z",
        }

        response = await client.post(
            "/jobs",
            json=payload,
        )

    assert response.status_code == 201

    data = response.json()

    assert "id" in data
    assert data["company"] == payload["company"]
    assert data["title"] == payload["title"]
    assert data["source"] == payload["source"]
    assert data["source_url"] == payload["source_url"]
    assert data["description"] == payload["description"]
    assert data["location"] == payload["location"]
    assert data["employment_type"] == payload["employment_type"]
    assert data["discovered_at"] is not None
    assert data["created_at"] is not None


async def test_create_job_rejects_duplicate_source_url() -> None:
    transport = ASGITransport(app=app)

    source_url = f"https://example.com/jobs/{uuid4()}"

    async with AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as client:
        payload = {
            "company": "Acme Technologies",
            "title": "Python Developer",
            "source": "Example",
            "source_url": source_url,
        }

        first_response = await client.post(
            "/jobs",
            json=payload,
        )

        assert first_response.status_code == 201

        second_response = await client.post(
            "/jobs",
            json={
                **payload,
                "company": "Another Company",
            },
        )

    assert second_response.status_code == 409
    assert "already exists" in second_response.json()["detail"]


async def test_get_job_by_id() -> None:
    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as client:
        create_response = await client.post(
            "/jobs",
            json={
                "company": "Get Job Company",
                "title": "Backend Engineer",
                "source": "Company Website",
                "source_url": f"https://example.com/jobs/{uuid4()}",
            },
        )

        assert create_response.status_code == 201

        job_id = create_response.json()["id"]

        response = await client.get(
            f"/jobs/{job_id}",
        )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == job_id
    assert data["company"] == "Get Job Company"
    assert data["title"] == "Backend Engineer"


async def test_get_job_returns_404_when_missing() -> None:
    transport = ASGITransport(app=app)

    missing_job_id = uuid4()

    async with AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as client:
        response = await client.get(
            f"/jobs/{missing_job_id}",
        )

    assert response.status_code == 404

    data = response.json()

    assert str(missing_job_id) in data["detail"]


async def test_list_jobs() -> None:
    transport = ASGITransport(app=app)

    first_url = f"https://example.com/jobs/{uuid4()}"
    second_url = f"https://example.com/jobs/{uuid4()}"

    async with AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as client:
        first_response = await client.post(
            "/jobs",
            json={
                "company": "First Company",
                "title": "Python Developer",
                "source": "Example",
                "source_url": first_url,
            },
        )

        second_response = await client.post(
            "/jobs",
            json={
                "company": "Second Company",
                "title": "Backend Engineer",
                "source": "Example",
                "source_url": second_url,
            },
        )

        assert first_response.status_code == 201
        assert second_response.status_code == 201

        response = await client.get("/jobs")

    assert response.status_code == 200

    data = response.json()

    assert len(data) >= 2

    source_urls = {job["source_url"] for job in data}

    assert first_url in source_urls
    assert second_url in source_urls


async def test_update_job() -> None:
    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as client:
        create_response = await client.post(
            "/jobs",
            json={
                "company": "Original Company",
                "title": "Junior Developer",
                "source": "Example",
                "source_url": f"https://example.com/jobs/{uuid4()}",
                "location": "Kochi",
            },
        )

        assert create_response.status_code == 201

        job_id = create_response.json()["id"]

        response = await client.patch(
            f"/jobs/{job_id}",
            json={
                "title": "Python Backend Developer",
                "location": "Bangalore",
            },
        )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == job_id
    assert data["company"] == "Original Company"
    assert data["title"] == "Python Backend Developer"
    assert data["location"] == "Bangalore"


async def test_update_job_preserves_unspecified_fields() -> None:
    transport = ASGITransport(app=app)

    source_url = f"https://example.com/jobs/{uuid4()}"

    async with AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as client:
        create_response = await client.post(
            "/jobs",
            json={
                "company": "Original Company",
                "title": "Original Title",
                "source": "LinkedIn",
                "source_url": source_url,
                "description": "Original description",
                "location": "Kerala",
                "employment_type": "Full-time",
            },
        )

        assert create_response.status_code == 201

        job_id = create_response.json()["id"]

        response = await client.patch(
            f"/jobs/{job_id}",
            json={
                "title": "Updated Title",
            },
        )

    assert response.status_code == 200

    data = response.json()

    assert data["company"] == "Original Company"
    assert data["title"] == "Updated Title"
    assert data["source"] == "LinkedIn"
    assert data["source_url"] == source_url
    assert data["description"] == "Original description"
    assert data["location"] == "Kerala"
    assert data["employment_type"] == "Full-time"


async def test_update_job_can_clear_nullable_fields() -> None:
    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as client:
        create_response = await client.post(
            "/jobs",
            json={
                "company": "Nullable Company",
                "title": "Developer",
                "source": "Example",
                "source_url": f"https://example.com/jobs/{uuid4()}",
                "description": "Some description",
                "location": "Kochi",
                "employment_type": "Full-time",
            },
        )

        assert create_response.status_code == 201

        job_id = create_response.json()["id"]

        response = await client.patch(
            f"/jobs/{job_id}",
            json={
                "description": None,
                "location": None,
                "employment_type": None,
            },
        )

    assert response.status_code == 200

    data = response.json()

    assert data["description"] is None
    assert data["location"] is None
    assert data["employment_type"] is None


async def test_update_job_returns_404_when_missing() -> None:
    transport = ASGITransport(app=app)

    missing_job_id = uuid4()

    async with AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as client:
        response = await client.patch(
            f"/jobs/{missing_job_id}",
            json={
                "title": "Updated Title",
            },
        )

    assert response.status_code == 404


async def test_update_job_rejects_duplicate_source_url() -> None:
    transport = ASGITransport(app=app)

    first_url = f"https://example.com/jobs/{uuid4()}"
    second_url = f"https://example.com/jobs/{uuid4()}"

    async with AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as client:
        first_response = await client.post(
            "/jobs",
            json={
                "company": "First Company",
                "title": "Developer",
                "source": "Example",
                "source_url": first_url,
            },
        )

        second_response = await client.post(
            "/jobs",
            json={
                "company": "Second Company",
                "title": "Developer",
                "source": "Example",
                "source_url": second_url,
            },
        )

        assert first_response.status_code == 201
        assert second_response.status_code == 201

        second_job_id = second_response.json()["id"]

        response = await client.patch(
            f"/jobs/{second_job_id}",
            json={
                "source_url": first_url,
            },
        )

    assert response.status_code == 409
    assert "already exists" in response.json()["detail"]


async def test_delete_job() -> None:
    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as client:
        create_response = await client.post(
            "/jobs",
            json={
                "company": "Delete Company",
                "title": "Developer",
                "source": "Example",
                "source_url": f"https://example.com/jobs/{uuid4()}",
            },
        )

        assert create_response.status_code == 201

        job_id = create_response.json()["id"]

        delete_response = await client.delete(
            f"/jobs/{job_id}",
        )

        get_response = await client.get(
            f"/jobs/{job_id}",
        )

    assert delete_response.status_code == 204
    assert get_response.status_code == 404


async def test_delete_job_returns_404_when_missing() -> None:
    transport = ASGITransport(app=app)

    missing_job_id = uuid4()

    async with AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as client:
        response = await client.delete(
            f"/jobs/{missing_job_id}",
        )

    assert response.status_code == 404
