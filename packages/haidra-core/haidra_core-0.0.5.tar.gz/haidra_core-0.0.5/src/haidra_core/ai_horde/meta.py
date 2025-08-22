from pydantic import Field

from haidra_core.meta import SharedCISettings


class AIHordeCISettings(SharedCISettings):
    """Settings for AI Horde CI/CD pipelines."""

    hordelib_ci_ongoing: bool = Field(default=False)
    """Indicates if the hordelib CI/CD pipeline is ongoing."""

    horde_sdk_testing: bool = Field(default=False)
    """Indicates if the AI Horde SDK is currently being tested."""

    ai_horde_testing: bool = Field(default=False)
    """Indicates if the AI Horde is currently being tested."""
