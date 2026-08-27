from packages.database.models.job_skill import JobSkill as JobSkillModel
from packages.database.models.skill import CandidateSkill as CandidateSkillModel
from packages.database.models.skill import Skill as SkillModel
from packages.domain.jobs.skill import JobSkill
from packages.domain.skills.entities import CandidateSkill, Skill


def skill_to_domain(model: SkillModel) -> Skill:
    """Convert a database skill model into a domain entity."""
    return Skill(
        id=model.id,
        name=model.name,
    )


def skill_to_model(entity: Skill) -> SkillModel:
    """Convert a domain skill entity into a database model."""
    return SkillModel(
        id=entity.id,
        name=entity.name,
    )


def candidate_skill_to_domain(
    model: CandidateSkillModel,
) -> CandidateSkill:
    """Convert a database candidate-skill model into a domain entity."""
    return CandidateSkill(
        candidate_id=model.candidate_id,
        skill_id=model.skill_id,
        proficiency=model.proficiency,
    )


def candidate_skill_to_model(
    entity: CandidateSkill,
) -> CandidateSkillModel:
    """Convert a domain candidate-skill entity into a database model."""
    return CandidateSkillModel(
        candidate_id=entity.candidate_id,
        skill_id=entity.skill_id,
        proficiency=entity.proficiency,
    )


def job_skill_to_domain(model: JobSkillModel) -> JobSkill:
    """Convert a database job-skill model into a domain entity."""
    return JobSkill(
        job_id=model.job_id,
        skill_id=model.skill_id,
    )


def job_skill_to_model(entity: JobSkill) -> JobSkillModel:
    """Convert a domain job-skill entity into a database model."""
    return JobSkillModel(
        job_id=entity.job_id,
        skill_id=entity.skill_id,
    )
