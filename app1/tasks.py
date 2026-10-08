from celery import shared_task
from datetime import date, timedelta
from .models import task_detail
from .services.email_service import TaskEmailService


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 3},
)
def send_task_email(self, task_id, event_type):

    try:
        task = (
            task_detail.objects
            .select_related("fk_user")
            .get(id=task_id)
        )

        TaskEmailService.send_task_email(
            task=task,
            event_type=event_type,
        )

        return (
            f"Task email '{event_type}' sent "
            f"for task {task_id}"
        )

    except task_detail.DoesNotExist:
        return f"Task {task_id} does not exist"


@shared_task
def test_celery():
    return "Celery is working!"


@shared_task
def send_task_reminders():

    tomorrow = date.today() + timedelta(days=1)

    tasks = (
        task_detail.objects
        .select_related("fk_user")
        .filter(
            duedate=tomorrow,
            status__in=["Pending", "Processing"],
        )
    )

    reminder_count = 0

    for task in tasks:

        user = task.fk_user

        if user and user.email:

            send_task_email.delay(
                task_id=task.id,
                event_type="reminder",
            )

            reminder_count += 1

    return f"{reminder_count} reminder email(s) queued"