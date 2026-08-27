from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class CandidateProfile:
    """Professional profile associated with a candidate."""

    headline: str | None = None
    summary: str | None = None

    years_of_experience: float | None = None

    current_job_title: str | None = None
    current_company: str | None = None

    current_salary: int | None = None
    expected_salary: int | None = None

    notice_period_days: int | None = None

    highest_qualification: str | None = None
    career_level: str | None = None

    work_authorization: str | None = None

    willing_to_relocate: bool = False

    remote_preference: str | None = None