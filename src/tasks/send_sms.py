import logging

from src.config import setting
from src.core import celery_app
from src.utils.sms import SmsPanelFactory

logger = logging.getLogger("mechanic")

@celery_app.task(queue="send_sms")
def send_sms(phone_number: str, message: str):
    panel = SmsPanelFactory.get_sms_panel(setting.SMS_PANEL)
    panel.send_to_one(phone_number, message)