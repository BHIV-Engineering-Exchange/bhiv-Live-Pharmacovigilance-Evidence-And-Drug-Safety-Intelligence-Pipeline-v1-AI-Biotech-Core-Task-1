"""
Production monitoring utilities for the pharmacovigilance pipeline.

Phase 2:
Advanced Integration & Security Hardening

Purpose:
Provide lightweight structured monitoring for pipeline operations.
"""

import logging


LOGGER_NAME = "pharmacovigilance_pipeline"


def get_logger():
    """
    Return the pipeline logger.

    The logger is configured only once to avoid duplicate handlers.
    """
    logger = logging.getLogger(LOGGER_NAME)

    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    logger.setLevel(logging.INFO)
    return logger


def log_event(event, level="INFO", **details):
    """
    Record a structured pipeline monitoring event.

    Parameters:
        event: Short name describing the event.
        level: Logging level.
        details: Additional event information.
    """
    logger = get_logger()

    detail_text = " ".join(
        f"{key}={value}" for key, value in details.items()
    )

    message = event

    if detail_text:
        message = f"{event} | {detail_text}"

    level = level.upper()

    if level == "ERROR":
        logger.error(message)
    elif level == "WARNING":
        logger.warning(message)
    elif level == "DEBUG":
        logger.debug(message)
    else:
        logger.info(message)