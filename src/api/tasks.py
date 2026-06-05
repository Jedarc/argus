import os

from celery import Celery

celery_app = Celery(
    "argus",
    broker=os.environ.get("REDIS_URL", "redis://redis:6379/0"),
    backend=os.environ.get("REDIS_URL", "redis://redis:6379/0"),
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
)


# Tasks registered here as modules are implemented:
# @celery_app.task(bind=True)
# def run_module_task(self, job_id: int, module_name: str, target_value: str): ...
