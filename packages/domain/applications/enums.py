from enum import StrEnum


class ApplicationStatus(StrEnum):
    """Lifecycle states for a job application."""

    DISCOVERED = "discovered"
    EVALUATED = "evaluated"
    SHORTLISTED = "shortlisted"
    APPLICATION_STARTED = "application_started"
    APPLIED = "applied"
    ASSESSMENT = "assessment"
    INTERVIEW = "interview"
    OFFER = "offer"
    REJECTED = "rejected"
    WITHDRAWN = "withdrawn"
