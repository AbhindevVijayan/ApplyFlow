
from uuid import uuid4

from httpx import ASGITransport, AsyncClient

from packages.api.app import app


async def test_create_skill() -> None:
    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as client:
        response = await client.post(
            "/skills",
            json={
                "name": f"Python-{uuid4()}",
            },
        )

    assert response.status_code == 201

    data = response.json()

    assert "id" in data
    assert data["name"].startswith("Python-")


async def test_create_skill_rejects_duplicate_name() -> None:
    transport = ASGITransport(app=app)

    skill_name = f"Python-{uuid4()}"

    async with AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as client:
        first_response = await client.post(
            "/skills",
            json={"name": skill_name},
        )

        second_response = await client.post(
            "/skills",
            json={"name": skill_name},
        )

    assert first_response.status_code == 201
    assert second_response.status_code == 409
    assert "already exists" in second_response.json()["detail"]


async def test_list_skills() -> None:
    transport = ASGITransport(app=app)

    first_name = f"Python-{uuid4()}"
    second_name = f"FastAPI-{uuid4()}"

    async with AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as client:
        first_response = await client.post(
            "/skills",
            json={"name": first_name},
        )

        second_response = await client.post(
            "/skills",
            json={"name": second_name},
        )

        assert first_response.status_code == 201
        assert second_response.status_code == 201

        response = await client.get("/skills")

    assert response.status_code == 200

    data = response.json()

    names = {skill["name"] for skill in data}

    assert first_name in names
    assert second_name in names


async def test_get_skill_by_id() -> None:
    transport = ASGITransport(app=app)

    skill_name = f"Python-{uuid4()}"

    async with AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as client:
        create_response = await client.post(
            "/skills",
            json={"name": skill_name},
        )

        assert create_response.status_code == 201

        skill_id = create_response.json()["id"]

        response = await client.get(
            f"/skills/{skill_id}",
        )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == skill_id
    assert data["name"] == skill_name


async def test_get_skill_returns_404_when_missing() -> None:
    transport = ASGITransport(app=app)

    missing_skill_id = uuid4()

    async with AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as client:
        response = await client.get(
            f"/skills/{missing_skill_id}",
        )

    assert response.status_code == 404
    assert str(missing_skill_id) in response.json()["detail"]


async def test_delete_skill() -> None:
    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as client:
        create_response = await client.post(
            "/skills",
            json={
                "name": f"Delete-Skill-{uuid4()}",
            },
        )

        assert create_response.status_code == 201

        skill_id = create_response.json()["id"]

        delete_response = await client.delete(
            f"/skills/{skill_id}",
        )

        get_response = await client.get(
            f"/skills/{skill_id}",
        )

    assert delete_response.status_code == 204
    assert get_response.status_code == 404


async def test_delete_skill_returns_404_when_missing() -> None:
    transport = ASGITransport(app=app)

    missing_skill_id = uuid4()

    async with AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as client:
        response = await client.delete(
            f"/skills/{missing_skill_id}",
        )

    assert response.status_code == 404


async def test_add_skill_to_candidate() -> None:
    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as client:
        candidate_response = await client.post(
            "/candidates",
            json={
                "full_name": "Skill Test Candidate",
                "email": f"skill-{uuid4()}@example.com",
                "phone": None,
                "location": "Kerala",
            },
        )

        assert candidate_response.status_code == 201

        candidate_id = candidate_response.json()["id"]

        skill_response = await client.post(
            "/skills",
            json={
                "name": f"Python-{uuid4()}",
            },
        )

        assert skill_response.status_code == 201

        skill_id = skill_response.json()["id"]

        response = await client.post(
            f"/skills/candidates/{candidate_id}",
            json={
                "skill_id": skill_id,
                "proficiency": "advanced",
            },
        )

    assert response.status_code == 201

    data = response.json()

    assert data["candidate_id"] == candidate_id
    assert data["skill_id"] == skill_id
    assert data["proficiency"] == "advanced"


async def test_add_skill_to_candidate_rejects_duplicate() -> None:
    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as client:
        candidate_response = await client.post(
            "/candidates",
            json={
                "full_name": "Duplicate Skill Candidate",
                "email": f"duplicate-skill-{uuid4()}@example.com",
                "phone": None,
                "location": "Kerala",
            },
        )

        assert candidate_response.status_code == 201

        candidate_id = candidate_response.json()["id"]

        skill_response = await client.post(
            "/skills",
            json={
                "name": f"Python-{uuid4()}",
            },
        )

        assert skill_response.status_code == 201

        skill_id = skill_response.json()["id"]

        first_response = await client.post(
            f"/skills/candidates/{candidate_id}",
            json={
                "skill_id": skill_id,
                "proficiency": "beginner",
            },
        )

        second_response = await client.post(
            f"/skills/candidates/{candidate_id}",
            json={
                "skill_id": skill_id,
                "proficiency": "advanced",
            },
        )

    assert first_response.status_code == 201
    assert second_response.status_code == 409


async def test_get_candidate_skills() -> None:
    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as client:
        candidate_response = await client.post(
            "/candidates",
            json={
                "full_name": "Candidate Skills",
                "email": f"candidate-skills-{uuid4()}@example.com",
                "phone": None,
                "location": "Kerala",
            },
        )

        assert candidate_response.status_code == 201

        candidate_id = candidate_response.json()["id"]

        first_skill_response = await client.post(
            "/skills",
            json={"name": f"Python-{uuid4()}"},
        )

        second_skill_response = await client.post(
            "/skills",
            json={"name": f"FastAPI-{uuid4()}"},
        )

        assert first_skill_response.status_code == 201
        assert second_skill_response.status_code == 201

        first_skill_id = first_skill_response.json()["id"]
        second_skill_id = second_skill_response.json()["id"]

        first_assignment = await client.post(
            f"/skills/candidates/{candidate_id}",
            json={
                "skill_id": first_skill_id,
                "proficiency": "advanced",
            },
        )

        second_assignment = await client.post(
            f"/skills/candidates/{candidate_id}",
            json={
                "skill_id": second_skill_id,
                "proficiency": "intermediate",
            },
        )

        assert first_assignment.status_code == 201
        assert second_assignment.status_code == 201

        response = await client.get(
            f"/skills/candidates/{candidate_id}",
        )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 2

    skill_ids = {item["skill_id"] for item in data}

    assert first_skill_id in skill_ids
    assert second_skill_id in skill_ids


async def test_update_candidate_skill() -> None:
    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as client:
        candidate_response = await client.post(
            "/candidates",
            json={
                "full_name": "Update Skill Candidate",
                "email": f"update-skill-{uuid4()}@example.com",
                "phone": None,
                "location": "Kerala",
            },
        )

        assert candidate_response.status_code == 201

        candidate_id = candidate_response.json()["id"]

        skill_response = await client.post(
            "/skills",
            json={
                "name": f"Python-{uuid4()}",
            },
        )

        assert skill_response.status_code == 201

        skill_id = skill_response.json()["id"]

        add_response = await client.post(
            f"/skills/candidates/{candidate_id}",
            json={
                "skill_id": skill_id,
                "proficiency": "beginner",
            },
        )

        assert add_response.status_code == 201

        response = await client.patch(
            f"/skills/candidates/{candidate_id}/{skill_id}",
            json={
                "skill_id": skill_id,
                "proficiency": "expert",
            },
        )

    assert response.status_code == 200

    data = response.json()

    assert data["candidate_id"] == candidate_id
    assert data["skill_id"] == skill_id
    assert data["proficiency"] == "expert"


async def test_remove_candidate_skill() -> None:
    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as client:
        candidate_response = await client.post(
            "/candidates",
            json={
                "full_name": "Remove Skill Candidate",
                "email": f"remove-skill-{uuid4()}@example.com",
                "phone": None,
                "location": "Kerala",
            },
        )

        assert candidate_response.status_code == 201

        candidate_id = candidate_response.json()["id"]

        skill_response = await client.post(
            "/skills",
            json={
                "name": f"Python-{uuid4()}",
            },
        )

        assert skill_response.status_code == 201

        skill_id = skill_response.json()["id"]

        add_response = await client.post(
            f"/skills/candidates/{candidate_id}",
            json={
                "skill_id": skill_id,
                "proficiency": "advanced",
            },
        )

        assert add_response.status_code == 201

        delete_response = await client.delete(
            f"/skills/candidates/{candidate_id}/{skill_id}",
        )

        get_response = await client.get(
            f"/skills/candidates/{candidate_id}",
        )

    assert delete_response.status_code == 204
    assert get_response.status_code == 200
    assert get_response.json() == []


async def test_add_skill_returns_404_when_candidate_missing() -> None:
    transport = ASGITransport(app=app)

    missing_candidate_id = uuid4()

    async with AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as client:
        skill_response = await client.post(
            "/skills",
            json={
                "name": f"Python-{uuid4()}",
            },
        )

        assert skill_response.status_code == 201

        skill_id = skill_response.json()["id"]

        response = await client.post(
            f"/skills/candidates/{missing_candidate_id}",
            json={
                "skill_id": skill_id,
                "proficiency": "advanced",
            },
        )

    assert response.status_code == 404


async def test_add_skill_returns_404_when_skill_missing() -> None:
    transport = ASGITransport(app=app)

    candidate_id = uuid4()
    missing_skill_id = uuid4()

    async with AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as client:
        candidate_response = await client.post(
            "/candidates",
            json={
                "full_name": "Missing Skill Candidate",
                "email": f"missing-skill-{uuid4()}@example.com",
                "phone": None,
                "location": "Kerala",
            },
        )

        assert candidate_response.status_code == 201

        candidate_id = candidate_response.json()["id"]

        response = await client.post(
            f"/skills/candidates/{candidate_id}",
            json={
                "skill_id": str(missing_skill_id),
                "proficiency": "advanced",
            },
        )

    assert response.status_code == 404


async def test_remove_candidate_skill_returns_404_when_assignment_missing() -> None:
    transport = ASGITransport(app=app)

    candidate_id = uuid4()
    skill_id = uuid4()

    async with AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as client:
        candidate_response = await client.post(
            "/candidates",
            json={
                "full_name": "Missing Assignment Candidate",
                "email": f"missing-assignment-{uuid4()}@example.com",
                "phone": None,
                "location": "Kerala",
            },
        )

        assert candidate_response.status_code == 201

        candidate_id = candidate_response.json()["id"]

        response = await client.delete(
            f"/skills/candidates/{candidate_id}/{skill_id}",
        )

    assert response.status_code == 404

