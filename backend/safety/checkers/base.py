from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass
class CheckResult:
    """Result from a single safety checker."""

    is_flagged: bool
    categories: list[str] = field(default_factory=list)
    reasons: list[str] = field(default_factory=list)
    raw_scores: dict = field(default_factory=dict)


class SafetyChecker(ABC):
    """Abstract base class for safety checkers."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Unique name for this checker."""
        ...

    @abstractmethod
    def check(self, content: str) -> CheckResult:
        """Check content for safety violations.

        Args:
            content: The text to check.

        Returns:
            CheckResult with flagging details.
        """
        ...
