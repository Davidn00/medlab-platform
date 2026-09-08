"""Pruebas de la política de tolerancia a fallos de Celery."""

from app.tasks.calibration_tasks import check_calibration_status
from app.tasks.notification_tasks import (
    notify_calibration_expired,
    notify_calibration_expiring,
)
from app.tasks.report_tasks import generate_report
from app.tasks.result_tasks import process_laboratory_result
from app.tasks.retry import (
    TASK_RETRY_BACKOFF,
    TASK_RETRY_BACKOFF_MAX,
    TASK_RETRY_KWARGS,
    TRANSIENT_TASK_ERRORS,
)


def test_calibration_task_has_transient_retry_policy():
    assert check_calibration_status.autoretry_for == TRANSIENT_TASK_ERRORS
    assert check_calibration_status.retry_backoff == TASK_RETRY_BACKOFF
    assert check_calibration_status.retry_backoff_max == TASK_RETRY_BACKOFF_MAX
    assert check_calibration_status.max_retries == TASK_RETRY_KWARGS["max_retries"]


def test_notification_tasks_have_transient_retry_policy():
    for task in (
        notify_calibration_expired,
        notify_calibration_expiring,
    ):
        assert task.autoretry_for == TRANSIENT_TASK_ERRORS
        assert task.retry_backoff == TASK_RETRY_BACKOFF
        assert task.retry_backoff_max == TASK_RETRY_BACKOFF_MAX
        assert task.max_retries == TASK_RETRY_KWARGS["max_retries"]


def test_processing_tasks_have_transient_retry_policy():
    for task in (generate_report, process_laboratory_result):
        assert task.autoretry_for == TRANSIENT_TASK_ERRORS
        assert task.retry_backoff == TASK_RETRY_BACKOFF
        assert task.retry_backoff_max == TASK_RETRY_BACKOFF_MAX
        assert task.max_retries == TASK_RETRY_KWARGS["max_retries"]
