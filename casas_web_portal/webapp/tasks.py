import logging

from django.conf import settings
from huey.contrib.djhuey import on_commit_task

from casas_web_portal.functions import _send_mail

logger = logging.getLogger()


def _job_url(job):
    """Return the URL of the job page, absolute when APP_URL is configured."""
    app_url = getattr(settings, "APP_URL", "")
    if app_url:
        return f"https://{app_url}/job/{job.id}"
    return f"/job/{job.id}"


def _notify(job, subject, text):
    """Send a notification email about the job, without failing the task."""
    try:
        _send_mail(subject, text, job.user)
    except Exception as err:
        logger.exception(f"Error sending the email for job {job.id}: {err}")


@on_commit_task()
def run_job(job_id):
    """Run the model of a job and notify the user when it is finished.

    Args:
        job_id (int): the id of the job to run
    """
    from webapp.models import Job

    job = Job.objects.get(pk=job_id)
    try:
        job.run_model()
    except Exception as err:
        logger.exception(f"Model run for job {job.id} failed: {err}")
        _notify(
            job,
            f"CASAS job '{job.name}' failed",
            f"The model run for the job '{job.name}' failed:\n\n{err}",
        )
        raise
    _notify(
        job,
        f"CASAS job '{job.name}' completed",
        f"The model run for the job '{job.name}' has been completed.\n\n"
        f"You can download the results from {_job_url(job)}",
    )
