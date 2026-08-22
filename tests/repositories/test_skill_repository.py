from collections.abc import AsyncGenerator
from uuid import uuid4

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from packages.database.models.candidate import Candidate
from packages.database.models.skill import CandidateSkill, Skill
from packages.database.repositories.skill import SkillRepository
from packages.database.session import SessionFactory


@pytest.fixture
async def session() -> AsyncGenerator[AsyncSession, None]:
    async with SessionFactory() as session:
        yield session


@pytest.fixture
async def candidate(session: AsyncSession) -> Candidate:
    candidate = Candidate(
        full_name="Skill Test Candidate",
        email=f"skill-test-{uuid4()}@example.com",
    )

    session.add(candidate)
    await session.commit()
    await session.refresh(candidate)

    return candidate


@pytest.mark.asyncio
async def test_create_and_get_skill(
    session: AsyncSession,
) -> None:
    repository = SkillRepository(session)

    skill = Skill(name=f"Python-{uuid4()}")

    created = await repository.create(skill)
    await session.commit()

    assert created.id is not None
    assert created.name.startswith("Python-")

    fetched = await repository.get_by_id(created.id)

    assert fetched is not None
    assert fetched.id == created.id
    assert fetched.name == created.name

    await repository.delete(fetched)
    await session.commit()


@pytest.mark.asyncio
async def test_get_skill_by_name(
    session: AsyncSession,
) -> None:
    repository = SkillRepository(session)

    skill = Skill(name=f"Django-{uuid4()}")

    await repository.create(skill)
    await session.commit()

    fetched = await repository.get_by_name(skill.name)

    assert fetched is not None
    assert fetched.id == skill.id

    await repository.delete(fetched)
    await session.commit()


@pytest.mark.asyncio
async def test_get_nonexistent_skill_returns_none(
    session: AsyncSession,
) -> None:
    repository = SkillRepository(session)

    skill = await repository.get_by_name(
        f"does-not-exist-{uuid4()}",
    )

    assert skill is None


@pytest.mark.asyncio
async def test_get_all_skills_returns_sorted_results(
    session: AsyncSession,
) -> None:
    repository = SkillRepository(session)

    suffix = uuid4()

    first = Skill(name=f"AAA-{suffix}")
    second = Skill(name=f"BBB-{suffix}")
    third = Skill(name=f"CCC-{suffix}")

    await repository.create(third)
    await repository.create(first)
    await repository.create(second)
    await session.commit()

    skills = await repository.get_all()

    names = [skill.name for skill in skills if str(suffix) in skill.name]

    assert names == sorted(names)

    for skill in (first, second, third):
        await repository.delete(skill)

    await session.commit()


@pytest.mark.asyncio
async def test_update_skill(
    session: AsyncSession,
) -> None:
    repository = SkillRepository(session)

    skill = Skill(name=f"Python-{uuid4()}")

    await repository.create(skill)
    await session.commit()

    skill.name = f"Advanced Python-{uuid4()}"

    updated = await repository.update(skill)
    await session.commit()

    assert updated.name.startswith("Advanced Python-")

    fetched = await repository.get_by_id(skill.id)

    assert fetched is not None
    assert fetched.name == updated.name

    await repository.delete(fetched)
    await session.commit()


@pytest.mark.asyncio
async def test_delete_skill(
    session: AsyncSession,
) -> None:
    repository = SkillRepository(session)

    skill = Skill(name=f"Delete Skill-{uuid4()}")

    await repository.create(skill)
    await session.commit()

    skill_id = skill.id

    await repository.delete(skill)
    await session.commit()

    deleted = await repository.get_by_id(skill_id)

    assert deleted is None


@pytest.mark.asyncio
async def test_duplicate_skill_name_raises_integrity_error(
    session: AsyncSession,
) -> None:
    repository = SkillRepository(session)

    first = Skill(name=f"Duplicate-{uuid4()}")

    await repository.create(first)
    await session.commit()
    Skill_name = first.name
    second = Skill(name=Skill_name)

    with pytest.raises(IntegrityError):
        await repository.create(second)

    await session.rollback()

    existing = await repository.get_by_name(Skill_name)

    assert existing is not None
    assert existing.id == first.id

    await repository.delete(existing)
    await session.commit()


@pytest.mark.asyncio
async def test_add_skill_to_candidate(
    session: AsyncSession,
    candidate: Candidate,
) -> None:
    repository = SkillRepository(session)

    skill = Skill(name=f"Python-{uuid4()}")

    await repository.create(skill)
    await session.commit()

    candidate_skill = CandidateSkill(
        candidate_id=candidate.id,
        skill_id=skill.id,
        proficiency="advanced",
    )

    created = await repository.add_to_candidate(candidate_skill)
    await session.commit()

    assert created.candidate_id == candidate.id
    assert created.skill_id == skill.id
    assert created.proficiency == "advanced"

    await repository.remove_from_candidate(created)
    await repository.delete(skill)
    await session.commit()


@pytest.mark.asyncio
async def test_get_candidate_skill(
    session: AsyncSession,
    candidate: Candidate,
) -> None:
    repository = SkillRepository(session)

    skill = Skill(name=f"Python-{uuid4()}")

    await repository.create(skill)
    await session.commit()

    candidate_skill = CandidateSkill(
        candidate_id=candidate.id,
        skill_id=skill.id,
        proficiency="expert",
    )

    await repository.add_to_candidate(candidate_skill)
    await session.commit()

    fetched = await repository.get_candidate_skill(
        candidate.id,
        skill.id,
    )

    assert fetched is not None
    assert fetched.candidate_id == candidate.id
    assert fetched.skill_id == skill.id
    assert fetched.proficiency == "expert"

    await repository.remove_from_candidate(fetched)
    await repository.delete(skill)
    await session.commit()


@pytest.mark.asyncio
async def test_get_candidate_skills(
    session: AsyncSession,
    candidate: Candidate,
) -> None:
    repository = SkillRepository(session)

    first = Skill(name=f"Python-{uuid4()}")
    second = Skill(name=f"Django-{uuid4()}")

    await repository.create(first)
    await repository.create(second)
    await session.commit()

    first_link = CandidateSkill(
        candidate_id=candidate.id,
        skill_id=first.id,
        proficiency="advanced",
    )

    second_link = CandidateSkill(
        candidate_id=candidate.id,
        skill_id=second.id,
        proficiency="intermediate",
    )

    await repository.add_to_candidate(first_link)
    await repository.add_to_candidate(second_link)
    await session.commit()

    skills = await repository.get_candidate_skills(candidate.id)

    skill_ids = {item.skill_id for item in skills}

    assert first.id in skill_ids
    assert second.id in skill_ids

    for item in skills:
        await repository.remove_from_candidate(item)

    await repository.delete(first)
    await repository.delete(second)
    await session.commit()


@pytest.mark.asyncio
async def test_update_candidate_skill(
    session: AsyncSession,
    candidate: Candidate,
) -> None:
    repository = SkillRepository(session)

    skill = Skill(name=f"Python-{uuid4()}")

    await repository.create(skill)
    await session.commit()

    candidate_skill = CandidateSkill(
        candidate_id=candidate.id,
        skill_id=skill.id,
        proficiency="beginner",
    )

    await repository.add_to_candidate(candidate_skill)
    await session.commit()

    candidate_skill.proficiency = "advanced"

    updated = await repository.update_candidate_skill(
        candidate_skill,
    )
    await session.commit()

    assert updated.proficiency == "advanced"

    fetched = await repository.get_candidate_skill(
        candidate.id,
        skill.id,
    )

    assert fetched is not None
    assert fetched.proficiency == "advanced"

    await repository.remove_from_candidate(fetched)
    await repository.delete(skill)
    await session.commit()


@pytest.mark.asyncio
async def test_remove_skill_from_candidate(
    session: AsyncSession,
    candidate: Candidate,
) -> None:
    repository = SkillRepository(session)

    skill = Skill(name=f"Python-{uuid4()}")

    await repository.create(skill)
    await session.commit()

    candidate_skill = CandidateSkill(
        candidate_id=candidate.id,
        skill_id=skill.id,
    )

    await repository.add_to_candidate(candidate_skill)
    await session.commit()

    await repository.remove_from_candidate(candidate_skill)
    await session.commit()

    fetched = await repository.get_candidate_skill(
        candidate.id,
        skill.id,
    )

    assert fetched is None

    await repository.delete(skill)
    await session.commit()


@pytest.mark.asyncio
async def test_duplicate_candidate_skill_raises_integrity_error(
    session: AsyncSession,
    candidate: Candidate,
) -> None:
    repository = SkillRepository(session)

    skill = Skill(name=f"Python-{uuid4()}")

    await repository.create(skill)
    await session.commit()

    candidate_id = candidate.id
    skill_id = skill.id

    first = CandidateSkill(
        candidate_id=candidate_id,
        skill_id=skill_id,
    )

    second = CandidateSkill(
        candidate_id=candidate_id,
        skill_id=skill_id,
    )

    await repository.add_to_candidate(first)
    await session.commit()

    session.expunge(first)

    with pytest.raises(IntegrityError):
        await repository.add_to_candidate(second)

    await session.rollback()

    existing = await repository.get_candidate_skill(
        candidate_id,
        skill_id,
    )

    assert existing is not None
    assert existing.proficiency is None

    await repository.remove_from_candidate(existing)
    await repository.delete(skill)
    await session.commit()


@pytest.mark.asyncio
async def test_delete_candidate_cascades_to_candidate_skills(
    session: AsyncSession,
    candidate: Candidate,
) -> None:
    repository = SkillRepository(session)

    skill = Skill(name=f"Python-{uuid4()}")

    await repository.create(skill)
    await session.commit()

    candidate_skill = CandidateSkill(
        candidate_id=candidate.id,
        skill_id=skill.id,
    )

    await repository.add_to_candidate(candidate_skill)
    await session.commit()

    candidate_id = candidate.id
    skill_id = skill.id

    await session.delete(candidate)
    await session.commit()

    remaining = await repository.get_candidate_skill(
        candidate_id,
        skill_id,
    )

    assert remaining is None

    skill = await repository.get_by_id(skill_id)
    assert skill is not None

    await repository.delete(skill)
    await session.commit()


@pytest.mark.asyncio
async def test_delete_skill_cascades_to_candidate_skills(
    session: AsyncSession,
    candidate: Candidate,
) -> None:
    repository = SkillRepository(session)

    skill = Skill(name=f"Python-{uuid4()}")

    await repository.create(skill)
    await session.commit()

    candidate_skill = CandidateSkill(
        candidate_id=candidate.id,
        skill_id=skill.id,
    )

    await repository.add_to_candidate(candidate_skill)
    await session.commit()

    candidate_id = candidate.id
    skill_id = skill.id

    await repository.delete(skill)
    await session.commit()

    remaining = await repository.get_candidate_skill(
        candidate_id,
        skill_id,
    )

    assert remaining is None
