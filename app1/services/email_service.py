from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string


class TaskEmailService:

    TEMPLATE_MAP = {
        "created": {
            "subject": "New Task Assigned",
            "html": "emails/task_created.html",
            "text": "emails/text/task_created.txt",
        },
        "updated": {
            "subject": "Task Updated",
            "html": "emails/task_updated.html",
            "text": "emails/text/task_updated.txt",
        },
        "completed": {
            "subject": "Task Completed Successfully",
            "html": "emails/task_completed.html",
            "text": "emails/text/task_completed.txt",
        },
        "reminder": {
            "subject": "Task Due Tomorrow",
            "html": "emails/task_reminder.html",
            "text": "emails/text/task_reminder.txt",
        },
    }

    @classmethod
    def send_task_email(cls, task, event_type):

        if not task.fk_user or not task.fk_user.email:
            return False

        template_config = cls.TEMPLATE_MAP.get(event_type)

        if not template_config:
            raise ValueError(
                f"Unsupported task email event: {event_type}"
            )

        user = task.fk_user

        context = {
            "user_name": user.Name,
            "user_id": user.id,
            "task_id": task.id,
            "task_name": task.taskname,
            "task_details": task.taskdetails,
            "assign_date": task.assigndate,
            "due_date": task.duedate,
            "completion_date": task.completion_date,
            "status": task.status,
        }

        html_content = render_to_string(
            template_config["html"],
            context
        )

        text_content = render_to_string(
            template_config["text"],
            context
        )

        email = EmailMultiAlternatives(
            subject=template_config["subject"],
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[user.email],
        )

        email.attach_alternative(
            html_content,
            "text/html"
        )

        email.send(fail_silently=False)

        return True