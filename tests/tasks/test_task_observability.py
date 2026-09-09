from unittest.mock import MagicMock

from app.tasks.report_tasks import generate_report


def test_generate_report_is_bound_task():
    assert generate_report.bind is not None


def test_generate_report_has_retry_configuration():
    assert generate_report.autoretry_for
    assert generate_report.retry_backoff
    assert generate_report.retry_backoff_max