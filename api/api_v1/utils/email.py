from fastapi import BackgroundTasks
from fastapi_mail import MessageSchema, MessageType, ConnectionConfig, FastMail

from core.config import settings

smtp_config = ConnectionConfig(**settings.smtp.model_dump())
fm = FastMail(smtp_config)


def send_plain_message_to_email(
    subject: str,
    email_address: str,
    body: str,
    background_tasks: BackgroundTasks,
) -> None:
    message = MessageSchema(
        subject=subject,
        recipients=[email_address],
        body=body,
        subtype=MessageType.plain,
    )
    background_tasks.add_task(fm.send_message, message, None)
