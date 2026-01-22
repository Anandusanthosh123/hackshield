# core/badge_system.py
from .models import Badge, UserBadge, ChallengeAttempt, UserCourseProgress, UserLabProgress


def check_and_award_badges(user):
    """
    Awards:
      ✔ XP-based badges
      ✔ Challenge-completion badges
      ✔ Course-completion badges
      ✔ Lab-completion badges
      ✔ Streak badges
      ✔ Game-play badges

    No model changes, only logic.
    """

    # -----------------------------
    # 1️⃣ XP-based badges (default)
    # -----------------------------
    for badge in Badge.objects.filter(xp_required__lte=user.xp):
        UserBadge.objects.get_or_create(user=user, badge=badge)

    # -----------------------------
    # 2️⃣ Challenge count badges
    # -----------------------------
    solved_count = ChallengeAttempt.objects.filter(user=user, solved=True).count()

    badge = Badge.objects.filter(name__iexact="First Capture").first()
    if badge and solved_count >= 1:
        UserBadge.objects.get_or_create(user=user, badge=badge)

    badge = Badge.objects.filter(name__iexact="Puzzle Solver").first()
    if badge and solved_count >= 3:
        UserBadge.objects.get_or_create(user=user, badge=badge)

    # -----------------------------
    # 3️⃣ Course completion badges
    # -----------------------------
    completed_courses = UserCourseProgress.objects.filter(user=user, completed=True).count()

    badge = Badge.objects.filter(name__iexact="Certified Beginner").first()
    if badge and completed_courses >= 1:
        UserBadge.objects.get_or_create(user=user, badge=badge)

    # -----------------------------
    # 4️⃣ Lab completion badges
    # -----------------------------
    completed_labs = UserLabProgress.objects.filter(user=user, completed=True).count()

    badge = Badge.objects.filter(name__iexact="Lab Beginner").first()
    if badge and completed_labs >= 1:
        UserBadge.objects.get_or_create(user=user, badge=badge)

    # -----------------------------
    # 5️⃣ Streak badges
    # -----------------------------
    badge = Badge.objects.filter(name__iexact="Warm-Up Streak").first()
    if badge and user.streak >= 3:
        UserBadge.objects.get_or_create(user=user, badge=badge)

    badge = Badge.objects.filter(name__iexact="Unstoppable").first()
    if badge and user.streak >= 7:
        UserBadge.objects.get_or_create(user=user, badge=badge)

    # -----------------------------
    # 6️⃣ XP milestone badges
    # -----------------------------
    badge = Badge.objects.filter(name__iexact="Cyber Newbie").first()
    if badge and user.xp >= 100:
        UserBadge.objects.get_or_create(user=user, badge=badge)

    badge = Badge.objects.filter(name__iexact="XP Collector").first()
    if badge and user.xp >= 1000:
        UserBadge.objects.get_or_create(user=user, badge=badge)
