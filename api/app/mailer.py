"""Envoi d'e-mails par SMTP (Proton : smtp.protonmail.ch:587, STARTTLS, jeton SMTP).

Sans SMTP_HOST, rien n'est envoyé (le site fonctionne normalement). L'envoi se fait hors de la requête
(tâche de fond), dans un thread pour ne pas bloquer la boucle asyncio.
"""
import asyncio
import logging
import smtplib
import ssl
from email.message import EmailMessage
from email.utils import formatdate, make_msgid

from .config import get_settings

log = logging.getLogger("mailer")


def _send(to: str, subject: str, text: str, bcc: bool, html: str = "") -> None:
    s = get_settings()
    msg = EmailMessage()
    msg["From"] = s.smtp_from or s.smtp_user
    msg["To"] = to
    msg["Subject"] = subject
    msg["Date"] = formatdate(localtime=True)
    msg["Message-ID"] = make_msgid(domain=(s.smtp_from or s.smtp_user).rsplit("@", 1)[-1].strip("> "))
    msg.set_content(text)
    if html:
        msg.add_alternative(html, subtype="html")   # HTML affiché par les messageries ; texte en secours
    # Copie cachée : l'adresse n'apparaît dans aucun en-tête, seulement dans l'enveloppe SMTP
    rcpt = [to] + ([s.mail_bcc] if bcc and s.mail_bcc and s.mail_bcc.lower() != to.lower() else [])
    with smtplib.SMTP(s.smtp_host, s.smtp_port, timeout=20) as smtp:
        if s.smtp_starttls:
            smtp.starttls(context=ssl.create_default_context())
        if s.smtp_user:
            smtp.login(s.smtp_user, s.smtp_password)
        smtp.send_message(msg, to_addrs=rcpt)


async def send_mail(to: str, subject: str, text: str, bcc: bool = False, html: str = "") -> None:
    if not get_settings().smtp_host or not to:
        return
    try:
        await asyncio.to_thread(_send, to, subject, text, bcc, html)
    except Exception as e:  # un e-mail raté ne doit jamais casser la connexion ou l'inscription
        log.warning("envoi impossible à %s : %s", to, e)
