from app.tasks.result_tasks import process_laboratory_result


def test_result_task_retry_configuration():
    assert process_laboratory_result.autoretry_for
    assert process_laboratory_result.retry_backoff
    assert process_laboratory_result.retry_backoff_max