import logging

from src.monitoring import get_logger, log_event


def test_get_logger_returns_pipeline_logger():
    logger = get_logger()

    assert isinstance(logger, logging.Logger)
    assert logger.name == "pharmacovigilance_pipeline"


def test_get_logger_reuses_same_logger():
    logger_one = get_logger()
    logger_two = get_logger()

    assert logger_one is logger_two


def test_logger_has_handler():
    logger = get_logger()

    assert len(logger.handlers) >= 1


def test_log_event_does_not_raise():
    log_event(
        "TEST_EVENT",
        drug="ibuprofen",
        record_count=3,
    )


def test_log_event_supports_warning_level():
    log_event(
        "TEST_WARNING",
        level="WARNING",
        reason="test",
    )


def test_log_event_supports_error_level():
    log_event(
        "TEST_ERROR",
        level="ERROR",
        reason="test",
    )