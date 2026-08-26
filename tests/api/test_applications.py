from uuid import uuid4

from httpx import ASGITransport, AsyncClient

from packages.api.app import app


async def create_candidate(client: AsyncClient) -> str:
    response = await client.post(
        "/candidates",
        json={
            "full_name": "Application Test Candidate",
            "email": f"application-{uuid4()}@example.com",
            "phone": None,
            "location": "Kerala",
        },
    )

    assert response.status_code == 201

    return response.json()["id"]


async def create_job(client: AsyncClient) -> str:
    response = await client.post(
        "/jobs",
        json={
            "company": "Application Test Company",
            "title": "Python Backend Engineer",
            "source": "Example",
            "source_url": f"https://example.com/jobs/{uuid4()}",
            "description": "Backend engineering role.",
            "location": "Bangalore",
            "employment_type": "Full-time",
        },
    )

    assert response.status_code == 201

    return response.json()["id"]


async def create_resume(
    client: AsyncClient,
    candidate_id: str,
) -> str:
    response = await client.post(
        "/resumes",
        json={
            "candidate_id": candidate_id,
            "filename": "resume.pdf",
            "content_type": "application/pdf",
            "storage_key": f"resumes/{uuid4()}.pdf",
            "parsed_text": "Python FastAPI backend developer.",
            "is_canonical": True,
        },
    )

    assert response.status_code == 201

    return response.json()["id"]


async def create_application(
    client: AsyncClient,
) -> tuple[str, str, str, str]:
    candidate_id = await create_candidate(client)
    job_id = await create_job(client)
    resume_id = await create_resume(client, candidate_id)

    response = await client.post(
        "/applications",
        json={
            "candidate_id": candidate_id,
            "job_id": job_id,
            "resume_id": resume_id,
        },
    )

    assert response.status_code == 201

    application_id = response.json()["id"]

    return application_id, candidate_id, job_id, resume_id


async def test_create_application() -> None:
    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as client:
        application_id, candidate_id, job_id, resume_id = await create_application(client)

        response = await client.get(
            f"/applications/{application_id}",
        )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == application_id
    assert data["candidate_id"] == candidate_id
    assert data["job_id"] == job_id
    assert data["resume_id"] == resume_id
    assert data["status"] == "draft"
    assert data["applied_at"] is None
    assert data["external_application_url"] is None
    assert data["failure_reason"] is None


async def test_get_application_returns_404_when_missing() -> None:
    transport = ASGITransport(app=app)

    missing_application_id = uuid4()

    async with AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as client:
        response = await client.get(
            f"/applications/{missing_application_id}",
        )

    assert response.status_code == 404
    assert str(missing_application_id) in response.json()["detail"]


async def test_create_application_rejects_duplicate() -> None:
    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as client:
        candidate_id = await create_candidate(client)
        job_id = await create_job(client)
        resume_id = await create_resume(client, candidate_id)

        payload = {
            "candidate_id": candidate_id,
            "job_id": job_id,
            "resume_id": resume_id,
        }

        first_response = await client.post(
            "/applications",
            json=payload,
        )

        second_response = await client.post(
            "/applications",
            json=payload,
        )

    assert first_response.status_code == 201
    assert second_response.status_code == 409
    assert "already exists" in second_response.json()["detail"]


async def test_list_candidate_applications() -> None:
    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as client:
        candidate_id = await create_candidate(client)
        job_id = await create_job(client)
        resume_id = await create_resume(client, candidate_id)

        response = await client.post(
            "/applications",
            json={
                "candidate_id": candidate_id,
                "job_id": job_id,
                "resume_id": resume_id,
            },
        )

        assert response.status_code == 201

        application_id = response.json()["id"]

        response = await client.get(
            f"/applications/candidate/{candidate_id}",
        )

    assert response.status_code == 200

    data = response.json()

    application_ids = {application["id"] for application in data}

    assert application_id in application_ids


async def test_list_job_applications() -> None:
    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as client:
        candidate_id = await create_candidate(client)
        job_id = await create_job(client)
        resume_id = await create_resume(client, candidate_id)

        response = await client.post(
            "/applications",
            json={
                "candidate_id": candidate_id,
                "job_id": job_id,
                "resume_id": resume_id,
            },
        )

        assert response.status_code == 201

        application_id = response.json()["id"]

        response = await client.get(
            f"/applications/job/{job_id}",
        )

    assert response.status_code == 200

    data = response.json()

    application_ids = {application["id"] for application in data}

    assert application_id in application_ids


async def test_update_application() -> None:
    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as client:
        application_id, _, _, _ = await create_application(client)

        response = await client.patch(
            f"/applications/{application_id}",
            json={
                "notes": "Tailored resume for backend role.",
            },
        )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == application_id
    assert data["notes"] == "Tailored resume for backend role."


async def test_update_application_returns_404_when_missing() -> None:
    transport = ASGITransport(app=app)

    missing_application_id = uuid4()

    async with AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as client:
        response = await client.patch(
            f"/applications/{missing_application_id}",
            json={
                "notes": "This should fail.",
            },
        )

    assert response.status_code == 404
    assert str(missing_application_id) in response.json()["detail"]


async def test_delete_application() -> None:
    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as client:
        application_id, _, _, _ = await create_application(client)

        delete_response = await client.delete(
            f"/applications/{application_id}",
        )

        get_response = await client.get(
            f"/applications/{application_id}",
        )

    assert delete_response.status_code == 204
    assert get_response.status_code == 404


async def test_delete_application_returns_404_when_missing() -> None:
    transport = ASGITransport(app=app)

    missing_application_id = uuid4()

    async with AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as client:
        response = await client.delete(
            f"/applications/{missing_application_id}",
        )

    assert response.status_code == 404


async def test_submit_application() -> None:
    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as client:
        application_id, _, _, _ = await create_application(client)

        await client.patch(
            f"/applications/{application_id}",
            json={
                "status": "ready",
            },
        )

        response = await client.post(
            f"/applications/{application_id}/submit",
        )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == application_id
    assert data["status"] == "submitted"
    assert data["applied_at"] is not None
    assert data["external_application_url"] is not None
    assert data["failure_reason"] is None


async def test_submit_application_rejects_draft() -> None:
    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as client:
        application_id, _, _, _ = await create_application(client)

        response = await client.post(
            f"/applications/{application_id}/submit",
        )

    assert response.status_code == 409


async def test_submit_application_returns_404_when_missing() -> None:
    transport = ASGITransport(app=app)

    missing_application_id = uuid4()

    async with AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as client:
        response = await client.post(
            f"/applications/{missing_application_id}/submit",
        )

    assert response.status_code == 404
