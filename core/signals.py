from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from .models import UserQuizSession, CustomUser, UserProgress, Badge, UserBadge


@receiver(post_save, sender=UserQuizSession)
def update_user_progress(sender, instance, created, **kwargs):
    """
    Triggered every time a quiz answer is saved.
    Updates XP, streaks, coins, and badges automatically.
    """
    if not created:
        return

    user = instance.user
    question = instance.question

    # ✅ Update XP & Coins if correct
    if instance.is_correct:
        user.xp += question.xp_reward
        user.cyber_coins += question.coin_reward

    # ✅ Update level (e.g. every 100 XP = +1 level)
    user.level = (user.xp // 100) + 1

    # ✅ Handle streak logic
    today = timezone.now().date()
    yesterday = today - timezone.timedelta(days=1)

    played_yesterday = UserProgress.objects.filter(user=user, date=yesterday).exists()

    if played_yesterday:
        user.streak += 1
    else:
        user.streak = 1  # reset to 1 if missed a day

    user.save()

    # ✅ Record daily XP progress
    progress, _ = UserProgress.objects.get_or_create(user=user, date=today)
    progress.xp_gained += question.xp_reward if instance.is_correct else 0
    progress.streak = user.streak
    progress.save()

    # ✅ Auto award badges based on XP thresholds
    for badge in Badge.objects.all():
        if user.xp >= badge.xp_required:
            UserBadge.objects.get_or_create(user=user, badge=badge)
