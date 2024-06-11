"""
Модуль работает с отправкой сообщений на указанную почту.

func:
    send_email: функция отправки сообщения.
"""
import ssl
import smtplib
from string import Template

from config import WOKR_EMAIL, WOKR_EMAIL_PASS, WOKR_PORT, WORK_HOSTNAME


async def send_email(email: str, message: str, context: str):
    """
    Функция отправляет пользователю сообщение на почту.

    args:
        context_ssl: представляет собой контекст для SSL
    """
    context_ssl = ssl.create_default_context()
    try:
        with smtplib.SMTP_SSL(WORK_HOSTNAME, WOKR_PORT,
                              context=context_ssl, timeout=2) as server:
            await server.login(WOKR_EMAIL, WOKR_EMAIL_PASS)
            message = Template(message).substitute(context)
            server.sendmail(WOKR_EMAIL, email, message.encode('utf-8'))
    except smtplib.SMTPException as ex:
        print(f"SMTP error: {ex}")
        raise
    except Exception as ex:
        print(f"Error: {ex}")
        raise
