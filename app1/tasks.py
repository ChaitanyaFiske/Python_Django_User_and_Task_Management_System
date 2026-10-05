from celery import shared_task
from datetime import date, timedelta
from celery import shared_task
from django.core.mail import send_mail
from .models import task_detail

@shared_task
def test_celery():
    return "Celery is working!"

@shared_task
def send_task_email(
    subject,
    message,
    recipient_email,
):
    send_mail(
        subject=subject,
        message=message,
        from_email="chaitanyafiske2001@gmail.com",
        recipient_list=[recipient_email],
        fail_silently=False,
    )

    return f"Email sent to {recipient_email}"

@shared_task
def send_task_reminders():
    tomorrow = date.today() + timedelta(days=1)

    tasks = task_detail.objects.select_related("fk_user").filter(
        duedate=tomorrow,
        status__in=["Pending", "Processing"]
    )

    reminder_count = 0

    for task in tasks:
        user = task.fk_user

        if user and user.email:
            send_task_email.delay(
                subject="Task Due Tomorrow",
                message=f"""Hello {user.Name},

This is a reminder that your task is due tomorrow.

Task ID: {task.id}
Task Name: {task.taskname}
Details: {task.taskdetails}
Due Date: {task.duedate}
Status: {task.status}

Please complete the task before the due date.""",
                recipient_email=user.email,
            )

            reminder_count += 1

    return f"{reminder_count} reminder email(s) queued"