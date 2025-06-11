from celery import shared_task


# health check
@shared_task
def ping():
    print("PONG")
