from collections.abc import AsyncGenerator
from uuid import uuid4

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from packages.database.models.job import Job
from packages.database.models.job_skill import JobSkill
from packages.database.models.skill import Skill
from packages.database.repositories.job_skill import JobSkillRepository
from packages.database.session import SessionFactory


@pytest.fixture
async def session() -> AsyncGenerator[AsyncSession, None]:
    async with SessionFactory() as session:
        yield session


@pytest.fixture
async def job(session: AsyncSession) -> Job:
    job = Job(
        company="Job Skill Test Company",
        title="Python Engineer",
        source="test",
        source_url=f"https://example.com/jobs/{uuid4()}",
    )

    session.add(job)
    await session.commit()
    await session.refresh(job)

    return job


@pytest.fixture
async def skill(session: AsyncSession) -> Skill:
    skill = Skill(
        name=f"Python-{uuid4()}",
    )

    session.add(skill)
    await session.commit()
    await session.refresh(skill)

    return skill


@pytest.mark.asyncio
async def test_add_and_get_job_skill(
    session: AsyncSession,
    job: Job,
    skill: Skill,
) -> None:
    repository = JobSkillRepository(session)

    job_skill = JobSkill(
        job_id=job.id,
        skill_id=skill.id,
    )

    created = await repository.add(job_skill)
    await session.commit()

    fetched = await repository.get(
        job.id,
        skill.id,
    )

    assert created.job_id == job.id
    assert created.skill_id == skill.id

    assert fetched is not None
    assert fetched.job_id == job.id
    assert fetched.skill_id == skill.id

    await repository.remove(job.id, skill.id)
    await session.commit()


@pytest.mark.asyncio
async def test_get_nonexistent_job_skill_returns_none(
    session: AsyncSession,
) -> None:
    repository = JobSkillRepository(session)

    result = await repository.get(
        uuid4(),
        uuid4(),
    )

    assert result is None


@pytest.mark.asyncio
async def test_list_for_job_returns_required_skills_in_deterministic_order(
    session: AsyncSession,
    job: Job,
) -> None:
    repository = JobSkillRepository(session)

    first_skill = Skill(name=f"Python-{uuid4()}")
    second_skill = Skill(name=f"Django-{uuid4()}")
    third_skill = Skill(name=f"FastAPI-{uuid4()}")

    session.add_all(
        [
            first_skill,
            second_skill,
            third_skill,
        ],
    )
    await session.commit()

    links = [
        JobSkill(
            job_id=job.id,
            skill_id=third_skill.id,
        ),
        JobSkill(
            job_id=job.id,
            skill_id=first_skill.id,
        ),
        JobSkill(
            job_id=job.id,
            skill_id=second_skill.id,
        ),
    ]

    for link in links:
        await repository.add(link)

    await session.commit()

    result = await repository.list_for_job(job.id)

    assert [item.skill_id for item in result] == sorted(
        [
            first_skill.id,
            second_skill.id,
            third_skill.id,
        ],
    )

    for link in links:
        await repository.remove(
            link.job_id,
            link.skill_id,
        )

    await session.commit()


@pytest.mark.asyncio
async def test_list_for_job_returns_empty_for_job_without_skills(
    session: AsyncSession,
    job: Job,
) -> None:
    repository = JobSkillRepository(session)

    result = await repository.list_for_job(job.id)

    assert result == []


@pytest.mark.asyncio
async def test_duplicate_job_skill_raises_integrity_error(
    session: AsyncSession,
    job: Job,
    skill: Skill,
) -> None:
    repository = JobSkillRepository(session)
    
    job_id = job.id
    skill_id = skill.id

    first = JobSkill(
        job_id=job.id,
        skill_id=skill.id,
    )

    second = JobSkill(
        job_id=job.id,
        skill_id=skill.id,
    )

    await repository.add(first)
    await session.commit()
    
    session.expunge(first)
        
    with pytest.raises(IntegrityError):
        await repository.add(second)

    await session.rollback()

    existing = await repository.get(
        job_id,
        skill_id,
    )

    assert existing is not None
    assert existing.job_id == job_id
    assert existing.skill_id == skill_id

    await repository.remove(
        job_id,
        skill_id,
    )
    await session.commit()


@pytest.mark.asyncio
async def test_remove_job_skill(
    session: AsyncSession,
    job: Job,
    skill: Skill,
) -> None:
    repository = JobSkillRepository(session)

    job_skill = JobSkill(
        job_id=job.id,
        skill_id=skill.id,
    )

    await repository.add(job_skill)
    await session.commit()

    await repository.remove(
        job.id,
        skill.id,
    )
    await session.commit()

    result = await repository.get(
        job.id,
        skill.id,
    )

    assert result is None


@pytest.mark.asyncio
async def test_remove_nonexistent_job_skill_is_noop(
    session: AsyncSession,
) -> None:
    repository = JobSkillRepository(session)

    await repository.remove(
        uuid4(),
        uuid4(),
    )


@pytest.mark.asyncio
async def test_delete_job_cascades_to_job_skills(
    session: AsyncSession,
    job: Job,
    skill: Skill,
) -> None:
    repository = JobSkillRepository(session)

    job_skill = JobSkill(
        job_id=job.id,
        skill_id=skill.id,
    )

    await repository.add(job_skill)
    await session.commit()

    job_id = job.id
    skill_id = skill.id

    await session.delete(job)
    await session.commit()

    result = await repository.get(
        job_id,
        skill_id,
    )

    assert result is None

    remaining_skill = await session.get(Skill, skill_id)

    assert remaining_skill is not None

    await session.delete(remaining_skill)
    await session.commit()


@pytest.mark.asyncio
async def test_delete_skill_cascades_to_job_skills(
    session: AsyncSession,
    job: Job,
    skill: Skill,
) -> None:
    repository = JobSkillRepository(session)

    job_skill = JobSkill(
        job_id=job.id,
        skill_id=skill.id,
    )

    await repository.add(job_skill)
    await session.commit()

    job_id = job.id
    skill_id = skill.id

    await session.delete(skill)
    await session.commit()

    result = await repository.get(
        job_id,
        skill_id,
    )

    assert result is None
