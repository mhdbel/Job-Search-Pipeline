import logging
import os
from typing import Any, Dict

import yaml

logger = logging.getLogger(__name__)

SRC_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SRC_DIR)
DEFAULT_CONFIG_PATH = os.path.join(PROJECT_ROOT, "config.yaml")


def validate_config(config: Dict[str, Any]) -> Dict[str, Any]:
    """Validate required configuration keys and shapes."""

    required_paths = [
        "scraping.job_boards",
    ]

    missing = []
    for path in required_paths:
        cursor: Any = config
        for part in path.split("."):
            if not isinstance(cursor, dict) or part not in cursor:
                missing.append(path)
                break
            cursor = cursor[part]

    if missing:
        logger.error("Missing required configuration keys: %s", ", ".join(missing))
        raise ValueError(f"Missing required configuration keys: {', '.join(missing)}")

    # Validate that job_boards is a list
    job_boards = config.get("scraping", {}).get("job_boards")
    if not isinstance(job_boards, list):
        raise ValueError("'scraping.job_boards' must be a list of job board definitions")

    return config


def load_config(config_path: str | None = None) -> Dict[str, Any]:
    """Load and validate configuration, supporting an override path or environment variable."""

    candidate_path = config_path or os.getenv("JOB_PIPELINE_CONFIG", DEFAULT_CONFIG_PATH)
    if not os.path.exists(candidate_path):
        print(f"Error: Configuration file not found at {candidate_path}")
        return None

    try:
        with open(candidate_path, "r", encoding="utf-8") as handle:
            config = yaml.safe_load(handle) or {}
    except yaml.YAMLError as exc:
        print(f"Error parsing YAML configuration: {exc}")
        return None
    except OSError as exc:
        print(f"Error reading configuration file {candidate_path}: {exc}")
        return None

    try:
        return validate_config(config)
    except ValueError as exc:
        print(f"Error validating configuration: {exc}")
        return None
