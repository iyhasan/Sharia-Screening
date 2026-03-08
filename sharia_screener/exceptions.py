from __future__ import annotations


class ScreeningError(Exception):
    """Base error for screening failures."""


class ConfigurationError(ScreeningError):
    """Invalid or missing configuration for a provider or runtime."""


class UpstreamDataError(ScreeningError):
    """Upstream data could not be retrieved or was missing."""


class ValidationError(ScreeningError):
    """Input or data failed validation."""
