"""Custom exception classes for ai-ffmpeg-cli.

This module defines application-specific exception types that provide
clear error categorization and handling throughout the application.
Each exception type corresponds to a specific failure scenario in
the processing pipeline.
"""


class ConfigError(Exception):
    """Raised when configuration or environment validation fails.

    This exception is raised when there are issues with:
    - Missing or invalid environment variables
    - Configuration file problems
    - Missing dependencies (e.g., ffmpeg not in PATH)
    - Invalid API keys or credentials

    This exception should be handled at the application level to
    provide clear guidance to users about configuration issues.
    """


class ParseError(Exception):
    """Raised when the LLM fails to produce a valid intent.

    This exception is raised when:
    - Natural language parsing fails
    - LLM returns invalid JSON
    - Intent validation fails
    - API communication errors occur

    This exception indicates issues with the LLM processing pipeline
    and should be handled with appropriate retry logic or user guidance.
    """


class BuildError(Exception):
    """Raised when an intent cannot be routed or converted into commands.

    This exception is raised when:
    - Intent routing fails
    - Command plan generation fails
    - Security validation fails
    - Unsupported operations are requested

    This exception indicates issues with converting user intent into
    executable commands and should be handled with clear error messages.
    """


class ExecError(Exception):
    """Raised when command execution fails.

    This exception is raised when:
    - ffmpeg command execution fails
    - File operations fail
    - Permission issues occur
    - System resource problems

    This exception indicates runtime execution failures and should
    be handled with appropriate error recovery or user notification.
    """
