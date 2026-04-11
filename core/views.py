# core/views.py
import os
import json
import random
import requests
import feedparser

from datetime import datetime

from .models import HackingLab, UserLabProgress

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.http import JsonResponse, HttpResponse, Http404
from django.conf import settings
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.views.decorators.cache import never_cache
from django.urls import reverse
from django.http import FileResponse, Http404
from django.contrib import messages
from django.utils.text import slugify
from .models import Certificate
from .ai_prompts import LAB_AI_SYSTEM_PROMPT
from .forms import RegisterForm, AvatarForm, ProfileForm
import json
import requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import check_password

from django.utils import timezone

from core.models import Challenge, ChallengeAttempt




from .models import (
    CustomUser, Question, Badge, UserBadge, UserProgress,
    Course, Lesson, UserCourseProgress,
    Game, GameProgress,
    Certificate, Challenge, ChallengeAttempt
)

# from .models import (
#     CourseQuizQuestion,
#     CourseQuizOption,
#     CourseQuizAttempt,
# )
from .models import (
    Course,
    Lesson,
    UserCourseProgress,
    CourseQuizAttempt,
)

from core.utils.weasyprint_certificate import generate_certificate_pdf
from django.views.decorators.cache import never_cache
from django.http import FileResponse



# ---------------------------
# Optional BeautifulSoup for better article scraping
# ---------------------------
try:
    from bs4 import BeautifulSoup
    BS_AVAILABLE = True
except Exception:
    BS_AVAILABLE = False

# ---------------------------
# CACHE FILE LOCATIONS (inside core/)
# ---------------------------
CORE_DIR = os.path.dirname(os.path.abspath(__file__))
CACHE_NEWS = os.path.join(CORE_DIR, "news_cache.json")
CACHE_JOBS = os.path.join(CORE_DIR, "jobs_cache.json")


# ---------------------------
# UTIL: load/save simple JSON caches
# ---------------------------
def load_cache(path):
    try:
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as fh:
                return json.load(fh)
    except Exception:
        return []
    return []


def save_cache(path, data):
    try:
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(data, fh, indent=2, ensure_ascii=False)
    except Exception:
        pass


# ---------------------------
# Small helper to fetch article HTML/text (best-effort)
# ---------------------------
def fetch_article_text(url):
    """
    Try to fetch and return readable text for an article URL.
    If BeautifulSoup is not installed or parsing fails, return empty string.
    """
    try:
        if not BS_AVAILABLE:
            return ""
        r = requests.get(url, timeout=6, headers={"User-Agent": "Mozilla/5.0"})
        if r.status_code != 200:
            return ""
        soup = BeautifulSoup(r.text, "html.parser")

        # Try <article> first, fall back to generic selectors
        article = soup.find("article")
        if not article:
            # many news sites wrap main content in divs with common classes
            candidate = soup.find("div", class_=lambda c: c and ("content" in c or "article" in c or "post" in c))
            article = candidate if candidate else soup.body

        # remove scripts/styles/nav/footer
        for t in article.find_all(["script", "style", "nav", "footer", "aside"]):
            t.decompose()

        text = article.get_text(separator="\n", strip=True)
        # Keep a limited length to avoid huge JSON caches
        return text[:20000]
    except Exception:
        return ""


# ==========================================================
# CYBER NEWS (online fetch + offline cache + viewer)
# ==========================================================
def fetch_cyber_news():
    """
    Fetch cybersecurity news using NewsData.io API.
    Falls back to offline cache if internet/API fails.
    Stores full article content for offline reading.
    """

    API_KEY = "pub_dc29232fd7fc460f9fa0a3d9e1d17c1a"
    URL = f"https://newsdata.io/api/1/news?apikey={API_KEY}&q=cybersecurity&language=en"

    try:
        r = requests.get(URL, timeout=6)
        if r.status_code != 200:
            raise Exception("NewsAPI error")

        data = r.json()
        results = data.get("results", [])

        news = []
        for item in results[:15]:
            title = item.get("title", "Untitled")
            link = item.get("link", "#")
            summary = item.get("description", "") or ""
            date = item.get("pubDate", "")

            # stable unique ID
            nid = str(abs(hash(link or title)))

            # attempt to fetch full article text (best-effort)
            full_text = fetch_article_text(link)
            if not full_text:
                full_text = summary

            news.append({
                "id": nid,
                "title": title,
                "summary": summary[:400],
                "content": full_text,
                "link": link or "#",
                "date": date,
            })

        # Cache and return
        if news:
            save_cache(CACHE_NEWS, news)
            return news

        raise Exception("Empty API response")

    except Exception:
        # fallback to offline cache
        cached = load_cache(CACHE_NEWS)
        if cached:
            return cached

        # ultimate fallback
        return [{
            "id": "offline-1",
            "title": "Offline: Cybersecurity news unavailable",
            "summary": "No internet. Showing offline cached content.",
            "content": "Connect to the internet and press refresh to load latest stories.",
            "link": "#",
            "date": "Cached",
        }]




@login_required
def view_news(request, item_id):
    """
    Render full news content from cache (works offline).
    """
    news_items = load_cache(CACHE_NEWS)
    for it in news_items:
        if str(it.get("id")) == str(item_id):
            return render(request, "dashboard/news_view.html", {"item": it})
    raise Http404("News item not found")


@login_required
def refresh_news(request):
    """
    Trigger a refresh (tries online, falls back to cache). Returns JSON success and count.
    """
    items = fetch_cyber_news()
    return JsonResponse({"status": "ok", "count": len(items)})


# ==========================================================
# CYBER JOBS (RSS + LinkedIn fallback + cache + viewer)
# ==========================================================
def fetch_cyber_jobs():
    """
    Fetch job postings from an RSS (preferred). If empty, try a naive LinkedIn HTML parse fallback.
    Save cache so jobs are available offline. Returns a list of job dicts.
    """
    try:
        # Prefer a job RSS that is reasonably stable. Replace with a feed you trust if you have one.
        FEED_URL = "https://www.cybersecurity-help.cz/rss/jobs/"  # example feed; change if you have a better one
        feed = feedparser.parse(FEED_URL)

        jobs = []
        if getattr(feed, "entries", None):
            for entry in feed.entries[:20]:
                link = entry.get("link", "") or ""
                jid = str(abs(hash(link or entry.get("title", ""))))
                jobs.append({
                    "id": jid,
                    "title": entry.get("title", "Cyber Job"),
                    "company": entry.get("author", "") or entry.get("company", "") or "Unknown",
                    "location": "",
                    "description": entry.get("summary", "")[:2000],
                    "link": link or "#",
                    "date": entry.get("published", ""),
                })

        # ---------------------------
        # LinkedIn fallback (fixed parser)
        # ---------------------------
        if not jobs:
            try:
                url = "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?keywords=cyber%20security"
                r = requests.get(url, timeout=6, headers={"User-Agent": "Mozilla/5.0"})
                if r.status_code == 200 and r.text:
                    # LinkedIn HTML is fragile; try to get titles and also attempt to find job links if present.
                    chunks = r.text.split('<h3 class="base-search-card__title">')
                    for segment in chunks[1:20]:
                        try:
                            title = segment.split("</h3>")[0].strip()
                        except Exception:
                            title = "Cybersecurity Job"
                        jid = str(abs(hash(title)))
                        # Attempt to extract a direct job link if present nearby
                        link = "#"
                        # try to find data-job-id or view link in the chunk
                        if 'href="' in segment:
                            # a naive attempt: find the first href after this title chunk
                            try:
                                href_part = segment.split('href="', 1)[1].split('"', 1)[0]
                                if href_part.startswith("/"):
                                    link = "https://www.linkedin.com" + href_part
                                elif href_part.startswith("http"):
                                    link = href_part
                            except Exception:
                                link = "#"
                        jobs.append({
                            "id": jid,
                            "title": title,
                            "company": "LinkedIn",
                            "location": "",
                            "description": "LinkedIn job (parsed).",
                            "link": link or "#",
                            "date": datetime.utcnow().isoformat(),
                        })
            except Exception:
                pass

        if jobs:
            save_cache(CACHE_JOBS, jobs)
            return jobs

        raise Exception("No jobs parsed")

    except Exception:
        cached = load_cache(CACHE_JOBS)
        if cached:
            return cached

        # fallback jobs
        return [
            {
                "id": "job-offline-1",
                "title": "Offline: SOC Analyst",
                "company": "Offline Corp",
                "location": "Remote",
                "description": "This is an offline placeholder job. When online, the dashboard will fetch fresh listings.",
                "link": "#",
                "date": "Cached",
            }
        ]


@login_required
def view_job(request, item_id):
    """
    Show full job description from the cache (works offline).
    """
    jobs = load_cache(CACHE_JOBS)
    for j in jobs:
        if str(j.get("id")) == str(item_id):
            return render(request, "dashboard/job_view.html", {"job": j})
    raise Http404("Job not found")


@login_required
def refresh_jobs(request):
    """
    Trigger a jobs refresh; returns json with updated count.
    """
    jobs = fetch_cyber_jobs()
    return JsonResponse({"status": "ok", "count": len(jobs)})


# ==========================================================
# AUTH & HOME
# ==========================================================
def home(request):
    return render(request, "home.html")


def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Account created successfully!")
            return redirect("login")
        messages.error(request, "Fix the errors below.")
    else:
        form = RegisterForm()

    return render(request, "auth/register.html", {"form": form})


def user_login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect("dashboard")
        messages.error(request, "Invalid username or password.")
    return render(request, "auth/login.html")


@never_cache
@login_required
def user_logout(request):
    logout(request)
    request.session.flush()
    messages.success(request, "Logged out.")
    return redirect("home")


# ==========================================================
# DASHBOARD (main)
# ==========================================================
@login_required
def dashboard(request):
    user = request.user
    today = timezone.now().date()

    # Today's XP
    today_progress = UserProgress.objects.filter(user=user, date=today).first()
    today_xp = today_progress.xp_gained if today_progress else 0

    # Recent activity (last 10 logs)
    recent = UserProgress.objects.filter(user=user).order_by("-date")[:10]

    # Heatmap - last 30 days
    heatmap = []
    for i in range(30):
        d = today - timezone.timedelta(days=i)
        log = UserProgress.objects.filter(user=user, date=d).first()
        heatmap.append(log.xp_gained if log else 0)
    heatmap.reverse()

    # Level progress
    xp_for_prev = (user.level - 1) * 100
    xp_into = user.xp - xp_for_prev
    progress_percent = max(0, min(100, int((xp_into / 100) * 100)))

    # Last 7 days and streak trend
    last7 = []
    streak_trend = []
    weekday_labels = []
    for i in range(6, -1, -1):
        d = today - timezone.timedelta(days=i)
        log = UserProgress.objects.filter(user=user, date=d).first()
        last7.append(log.xp_gained if log else 0)
        streak_trend.append(log.streak if log else 0)
        weekday_labels.append(d.strftime("%a"))

    # Other objects
    courses = Course.objects.all()
    enrollments = {p.course.id: p for p in UserCourseProgress.objects.filter(user=user)}
    badges = UserBadge.objects.filter(user=user).select_related("badge")
    certificates = Certificate.objects.filter(user=user)
    games = Game.objects.all()
    game_progress = {gp.game.id: gp for gp in GameProgress.objects.filter(user=user)}
    challenges = Challenge.objects.all().order_by("-created_at")[:6]
    solved_ids = ChallengeAttempt.objects.filter(user=user, solved=True).values_list("challenge_id", flat=True)

    # Feeds (offline-ready)
    news = fetch_cyber_news()
    jobs = fetch_cyber_jobs()

    return render(request, "dashboard/dashboard.html", {
        "user": user,
        "today_xp": today_xp,
        "recent": recent,
        "heatmap": heatmap,
        "progress_percent": progress_percent,
        "last7_days": last7,
        "streak_trend": streak_trend,
        "weekday_labels": weekday_labels,
        "courses": courses,
        "enrollments": enrollments,
        "badges": badges,
        "certificates": certificates,
        "games": games,
        "game_progress": game_progress,
        "challenges": challenges,
        "solved_ids": solved_ids,
        "news": news,
        "jobs": jobs,
    })


# ==========================================================
# QUIZ API
# ==========================================================
@never_cache
@login_required
def quiz_view(request):
    return render(request, "quiz.html")


@require_http_methods(["GET"])
def quiz_api(request):
    qs = list(Question.objects.all())
    random.shuffle(qs)
    selected = qs[:10]
    return JsonResponse([{
        "id": q.id,
        "text": q.text,
        "option_a": q.option_a,
        "option_b": q.option_b,
        "option_c": q.option_c,
        "option_d": q.option_d,
        "xp_reward": q.xp_reward,
    } for q in selected], safe=False)


@csrf_exempt
@login_required
@require_http_methods(["POST"])
def quiz_complete(request):
    try:
        data = json.loads(request.body)
        xp = int(data.get("xp", 0))
        user = request.user
        user.log_xp(xp)
        for b in Badge.objects.filter(xp_required__lte=user.xp):
            UserBadge.objects.get_or_create(user=user, badge=b)
        return JsonResponse({"status": "ok", "xp": user.xp})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


# ==========================================================
# LEADERBOARD
# ==========================================================
@never_cache
@login_required
def leaderboard(request):
    top = CustomUser.objects.order_by("-cyber_score")[:20]
    return render(request, "leaderboard.html", {"top_users": top})


# ==========================================================
# PROFILE
# ==========================================================
@never_cache
@login_required
def profile(request, username):
    profile_user = get_object_or_404(CustomUser, username=username)
    is_owner = (request.user == profile_user)

    # Profile update
    if request.method == "POST" and is_owner:
        form = ProfileForm(request.POST, request.FILES, instance=profile_user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated.")
            return redirect("profile", username=username)
    else:
        form = ProfileForm(instance=profile_user)

    # XP graph
    today = timezone.now().date()
    labels, values = [], []

    for i in range(30):
        d = today - timezone.timedelta(days=i)
        labels.append(d.strftime("%Y-%m-%d"))
        log = UserProgress.objects.filter(user=profile_user, date=d).first()
        values.append(log.xp_gained if log else 0)

    labels.reverse()
    values.reverse()

    # Badges
    all_badges = Badge.objects.all()
    unlocked_badges = UserBadge.objects.filter(user=profile_user).values_list("badge_id", flat=True)

    # Other data
    certificates = Certificate.objects.filter(
    user=profile_user,
    related_course__isnull=False
)

    courses = UserCourseProgress.objects.filter(user=profile_user)
    completed_challenges = ChallengeAttempt.objects.filter(user=profile_user, solved=True)

    return render(request, "dashboard/profile.html", {
        "profile_user": profile_user,
        "form": form,
        "is_owner": is_owner,
        "labels": labels,
        "values": values,

        # BADGES NEW:
        "all_badges": all_badges,
        "unlocked_badges": unlocked_badges,
        "new_badge": request.session.pop("new_badge", None),

        "certificates": certificates,
        "courses": courses,
        "completed_challenges": completed_challenges,
    })

# ==========================================================
# REMOVE AVATAR / COVER
# ==========================================================
@login_required
def remove_avatar(request):
    user = request.user
    if getattr(user, "avatar", None):
        try:
            user.avatar.delete(save=False)
        except Exception:
            pass
        user.avatar = None
        user.save()
    messages.success(request, "Avatar removed.")
    return redirect("profile", username=user.username)


@login_required
def remove_cover(request):
    user = request.user
    if getattr(user, "cover_photo", None):
        try:
            user.cover_photo.delete(save=False)
        except Exception:
            pass
        user.cover_photo = None
        user.save()
    messages.success(request, "Cover removed.")
    return redirect("profile", username=user.username)


# ==========================================================
# CHALLENGES
# ==========================================================
@never_cache
@login_required
def challenge_list(request):
    challenges = Challenge.objects.all().order_by("-created_at")
    solved_ids = ChallengeAttempt.objects.filter(user=request.user, solved=True).values_list("challenge_id", flat=True)
    return render(request, "dashboard/challenges.html", {"challenges": challenges, "solved_ids": solved_ids})

def normalize_flag(flag: str) -> str:
    """
    Normalize flags so:
    - FLAG{test}
    - flag{test}
    - test
    all become: test
    """
    return (
        flag.lower()
        .replace("flag{", "")
        .replace("}", "")
        .strip()
    )


@csrf_protect
@never_cache
@login_required
def challenge_detail(request, slug):
    challenge = get_object_or_404(Challenge, slug=slug)

    attempt, _ = ChallengeAttempt.objects.get_or_create(
        user=request.user,
        challenge=challenge
    )

    # ================= START CHALLENGE =================
    if request.method == "POST" and "start_challenge" in request.POST:
        if not attempt.started_at and not attempt.solved:
            attempt.started_at = timezone.now()
            attempt.save()
        return redirect("challenge_detail", slug=slug)

    # ================= FLAG SUBMISSION =================
    if request.method == "POST" and "flag" in request.POST:
        if not attempt.started_at or attempt.solved:
            return redirect("challenge_detail", slug=slug)

        submitted_flag = request.POST.get("flag", "")
        attempt.attempts += 1

        if normalize_flag(submitted_flag) == normalize_flag(challenge.flag):
            attempt.solved = True
            attempt.solved_at = timezone.now()
            attempt.time_spent = attempt.solved_at - attempt.started_at
            attempt.save()

            request.user.log_xp(challenge.xp_reward)
            messages.success(request, f"Correct flag! +{challenge.xp_reward} XP")
            return redirect("challenge_detail", slug=slug)

        attempt.save()
        messages.error(request, "Incorrect flag. Try again.")

    # ================= LOAD ARTIFACT FILES =================
    artifacts = []
    artifacts_dir = os.path.join(
        settings.MEDIA_ROOT,
        "challenges",
        challenge.slug
    )

    if os.path.isdir(artifacts_dir):
        artifacts = sorted([
            f for f in os.listdir(artifacts_dir)
            if os.path.isfile(os.path.join(artifacts_dir, f))
        ])

    return render(
        request,
        "dashboard/challenge_detail.html",
        {
            "challenge": challenge,
            "attempt": attempt,
            "artifacts": artifacts,  # ✅ THIS FIXES EVERYTHING
        },
    )


@never_cache
@login_required
def challenge_history(request):
    attempts = ChallengeAttempt.objects.filter(user=request.user).select_related("challenge").order_by("-solved_at", "-started_at")
    return render(request, "dashboard/challenge_history.html", {
        "attempts": attempts,
    })


@login_required
def view_challenge_file(request, slug, filename):
    base_path = os.path.join(settings.MEDIA_ROOT, "challenges", slug)

    # 🔐 Normalize paths (CRITICAL)
    base_path = os.path.normpath(base_path)
    file_path = os.path.normpath(os.path.join(base_path, filename))

    # 🔒 Prevent path traversal
    if not file_path.startswith(base_path):
        raise Http404("Invalid file path")

    if not os.path.exists(file_path) or not os.path.isfile(file_path):
        raise Http404("File not found")

    return FileResponse(
        open(file_path, "rb"),
        content_type="text/plain; charset=utf-8"
    )


# ==========================================================
# COURSES + LESSONS
# ==========================================================
@never_cache
@login_required
def course_list(request):
    courses = Course.objects.all()

    progress_map = {
        p.course_id: p
        for p in UserCourseProgress.objects.filter(user=request.user)
    }

    # attach progress directly to course objects
    for course in courses:
        course.user_progress = progress_map.get(course.id)

    return render(request, "courses/course_list.html", {
        "courses": courses
    })


@never_cache
@login_required
def course_detail(request, slug):
    course = get_object_or_404(Course, slug=slug)

    progress = UserCourseProgress.objects.filter(
        user=request.user,
        course=course
    ).first()

    lessons = course.lessons.all().order_by("order")

    # ✅ FIX: ALWAYS DEFINE certificates
    certificates = Certificate.objects.filter(
        user=request.user,
        related_course=course
    )

    if request.method == "POST":

        # ENROLL
        if "enroll" in request.POST:
            progress, created = UserCourseProgress.objects.get_or_create(
                user=request.user,
                course=course
            )

            if created:
                first_lesson = lessons.first()
                progress.current_lesson = first_lesson
                progress.save()

            return redirect(
                "lesson_view",
                course_slug=course.slug,
                lesson_id=progress.current_lesson.id
            )

        # UNENROLL / RESET
        if "unenroll" in request.POST and progress:

            # delete certificates + files
            for cert in certificates:
                if cert.file:
                    cert.file.delete(save=False)
                cert.delete()

            # delete quiz attempts
            CourseQuizAttempt.objects.filter(
                user=request.user,
                course=course
            ).delete()

            # delete progress
            progress.completed_lessons.clear()
            progress.delete()

            messages.success(
                request,
                "Course reset successfully."
            )

            return redirect("course_list")

    return render(request, "courses/course_detail.html", {
        "course": course,
        "lessons": lessons,
        "progress": progress,
        "certificates": certificates,  # ✅ always exists
    })

   



@never_cache
@login_required
def lesson_view(request, course_slug, lesson_id):
    course = get_object_or_404(Course, slug=course_slug)
    lesson = get_object_or_404(Lesson, id=lesson_id, course=course)

    progress = get_object_or_404(
        UserCourseProgress, user=request.user, course=course
    )

    # 🚫 Block skipping lessons
    if progress.current_lesson and lesson.id != progress.current_lesson.id:
        messages.warning(request, "Please follow the lesson order.")
        return redirect(
            "lesson_view",
            course_slug=course.slug,
            lesson_id=progress.current_lesson.id
        )

    lessons = list(course.lessons.all())
    index = lessons.index(lesson)

    prev_lesson = lessons[index - 1] if index > 0 else None
    next_lesson = lessons[index + 1] if index + 1 < len(lessons) else None
    is_last = next_lesson is None

    if request.method == "POST":
        # MARK COMPLETE
        if lesson not in progress.completed_lessons.all():
            progress.completed_lessons.add(lesson)
            request.user.log_xp(10)

        if next_lesson:
            progress.current_lesson = next_lesson
            progress.save()
            return redirect(
                "lesson_view",
                course_slug=course.slug,
                lesson_id=next_lesson.id
            )
        else:
            # FINAL LESSON → QUIZ
            progress.completed = True
            progress.save()
            return redirect("course_quiz", course_slug=course.slug)

    return render(request, "courses/lesson_detail.html", {
        "course": course,
        "lesson": lesson,
        "prev_lesson": prev_lesson,
        "is_last": is_last,
    })

from django.views.decorators.cache import never_cache
from django.contrib.auth.decorators import login_required


@never_cache
@login_required
def course_quiz(request, course_slug):
    course = get_object_or_404(Course, slug=course_slug)

    progress = get_object_or_404(
        UserCourseProgress,
        user=request.user,
        course=course
    )

    # 🔒 Ensure all lessons are completed
    if not progress.completed:
        messages.error(request, "Complete all lessons before taking the quiz.")
        return redirect("course_detail", slug=course.slug)

    # 🔢 Count attempts
    attempts_done = CourseQuizAttempt.objects.filter(
        user=request.user,
        course=course
    ).count()

    # 🚫 Max attempts reached
    if attempts_done >= 5:
        messages.error(
            request,
            "Maximum quiz attempts reached. Please unenroll and re-enroll to try again."
        )
        return redirect("course_detail", slug=course.slug)

    # 📋 Load questions
    questions = list(course.quiz_questions.all())
    if len(questions) < 10:
        messages.error(request, "Quiz is not properly configured.")
        return redirect("course_detail", slug=course.slug)

    random.shuffle(questions)
    questions = questions[:10]

    # =========================
    # SUBMIT QUIZ
    # =========================
    if request.method == "POST":
        score = 0

        for q in questions:
            selected = request.POST.get(f"q_{q.id}")
            correct = q.options.filter(is_correct=True).first()
            if correct and selected == str(correct.id):
                score += 1

        passed = score >= 7

        # 🧪 SAVE ATTEMPT
        CourseQuizAttempt.objects.create(
            user=request.user,
            course=course,
            score=score,
            attempt_no=attempts_done + 1,
            passed=passed
        )

        # =========================
        # ✅ PASSED
        # =========================
        if passed:
            certificate, created = Certificate.objects.get_or_create(
                user=request.user,
                related_course=course,
                defaults={
                    "title": f"{course.title} Completion Certificate",
                    "recipient_name": (
                        request.user.full_name or request.user.username
                    ),
                }
            )

            # 🧾 Generate PDF if missing
            if not certificate.file:
                generate_certificate_pdf(certificate)

            messages.success(
                request,
                "🎉 Congratulations! You passed the quiz and earned a certificate."
            )

            return redirect(
                "course_quiz_result",
                course_slug=course.slug
            )

        # =========================
        # ❌ FAILED
        # =========================
        messages.error(
            request,
            f"Quiz failed ({score}/10). Attempts left: {5 - (attempts_done + 1)}"
        )
        return redirect("course_quiz", course_slug=course.slug)

    # =========================
    # SHOW QUIZ PAGE
    # =========================
    return render(request, "courses/course_quiz.html", {
        "course": course,
        "questions": questions,
        "attempts_left": 5 - attempts_done,
    })


@never_cache
@login_required
def course_quiz_result(request, course_slug):
    course = get_object_or_404(Course, slug=course_slug)

    # 🔎 Get latest attempt
    attempt = CourseQuizAttempt.objects.filter(
        user=request.user,
        course=course
    ).order_by("-attempt_no").first()

    # 🚫 Safety check
    if not attempt:
        messages.error(request, "No quiz attempt found.")
        return redirect("course_detail", slug=course.slug)

    # 📊 Calculate percentage
    percentage = int((attempt.score / 10) * 100)

    # 🎓 Fetch certificate ONLY if passed
    certificate = None
    if attempt.passed:
        certificate = Certificate.objects.filter(
            user=request.user,
            related_course=course
        ).first()

    return render(request, "courses/quiz_result.html", {
        "course": course,
        "attempt": attempt,
        "percentage": percentage,
        "certificate": certificate,  # 👈 IMPORTANT
    })

    

# ==========================================================
# GAMES
# ==========================================================
@never_cache
@login_required
def game_list(request):
    games = Game.objects.all()
    progress = {p.game.id: p for p in GameProgress.objects.filter(user=request.user)}

    return render(request, "games/game_list.html", {
        "games": games,
        "progress": progress,
    })


@never_cache
@login_required
def game_play(request, slug):
    game = get_object_or_404(Game, slug=slug)
    progress, _ = GameProgress.objects.get_or_create(user=request.user, game=game)

    if request.method == "POST":
        score = int(request.POST.get("score", 0))
        progress.record_play(score)

        request.user.log_xp(game.xp_reward)
        messages.success(request, f"Game complete! +{game.xp_reward} XP")

        return redirect("game_list")

    template = f"games/{slug}.html"
    return render(request, template, {"game": game, "progress": progress})


# ==========================================================
# NEW API ENDPOINTS (for AJAX refresh)
# ==========================================================
@login_required
def api_news_items(request):
    data = fetch_cyber_news()
    return JsonResponse(data, safe=False)

@login_required
def api_job_items(request):
    """
    Returns JSON list of job items (cached or freshly fetched)
    Endpoint: /api/jobs/items/  (add to urls.py)
    """
    data = fetch_cyber_jobs()
    return JsonResponse(data, safe=False)



@never_cache
@login_required
def certificate_view(request, certificate_id):
    certificate = get_object_or_404(
        Certificate,
        id=certificate_id,
        user=request.user
    )

    return render(request, "courses/certificate_view.html", {
        "certificate": certificate
    })


@never_cache
@login_required
def certificate_download(request, cert_id):
    cert = get_object_or_404(
        Certificate,
        id=cert_id,
        user=request.user
    )

    # ✅ Auto-generate PDF if missing
    if not cert.file:
        generate_certificate_pdf(cert)

    # ❌ Still missing → stop
    if not cert.file:
        messages.error(
            request,
            "Certificate file is not ready yet. Please try again."
        )
        return redirect("profile", username=request.user.username)

    # ✅ Safe filename
    filename = f"{slugify(cert.title)}.pdf"

    return FileResponse(
        cert.file.open("rb"),
        as_attachment=True,
        filename=filename,
        content_type="application/pdf"
    )



@never_cache
@login_required
def certificate_preview(request, cert_id):
    certificate = get_object_or_404(
        Certificate,
        id=cert_id,
        user=request.user
    )

    if not certificate.file:
        raise Http404("Certificate not generated")

    response = FileResponse(
        certificate.file.open("rb"),
        content_type="application/pdf"
    )
    response["Content-Disposition"] = "inline"
    return response




def certificate_public_view(request, certificate_id):
    certificate = get_object_or_404(
        Certificate,
        certificate_id=certificate_id,
        public=True
    )
    return render(
        request,
        "certificates/certificate_public.html",
        {"certificate": certificate}
    )





# ============================
#   HACKING LAB SYSTEM (Docker)
# ============================

# ==========================================================
# DOCKER LAB INTEGRATION
# ==========================================================
from .docker_utils import (
    start_kali,
    start_ubuntu,
    stop_lab as docker_stop_lab,
    get_ip,
    exec_cmd
)

# ==========================================================
# LAB LIST
# ==========================================================
@login_required
def lab_list(request):
    labs = HackingLab.objects.all().order_by("difficulty")
    progress_map = {
        p.lab_id: p
        for p in UserLabProgress.objects.filter(user=request.user)
    }

    return render(request, "labs/lab_list.html", {
        "labs": labs,
        "progress": progress_map
    })


# ==========================================================
# LAB DETAIL
# ==========================================================
@login_required
def lab_detail(request, slug):
    lab = get_object_or_404(HackingLab, slug=slug)
    progress = UserLabProgress.objects.filter(
        user=request.user, lab=lab
    ).first()

    kali_ip = ubuntu_ip = None
    if progress and progress.kali_container_id:
        try:
            kali_ip = get_ip(progress.kali_container_id)
            ubuntu_ip = get_ip(progress.ubuntu_container_id)
        except Exception:
            pass

    return render(request, "labs/lab_detail.html", {
        "lab": lab,
        "progress": progress,
        "kali_ip": kali_ip,
        "ubuntu_ip": ubuntu_ip,
        "auto_refresh": bool(progress and progress.kali_container_id),
    })


# ==========================================================
# START LAB
# ==========================================================
@login_required
def start_lab(request, slug):
    lab = get_object_or_404(HackingLab, slug=slug)

    progress, _ = UserLabProgress.objects.get_or_create(
        user=request.user,
        lab=lab
    )

    if progress.kali_container_id:
        messages.info(request, "Lab is already running.")
        return redirect("lab_detail", slug=slug)

    try:
        kali_id = start_kali(request.user.username, lab.slug)
        ubuntu_id = start_ubuntu(request.user.username, lab.slug)

        progress.kali_container_id = kali_id
        progress.ubuntu_container_id = ubuntu_id
        progress.started_at = timezone.now()
        progress.save()

        messages.success(request, "Lab started successfully 🚀")

    except Exception as e:
        messages.error(request, f"Failed to start lab: {e}")

    return redirect("lab_detail", slug=slug)


# ==========================================================
# STOP LAB
# ==========================================================
@login_required
def stop_lab(request, slug):
    lab = get_object_or_404(HackingLab, slug=slug)
    progress = get_object_or_404(
        UserLabProgress,
        user=request.user,
        lab=lab
    )

    try:
        docker_stop_lab(request.user.username, lab.slug)

        progress.kali_container_id = ""
        progress.ubuntu_container_id = ""
        progress.save()

        messages.success(request, "Lab stopped and cleaned 🧹")

    except Exception as e:
        messages.error(request, f"Error stopping lab: {e}")

    return redirect("lab_detail", slug=slug)


# ==========================================================
# WEB SHELL (KALI)
# ==========================================================
@csrf_exempt
@login_required
def web_shell(request, slug):
    lab = get_object_or_404(HackingLab, slug=slug)
    progress = UserLabProgress.objects.filter(
        user=request.user,
        lab=lab
    ).first()

    if not progress or not progress.kali_container_id:
        return JsonResponse({"output": "Lab not running"})

    data = json.loads(request.body)
    command = data.get("command", "")

    output = exec_cmd(progress.kali_container_id, command)
    return JsonResponse({"output": output})


# ==========================================================
# COMPLETE LAB
# ==========================================================
@login_required
def complete_lab(request, slug):
    lab = get_object_or_404(HackingLab, slug=slug)
    progress = get_object_or_404(
        UserLabProgress,
        user=request.user,
        lab=lab
    )

    if progress.completed:
        messages.info(request, "Lab already completed.")
        return redirect("lab_detail", slug=slug)

    progress.completed = True
    progress.completed_at = timezone.now()
    progress.save()

    request.user.log_xp(lab.xp_reward)

    if lab.badge_reward:
        UserBadge.objects.get_or_create(
            user=request.user,
            badge=lab.badge_reward
        )

    messages.success(
        request,
        f"Lab completed! +{lab.xp_reward} XP 🏆"
    )

    return redirect("profile", username=request.user.username)

OLLAMA_URL = "http://127.0.0.1:11434/api/generate"

@csrf_exempt
@login_required
def lab_ai_guide(request):
    if request.method != "POST":
        return JsonResponse({"reply": "Invalid request method."}, status=400)

    # -----------------------------
    # GET USER MESSAGE
    # -----------------------------
    try:
        body = json.loads(request.body.decode("utf-8"))
        user_message = body.get("message", "").strip()
    except Exception:
        return JsonResponse({"reply": "Invalid JSON request."}, status=400)

    if not user_message:
        return JsonResponse({"reply": "Ask something 👇"})

    # -----------------------------
    # OLLAMA PAYLOAD (OPTIMIZED)
    # -----------------------------
    payload = {
        "model": "dolphin-phi",
        "prompt": f"{LAB_AI_SYSTEM_PROMPT}\nUser: {user_message}\nAssistant (max 3 lines):",
        "stream": False,
        "options": {
            "temperature": 0.3,
            "num_predict": 80,        # ⚡ faster
            "top_p": 0.9,
            "repeat_penalty": 1.05,
            "num_ctx": 512,           # ⚡ faster context
            "stop": ["\n\n"]          # ⚡ early stop
        }
    }

    # -----------------------------
    # CALL OLLAMA
    # -----------------------------
    try:
        response = requests.post(
            OLLAMA_URL,
            json=payload,
            timeout=40   # ⚡ faster timeout
        )

        if response.status_code != 200:
            return JsonResponse({"reply": "AI engine error."})

        data = response.json()
        raw_reply = data.get("response", "").strip()

        # -----------------------------
        # CLEAN RESPONSE (buddy style)
        # -----------------------------
        if not raw_reply:
            return JsonResponse({"reply": "Buddy, nothing came 😅 try again"})

        # remove unwanted AI phrases
        bad_starts = ["I understand", "As an AI", "Sure", "Here"]
        for b in bad_starts:
            if raw_reply.startswith(b):
                raw_reply = raw_reply.replace(b, "").strip()

        # keep only first 3 lines
        lines = raw_reply.split("\n")
        reply = "\n".join(lines[:3]).strip()

        if not reply:
            reply = "Buddy, try again 👀"

        return JsonResponse({"reply": reply})

    # -----------------------------
    # ERROR HANDLING
    # -----------------------------
    except requests.exceptions.ConnectionError:
        return JsonResponse({
            "reply": "Ollama not running ⚠️"
        })

    except Exception as e:
        return JsonResponse({
            "reply": f"AI error: {str(e)}"
        })

@never_cache
@login_required
def delete_account(request):
    if request.method == "POST":
        password = request.POST.get("password")

        if not password:
            messages.error(request, "Password is required.")
            return redirect("delete_account")

        # 🔐 Verify password
        if not check_password(password, request.user.password):
            messages.error(request, "Incorrect password.")
            return redirect("delete_account")

        # ✅ Password correct → delete account permanently
        user = request.user
        logout(request)
        user.delete()

        messages.success(
            request,
            "Your account has been permanently deleted."
        )
        return redirect("home")

    return render(request, "auth/delete_account.html")
