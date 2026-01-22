from celery import shared_task
from django.utils import timezone
from .models import CustomUser, UserProgress

@shared_task
def reset_streaks():
    """
    Runs daily via Celery Beat.
    Checks if users missed a day, resets streak to 0 if inactive.
    """
    today = timezone.now().date()
    users = CustomUser.objects.all()
    reset_count = 0

    for user in users:
        last_log = UserProgress.objects.filter(user=user).order_by('-date').first()

        # If user never played or missed yesterday → reset streak
        if not last_log or (today - last_log.date).days > 1:
            if user.streak != 0:
                user.streak = 0
                user.save()
                reset_count += 1

    print(f"✅ Celery: {reset_count} user streaks reset successfully.")
    return f"Reset {reset_count} streaks"
