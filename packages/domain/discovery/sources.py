from collections.abc import Sequence
from typing import Protocol

from packages.domain.discovery.entities import DiscoveredJob


class JobSource(Protocol):
    """Contract implemented by external job sources."""

    @property
    def name(self) -> str:
        """Return the stable source identifier."""
        ...

    async def discover(self) -> Sequence[DiscoveredJob]:
        """Discover jobs from the external source."""
        ...
