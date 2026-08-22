from uuid import uuid4

from httpx import ASGITransport, AsyncClient

from packages.api.app import app


async def test_create_resume() -> None:
    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as client:
        candidate_response = await client.post(
            "/candidates",
            json={
                "full_name": "Test Candidate",
                "email": f"test-{uuid4()}@example.com",
                "phone": None,
                "location": "Kerala",
            },
        )

        assert candidate_response.status_code == 201

        candidate_data = candidate_response.json()
        candidate_id = candidate_data["id"]

        payload = {
            "candidate_id": candidate_id,
            "filename": "resume.pdf",
            "content_type": "application/pdf",
            "storage_key": f"resumes/{uuid4()}.pdf",
            "parsed_text": "Python developer with FastAPI experience.",
            "is_canonical": True,
        }

        response = await client.post(
            "/resumes",
            json=payload,
        )

    assert response.status_code == 201

    data = response.json()

    assert data["candidate_id"] == candidate_id
    assert data["filename"] == "resume.pdf"
    assert data["content_type"] == "application/pdf"
    assert data["storage_key"] == payload["storage_key"]
    assert data["parsed_text"] == payload["parsed_text"]
    assert data["is_canonical"] is True
    assert "id" in data
    assert "created_at" in data


async def test_get_resume_by_id() -> None:
    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as client:
        candidate_response = await client.post(
            "/candidates",
            json={
                "full_name": "Get Resume Candidate",
                "email": f"get-resume-{uuid4()}@example.com",
                "phone": None,
                "location": "Kerala",
            },
        )

        assert candidate_response.status_code == 201

        candidate_id = candidate_response.json()["id"]

        create_response = await client.post(
            "/resumes",
            json={
                "candidate_id": candidate_id,
                "filename": "backend-resume.pdf",
                "content_type": "application/pdf",
                "storage_key": f"resumes/{uuid4()}.pdf",
                "parsed_text": "Python and FastAPI developer.",
                "is_canonical": True,
            },
        )

        assert create_response.status_code == 201

        resume_id = create_response.json()["id"]

        response = await client.get(
            f"/resumes/{resume_id}",
        )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == resume_id
    assert data["candidate_id"] == candidate_id
    assert data["filename"] == "backend-resume.pdf"
    assert data["content_type"] == "application/pdf"
    assert data["parsed_text"] == "Python and FastAPI developer."
    assert data["is_canonical"] is True


async def test_get_candidate_resumes() -> None:
    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as client:
        candidate_response = await client.post(
            "/candidates",
            json={
                "full_name": "Resume List Candidate",
                "email": f"resume-list-{uuid4()}@example.com",
                "phone": None,
                "location": "Kerala",
            },
        )

        assert candidate_response.status_code == 201

        candidate_id = candidate_response.json()["id"]

        first_resume = await client.post(
            "/resumes",
            json={
                "candidate_id": candidate_id,
                "filename": "resume-v1.pdf",
                "content_type": "application/pdf",
                "storage_key": f"resumes/{uuid4()}.pdf",
                "parsed_text": "Python developer.",
                "is_canonical": False,
            },
        )

        assert first_resume.status_code == 201

        second_resume = await client.post(
            "/resumes",
            json={
                "candidate_id": candidate_id,
                "filename": "resume-v2.pdf",
                "content_type": "application/pdf",
                "storage_key": f"resumes/{uuid4()}.pdf",
                "parsed_text": "Python and FastAPI developer.",
                "is_canonical": True,
            },
        )

        assert second_resume.status_code == 201

        response = await client.get(
            f"/resumes/candidate/{candidate_id}",
        )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 2

    filenames = {resume["filename"] for resume in data}

    assert filenames == {
        "resume-v1.pdf",
        "resume-v2.pdf",
    }

    assert all(resume["candidate_id"] == candidate_id for resume in data)

    canonical_resumes = [resume for resume in data if resume["is_canonical"] is True]

    assert len(canonical_resumes) == 1
    assert canonical_resumes[0]["filename"] == "resume-v2.pdf"


async def test_get_canonical_resume() -> None:
    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as client:
        candidate_response = await client.post(
            "/candidates",
            json={
                "full_name": "Canonical Resume Candidate",
                "email": f"canonical-{uuid4()}@example.com",
                "phone": None,
                "location": "Kerala",
            },
        )

        assert candidate_response.status_code == 201

        candidate_id = candidate_response.json()["id"]

        non_canonical_response = await client.post(
            "/resumes",
            json={
                "candidate_id": candidate_id,
                "filename": "old-resume.pdf",
                "content_type": "application/pdf",
                "storage_key": f"resumes/{uuid4()}.pdf",
                "parsed_text": "Old resume.",
                "is_canonical": False,
            },
        )

        assert non_canonical_response.status_code == 201

        canonical_response = await client.post(
            "/resumes",
            json={
                "candidate_id": candidate_id,
                "filename": "current-resume.pdf",
                "content_type": "application/pdf",
                "storage_key": f"resumes/{uuid4()}.pdf",
                "parsed_text": "Current resume with Python and FastAPI.",
                "is_canonical": True,
            },
        )

        assert canonical_response.status_code == 201

        response = await client.get(
            f"/resumes/candidate/{candidate_id}/canonical",
        )

    assert response.status_code == 200

    data = response.json()

    assert data["candidate_id"] == candidate_id
    assert data["filename"] == "current-resume.pdf"
    assert data["parsed_text"] == ("Current resume with Python and FastAPI.")
    assert data["is_canonical"] is True


async def test_get_canonical_resume_returns_404_when_missing() -> None:
    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as client:
        candidate_response = await client.post(
            "/candidates",
            json={
                "full_name": "No Canonical Resume",
                "email": f"no-canonical-{uuid4()}@example.com",
                "phone": None,
                "location": "Kerala",
            },
        )

        assert candidate_response.status_code == 201

        candidate_id = candidate_response.json()["id"]

        response = await client.get(
            f"/resumes/candidate/{candidate_id}/canonical",
        )

    assert response.status_code == 404

    data = response.json()

    assert "No canonical resume found" in data["detail"]
