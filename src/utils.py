"""
Utility functions for the CTCAE standardizer.
"""
import os
import logging
from typing import Dict, Any, Optional


def configure_logging(log_level: str = "INFO") -> None:
    """
    Configure logging for the application.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)

    # Configure root logger
    logging.basicConfig(
        level=numeric_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Configure specific loggers
    for logger_name in ['langchain', 'openai']:
        logging.getLogger(logger_name).setLevel(logging.WARNING)


def load_env_variables() -> Dict[str, str]:
    """
    Load environment variables needed for the application.

    Returns:
        Dictionary with environment variables
    """
    required_vars = [
        'OPENAI_API_KEY',
        'IRIS_HOSTNAME',
        'IRIS_USERNAME',
        'IRIS_PASSWORD'
    ]

    env_vars = {}
    missing_vars = []

    for var in required_vars:
        value = os.getenv(var)
        if value:
            env_vars[var] = value
        else:
            missing_vars.append(var)

    if missing_vars:
        print("Warning: The following environment variables are missing:")
        for var in missing_vars:
            print(f"  - {var}")

    return env_vars


def format_grade_description(description: str, max_length: Optional[int] = None) -> str:
    """
    Format a grade description for display.

    Args:
        description: The grade description to format
        max_length: Maximum length of the formatted description

    Returns:
        Formatted description
    """
    if not description:
        return ""

    # Normalize whitespace
    formatted = " ".join(description.split())

    # Truncate if needed
    if max_length and len(formatted) > max_length:
        formatted = formatted[:max_length - 3] + "..."

    return formatted