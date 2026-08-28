import re

from packages.domain.requirements.entities import JobRequirements


class KeywordJobRequirementsExtractor:
    """Extract job requirements using deterministic keyword matching."""

    KNOWN_SKILLS: tuple[str, ...] = (
        "Python",
        "Java",
        "JavaScript",
        "TypeScript",
        "C++",
        "C#",
        "Go",
        "Rust",
        "SQL",
        "MySQL",
        "PostgreSQL",
        "MongoDB",
        "Redis",
        "Django",
        "FastAPI",
        "Flask",
        "React",
        "Angular",
        "Vue",
        "Node.js",
        "Docker",
        "Kubernetes",
        "AWS",
        "Azure",
        "GCP",
        "Git",
        "Linux",
        "Kafka",
        "RabbitMQ",
        "REST",
        "GraphQL",
        "Machine Learning",
        "Deep Learning",
        "TensorFlow",
        "PyTorch",
    )

    def extract(
        self,
        description: str | None,
    ) -> JobRequirements:
        """Extract known skills from a job description."""

        if not description:
            return JobRequirements(required_skills=())

        normalized_description = description.casefold()

        extracted_skills: list[str] = []

        for skill in self.KNOWN_SKILLS:
            pattern = rf"(?<!\w){re.escape(skill.casefold())}(?!\w)"

            if re.search(pattern, normalized_description):
                extracted_skills.append(skill)

        return JobRequirements(
            required_skills=tuple(extracted_skills),
        )
