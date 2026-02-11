from celery import Celery

from src.config import setting


app = Celery(
    "src",
    broker=setting.REDIS_BROKER_URL,
    backend=setting.REDIS_BROKER_URL,
)

app.autodiscover_tasks([
    "src.tasks",
    "src.tasks.send_sms.send_sms"
])