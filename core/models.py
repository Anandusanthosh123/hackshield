# core/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from django.urls import reverse
import uuid


# ==========================================================
# 👤 CUSTOM USER MODEL
# ==========================================================
class CustomUser(AbstractUser):
    xp = models.IntegerField(default=0)
    level = models.IntegerField(default=1)
    cyber_score = models.FloatField(default=0.0)

    # Profile images
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    cover_photo = models.ImageField(upload_to='covers/', null=True, blank=True)

    # Coins
    cyber_coins = models.IntegerField(default=100)

    # Activity / streak
    streak = models.IntegerField(default=0)
    last_active = models.DateField(null=True, blank=True)

    # Profile info
    full_name = models.CharField(max_length=200, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    passion = models.CharField(max_length=200, blank=True)
    goal = models.CharField(max_length=300, blank=True)
    github = models.URLField(blank=True)
    linkedin = models.URLField(blank=True)

    def __str__(self):
        return self.username

    @property
    def rank(self):
        total_users = CustomUser.objects.count() or 1
        higher = CustomUser.objects.filter(xp__gt=self.xp).count()
        return round((higher / total_users) * 100, 1)

    # ======================================================
    # 🚀 FIXED XP / STREAK SYSTEM + AUTO BADGES
    # ======================================================
    def log_xp(self, amount):
        """Adds XP, updates streak, daily logs, cyber-score."""
        if amount is None or int(amount) <= 0:
            return

        amount = int(amount)
        today = timezone.now().date()
        yesterday = today - timezone.timedelta(days=1)

        had_xp_yesterday = UserProgress.objects.filter(
            user=self, date=yesterday, xp_gained__gt=0
        ).exists()

        today_has_xp = UserProgress.objects.filter(
            user=self, date=today
        ).exists()

        # ---- STREAK UPDATE ----
        if not today_has_xp:
            if had_xp_yesterday:
                self.streak += 1
            else:
                self.streak = 1

        # ---- UPDATE XP ----
        self.xp += amount

        # ---- LEVEL ----
        self.level = 1 + (self.xp // 100)

        # ---- CYBER SCORE ----
        self.cyber_score = round(
            (self.xp / 100.0) + (self.streak * 0.5),
            2
        )

        self.last_active = today
        self.save()

        # ---- DAILY XP LOG ----
        progress, _ = UserProgress.objects.get_or_create(
            user=self,
            date=today,
            defaults={"xp_gained": 0, "streak": self.streak}
        )
        progress.xp_gained += amount
        progress.streak = self.streak
        progress.save()

        # ⭐ AUTO-AWARD BADGES INCLUDING EVENT BADGES
        from .badge_system import check_and_award_badges
        check_and_award_badges(self)



# ==========================================================
# 🧩 QUESTIONS
# ==========================================================
class Question(models.Model):
    text = models.TextField()
    option_a = models.CharField(max_length=200)
    option_b = models.CharField(max_length=200)
    option_c = models.CharField(max_length=200)
    option_d = models.CharField(max_length=200)
    correct_answer = models.CharField(max_length=1, choices=[
        ('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D')
    ])
    explanation = models.TextField(blank=True)
    difficulty = models.CharField(max_length=10, choices=[
        ('Easy', 'Easy'),
        ('Medium', 'Medium'),
        ('Hard', 'Hard'),
    ], default='Medium')
    xp_reward = models.IntegerField(default=10)
    coin_reward = models.IntegerField(default=5)

    def __str__(self):
        return f"{self.text[:50]}..."


class UserQuizSession(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_answer = models.CharField(max_length=1, null=True, blank=True)
    is_correct = models.BooleanField(null=True)
    time_taken = models.FloatField(null=True)
    completed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - Q{self.question.id}"



# ==========================================================
# 🏅 BADGES
# ==========================================================
class Badge(models.Model):
    name = models.CharField(max_length=50)
    icon = models.CharField(max_length=50, default="🏆")
    description = models.TextField(blank=True)
    xp_required = models.IntegerField(default=0)

    def __str__(self):
        return self.name


class UserBadge(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    badge = models.ForeignKey(Badge, on_delete=models.CASCADE)
    awarded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'badge')

    def __str__(self):
        return f"{self.user.username} - {self.badge.name}"



# ==========================================================
# 📈 DAILY XP PROGRESS
# ==========================================================
class UserProgress(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='progress_logs')
    date = models.DateField(default=timezone.now)
    xp_gained = models.IntegerField(default=0)
    streak = models.IntegerField(default=0)

    class Meta:
        unique_together = ('user', 'date')
        ordering = ['-date']

    def __str__(self):
        return f"{self.user.username} – {self.date} – {self.xp_gained} XP"



# ==========================================================
# 🎓 COURSES
# ==========================================================
class Course(models.Model):
    title = models.CharField(max_length=120)
    slug = models.SlugField(unique=True)
    short_description = models.CharField(max_length=255, blank=True)
    detail = models.TextField(blank=True)
    thumbnail = models.ImageField(upload_to='course_thumbs/', null=True, blank=True)
    xp_reward = models.IntegerField(default=100)
    difficulty = models.CharField(max_length=50, choices=[
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    ], default='beginner')
    created_at = models.DateTimeField(auto_now_add=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', '-created_at']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('course_detail', kwargs={'slug': self.slug})



class Lesson(models.Model):
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='lessons'
    )

    title = models.CharField(max_length=200)

    # MAIN CONTENT (TEXT FIRST)
    content = models.TextField(
        help_text="Markdown or HTML supported"
    )

    # OPTIONAL MEDIA
    video_1 = models.FileField(
        upload_to='courses/videos/',
        null=True,
        blank=True
    )
    video_2 = models.FileField(
        upload_to='courses/videos/',
        null=True,
        blank=True
    )

    image_1 = models.ImageField(
        upload_to='courses/images/',
        null=True,
        blank=True
    )
    image_2 = models.ImageField(
        upload_to='courses/images/',
        null=True,
        blank=True
    )

    order = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.course.title} - {self.title}"





# ==========================================================
# 📝 COURSE QUIZ
# ==========================================================
class CourseQuizQuestion(models.Model):
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='quiz_questions'
    )
    question = models.TextField()
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.course.title} - Q{self.order}"



class CourseQuizOption(models.Model):
    question = models.ForeignKey(
        CourseQuizQuestion,
        on_delete=models.CASCADE,
        related_name='options'
    )
    text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.text



class CourseQuizAttempt(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)

    score = models.IntegerField()
    attempt_no = models.PositiveIntegerField()
    passed = models.BooleanField(default=False)
    attempted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'course', 'attempt_no')
        ordering = ['-attempt_no']

    def __str__(self):
        return f"{self.user.username} - {self.course.title} (Attempt {self.attempt_no})"





class UserCourseProgress(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)

    completed_lessons = models.ManyToManyField(Lesson, blank=True)

    current_lesson = models.ForeignKey(
        Lesson,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='+'
    )

    completed = models.BooleanField(default=False)
    enrolled_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)



# ==========================================================
# 🕹️ MINI GAMES
# ==========================================================
class Game(models.Model):
    name = models.CharField(max_length=120)
    slug = models.SlugField(unique=True)
    description = models.CharField(max_length=255, blank=True)
    thumbnail = models.ImageField(upload_to='game_thumbs/', null=True, blank=True)
    xp_reward = models.IntegerField(default=50)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class GameProgress(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    played = models.IntegerField(default=0)
    best_score = models.IntegerField(default=0)
    completed = models.BooleanField(default=False)
    last_played = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('user', 'game')

    def __str__(self):
        return f"{self.user.username} - {self.game.name}"

    def record_play(self, score):
        self.played += 1
        if score > self.best_score:
            self.best_score = score
        self.last_played = timezone.now()
        self.save()



# ==========================================================
# 🧠 CHALLENGES
# ==========================================================
class Challenge(models.Model):
    title = models.CharField(max_length=120)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    difficulty = models.CharField(
        max_length=20,
        choices=[('Easy', 'Easy'), ('Medium', 'Medium'), ('Hard', 'Hard')],
        default='Medium'
    )
    xp_reward = models.IntegerField(default=50)
    flag = models.CharField(max_length=100)
    thumbnail = models.ImageField(upload_to='challenge_thumbs/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class ChallengeAttempt(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    challenge = models.ForeignKey(Challenge, on_delete=models.CASCADE)
    attempts = models.IntegerField(default=0)
    solved = models.BooleanField(default=False)
    started_at = models.DateTimeField(null=True, blank=True)
    solved_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    time_spent = models.DurationField(null=True, blank=True)

    class Meta:
        unique_together = ('user', 'challenge')
        ordering = ['-solved_at', '-started_at']

    def __str__(self):
        return f"{self.user.username} - {self.challenge.title} ({'Done' if self.solved else '❌'})"



# ==========================================================
# 📜 CERTIFICATES
# ==========================================================
class Certificate(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    related_course = models.ForeignKey(
        Course,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    title = models.CharField(max_length=200)
    recipient_name = models.CharField(max_length=200, blank=True)
    file = models.FileField(upload_to='certificates/', null=True, blank=True)

    issued_at = models.DateField(auto_now_add=True)
    issued_by = models.CharField(max_length=120, default='HackShield')

    certificate_id = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False
    )

    downloadable = models.BooleanField(default=True)
    public = models.BooleanField(default=True)

    class Meta:
        unique_together = ('user', 'related_course')
        ordering = ['-issued_at']

    def __str__(self):
        return f"{self.user.username} - {self.title}"


# ==========================================================
# 🧪 HACKING LABS
# ==========================================================
class HackingLab(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    difficulty = models.CharField(max_length=20, choices=[
        ("Easy", "Easy"),
        ("Medium", "Medium"),
        ("Hard", "Hard"),
    ], default="Easy")

    kali_image = models.CharField(max_length=200, default="kalilinux/kali-rolling")
    ubuntu_image = models.CharField(max_length=200, default="ubuntu:latest")

    xp_reward = models.IntegerField(default=50)
    badge_reward = models.ForeignKey("Badge", on_delete=models.SET_NULL, null=True, blank=True)

    initial_instructions = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class UserLabProgress(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    lab = models.ForeignKey(HackingLab, on_delete=models.CASCADE)

    started_at = models.DateTimeField(auto_now_add=True)
    completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)

    kali_container_id = models.CharField(max_length=200, blank=True)
    ubuntu_container_id = models.CharField(max_length=200, blank=True)
    network_name = models.CharField(max_length=200, blank=True)

    class Meta:
        unique_together = ('user', 'lab')

    def __str__(self):
        return f"{self.user.username} - {self.lab.title} ({'Done' if self.completed else 'In Progress'})"
