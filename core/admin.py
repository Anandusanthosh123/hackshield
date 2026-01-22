# core/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    CustomUser, Question, UserQuizSession, Badge, UserBadge,
    UserProgress, Course, Lesson, UserCourseProgress,
    Game, GameProgress, Certificate, Challenge, ChallengeAttempt,
    HackingLab, UserLabProgress
)
from .models import (
    CourseQuizQuestion,
    CourseQuizOption,
    CourseQuizAttempt,
)


# -----------------------
# CustomUser admin
# -----------------------
@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = (
        'username', 'email', 'level', 'xp',
        'cyber_score', 'cyber_coins', 'streak', 'last_active', 'is_staff'
    )
    list_filter = ('is_staff', 'is_superuser', 'level')
    search_fields = ('username', 'email')

    fieldsets = UserAdmin.fieldsets + (
        ('Gamification', {
            'fields': (
                'xp', 'level', 'cyber_score', 'cyber_coins',
                'streak', 'last_active', 'avatar', 'cover_photo'
            )
        }),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Gamification', {
            'fields': ('xp', 'level', 'cyber_score', 'cyber_coins', 'streak')
        }),
    )


# -----------------------
# Quiz / Questions
# -----------------------
@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('short_text', 'difficulty', 'xp_reward', 'coin_reward')
    list_filter = ('difficulty',)
    search_fields = ('text',)

    def short_text(self, obj):
        return obj.text[:70]
    short_text.short_description = "Question"


@admin.register(UserQuizSession)
class UserQuizSessionAdmin(admin.ModelAdmin):
    list_display = ('user', 'question', 'is_correct', 'time_taken', 'completed_at')
    list_filter = ('is_correct',)
    readonly_fields = ('completed_at',)


# -----------------------
# Badges
# -----------------------
@admin.register(Badge)
class BadgeAdmin(admin.ModelAdmin):
    list_display = ('name', 'icon_preview', 'xp_required')
    search_fields = ('name', 'description')
    list_filter = ('xp_required',)
    ordering = ('xp_required',)

    fields = ('name', 'icon', 'description', 'xp_required')

    def icon_preview(self, obj):
        # If icon is emoji → show it bigger
        if obj.icon and len(obj.icon) <= 4:
            return f"<span style='font-size:24px;'>{obj.icon}</span>"
        # If icon is image URL → show image
        if obj.icon.startswith("http"):
            return f"<img src='{obj.icon}' width='32' height='32'/>"
        return obj.icon

    icon_preview.short_description = "Icon"
    icon_preview.allow_tags = True

# -----------------------
# Daily Progress
# -----------------------
@admin.register(UserProgress)
class UserProgressAdmin(admin.ModelAdmin):
    list_display = ('user', 'date', 'xp_gained', 'streak')
    list_filter = ('date',)
    search_fields = ('user__username',)


# -----------------------
# Courses & Lessons
# -----------------------
class LessonInline(admin.StackedInline):
    model = Lesson
    extra = 0
    ordering = ('order',)
    fields = (
        'title',
        'order',
        'content',
        'video_1',
        'video_2',
        'image_1',
        'image_2',
    )

class CourseQuizOptionInline(admin.TabularInline):
    model = CourseQuizOption
    extra = 4
    fields = ('text', 'is_correct')


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'difficulty', 'xp_reward', 'created_at')
    search_fields = ('title',)
    prepopulated_fields = {'slug': ('title',)}
    inlines = [LessonInline]


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'order')
    search_fields = ('title', 'course__title')
    
    
    
@admin.register(CourseQuizQuestion)
class CourseQuizQuestionAdmin(admin.ModelAdmin):
    list_display = ('course', 'short_question', 'order')
    list_filter = ('course',)
    search_fields = ('question',)
    ordering = ('course', 'order')
    inlines = [CourseQuizOptionInline]

    def short_question(self, obj):
        return obj.question[:80]
    short_question.short_description = "Question"

@admin.register(CourseQuizAttempt)
class CourseQuizAttemptAdmin(admin.ModelAdmin):
    list_display = ('user', 'course', 'attempt_no', 'score', 'passed', 'attempted_at')
    list_filter = ('passed', 'course')
    search_fields = ('user__username', 'course__title')
    readonly_fields = ('attempted_at',)


@admin.register(UserCourseProgress)
class UserCourseProgressAdmin(admin.ModelAdmin):
    list_display = ('user', 'course', 'completed', 'enrolled_at', 'updated_at')
    list_filter = ('completed',)
    search_fields = ('user__username', 'course__title')
    readonly_fields = ('enrolled_at', 'updated_at')


# -----------------------
# Games
# -----------------------
@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'xp_reward', 'created_at')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)


@admin.register(GameProgress)
class GameProgressAdmin(admin.ModelAdmin):
    list_display = ('user', 'game', 'played', 'best_score', 'last_played')
    readonly_fields = ('last_played',)


# -----------------------
# Certificates
# -----------------------
@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = ('user', 'title', 'issued_at', 'related_course', 'downloadable')
    readonly_fields = ('issued_at',)
    search_fields = ('user__username', 'title')


# -----------------------
# Challenges
# -----------------------
@admin.register(Challenge)
class ChallengeAdmin(admin.ModelAdmin):
    list_display = ('title', 'difficulty', 'xp_reward', 'created_at')
    prepopulated_fields = {'slug': ('title',)}
    search_fields = ('title', 'description')


@admin.register(ChallengeAttempt)
class ChallengeAttemptAdmin(admin.ModelAdmin):
    list_display = ('user', 'challenge', 'attempts', 'solved', 'started_at', 'solved_at')
    list_filter = ('solved',)
    readonly_fields = ('started_at', 'solved_at', 'updated_at')
    search_fields = ('user__username', 'challenge__title')


# -----------------------
# 🧪 Hacking Labs
# -----------------------
@admin.register(HackingLab)
class HackingLabAdmin(admin.ModelAdmin):
    list_display = ('title', 'difficulty', 'xp_reward', 'badge_reward', 'created_at')
    search_fields = ('title', 'description')
    prepopulated_fields = {'slug': ('title',)}
    list_filter = ('difficulty',)


@admin.register(UserLabProgress)
class UserLabProgressAdmin(admin.ModelAdmin):
    list_display = (
        'user', 'lab', 'completed',
        'started_at', 'completed_at',
        'kali_container_id', 'ubuntu_container_id', 'network_name'
    )
    list_filter = ('completed',)
    search_fields = ('user__username', 'lab__title')
    readonly_fields = ('started_at', 'completed_at')
    from .models import HackingLab, UserLabProgress



