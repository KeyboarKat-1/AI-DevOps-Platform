class OpenAIConfigurationError(ValueError):
    """Raised when the OpenAI configuration is invalid or missing."""


class OpenAIServiceError(RuntimeError):
    """Raised when an OpenAI request cannot be completed."""
