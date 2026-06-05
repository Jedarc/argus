import os

from celery import Celery
from kombu import Exchange, Queue

_BROKER_URL = os.environ.get("CELERY_BROKER_URL", "redis://redis:6379/1")
_RESULT_BACKEND = os.environ.get("CELERY_RESULT_BACKEND", "redis://redis:6379/2")

# All Celery queues are prefixed with "argus." to avoid collisions when the
# broker is shared with other services on the same Redis instance.
_QUEUE_DEFAULT = "argus.default"
_QUEUE_DLQ = "argus.dlq"

_default_exchange = Exchange(_QUEUE_DEFAULT, type="direct")
_dlq_exchange = Exchange(_QUEUE_DLQ, type="direct")

celery_app = Celery("argus", broker=_BROKER_URL, backend=_RESULT_BACKEND)

celery_app.conf.update(
    # Serialization
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,

    # Queue routing
    task_queues=[
        Queue(_QUEUE_DEFAULT, _default_exchange, routing_key=_QUEUE_DEFAULT),
        Queue(_QUEUE_DLQ, _dlq_exchange, routing_key=_QUEUE_DLQ),
    ],
    task_default_queue=_QUEUE_DEFAULT,
    task_default_exchange=_QUEUE_DEFAULT,
    task_default_routing_key=_QUEUE_DEFAULT,

    # Reliability
    task_acks_late=True,            # Acknowledge only after task completes, not on receipt
    task_reject_on_worker_lost=True,# Re-queue if worker dies mid-task

    # Time limits — soft limit raises SoftTimeLimitExceeded (catchable),
    # hard limit sends SIGKILL. Modules should respect the soft limit.
    task_soft_time_limit=300,       # 5 min — modules must finish or raise gracefully
    task_time_limit=360,            # 6 min — hard kill

    # Retry — tasks declare their own max_retries; this is the global cap.
    task_max_retries=2,

    # Concurrency — one task at a time per worker process to prevent
    # subprocess tools (Sherlock, Holehe) from competing for resources.
    worker_prefetch_multiplier=1,

    # Result expiry — keep job results in Redis for 24h, then expire.
    result_expires=86400,

    # Worker naming — prefix with argus so celery inspect output is unambiguous
    # when multiple Celery apps share the same broker.
    worker_hijack_root_logger=False,  # Let our structlog config own the root logger
)


# Tasks are registered here as modules are implemented.
# Each task must:
#   1. Accept job_id, module_name, target_value, api_key
#   2. Update Job.status → running on start, completed/failed on finish
#   3. Persist a Result row regardless of outcome
#   4. Emit a WebSocket event after each status transition
#   5. On permanent failure, route to the DLQ and set Job.status → failed
#
# Example skeleton:
#
# from celery.exceptions import SoftTimeLimitExceeded
#
# @celery_app.task(
#     bind=True,
#     name="argus.run_module",
#     max_retries=2,
#     default_retry_delay=5,
# )
# def run_module_task(self, job_id: int, module_name: str, target_value: str, api_key: str | None = None):
#     from api.database import SessionLocal
#     from api.models.job import Job, JobStatus
#     from api.modules import ALL_MODULES
#     from api.resilience import is_retryable_error
#     from api.logging_config import get_logger
#
#     log = get_logger(__name__).bind(job_id=job_id, module=module_name)
#     session = SessionLocal()
#
#     try:
#         job = session.get(Job, job_id)
#         job.status = JobStatus.running
#         session.commit()
#         log.info("module_started")
#
#         module = next(m for m in ALL_MODULES if m.name == module_name)
#         result = module.run(target_value, api_key)
#
#         # persist result, update job...
#         log.info("module_completed", found=result.found)
#
#     except SoftTimeLimitExceeded:
#         log.warning("module_timeout")
#         job.status = JobStatus.failed
#         job.error = "Module exceeded time limit"
#         session.commit()
#
#     except Exception as exc:
#         log.error("module_error", error=str(exc), exc_info=True)
#         if is_retryable_error(exc):
#             raise self.retry(exc=exc)
#         job.status = JobStatus.failed
#         job.error = str(exc)
#         session.commit()
#         # Route to DLQ for inspection
#         self.apply_async(queue=_QUEUE_DLQ, args=[job_id, module_name, target_value])
#
#     finally:
#         session.close()
