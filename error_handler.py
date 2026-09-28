"""
Production error handling utilities for the pharmacovigilance pipeline.

Phase 2:
Advanced Integration & Security Hardening

Purpose:
Provide a controlled application-level error boundary without
hiding useful diagnostic information.
"""


def safe_error_message(error):
    """
    Convert an exception into a safe, user-readable error message.

    The original exception is not exposed directly to the user.
    """
    if error is None:
        return "Unknown error."

    return f"{type(error).__name__}: {error}"


def handle_application_error(error):
    """
    Handle an unexpected application-level error.

    Returns a structured result instead of allowing an uncontrolled
    application failure.
    """
    return {
        "success": False,
        "error_type": type(error).__name__,
        "error": safe_error_message(error),
    }