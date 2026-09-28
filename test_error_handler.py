from src.error_handler import (
    safe_error_message,
    handle_application_error,
)


def test_safe_error_message_returns_readable_message():
    error = ValueError("invalid evidence")

    message = safe_error_message(error)

    assert "ValueError" in message
    assert "invalid evidence" in message


def test_safe_error_message_handles_none():
    assert safe_error_message(None) == "Unknown error."


def test_handle_application_error_returns_failure_result():
    error = RuntimeError("unexpected failure")

    result = handle_application_error(error)

    assert result["success"] is False
    assert result["error_type"] == "RuntimeError"
    assert "unexpected failure" in result["error"]


def test_handle_application_error_does_not_raise():
    error = Exception("controlled failure")

    result = handle_application_error(error)

    assert isinstance(result, dict)
    assert result["success"] is False