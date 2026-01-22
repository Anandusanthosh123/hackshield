# hackshield/urls.py

from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from core import views
from django.contrib.auth import views as auth_views
from core.views import view_challenge_file

# API views
from core.views import (
    api_news_items,
    api_job_items,
    start_lab,
    stop_lab,
    complete_lab,
)

   
    


urlpatterns = [

    # -------------------------
    # ADMIN + AUTH
    # -------------------------
    path('admin/', admin.site.urls),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),

    # -------------------------
    # DASHBOARD + HOME
    # -------------------------
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),

    # -------------------------
    # QUIZ
    # -------------------------
    path('quiz/', views.quiz_view, name='quiz'),
    path('api/quiz/', views.quiz_api, name='quiz_api'),
    path('api/quiz/complete/', views.quiz_complete, name='quiz_complete'),

    # -------------------------
    # LEADERBOARD + PROFILE
    # -------------------------
    path('leaderboard/', views.leaderboard, name='leaderboard'),
    path('profile/@<str:username>/', views.profile, name='profile'),

    # -------------------------
    # PASSWORD RESET
    # -------------------------
    path('password-reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),

    # -------------------------
    # USER SETTINGS
    # -------------------------
    path('remove-avatar/', views.remove_avatar, name='remove_avatar'),
    path('remove-cover/', views.remove_cover, name='remove_cover'),

    # -------------------------
    # CHALLENGES
    # -------------------------
    path('challenges/', views.challenge_list, name='challenge_list'),
    path('challenges/history/', views.challenge_history, name='challenge_history'),
    path('challenges/<slug:slug>/', views.challenge_detail, name='challenge_detail'),

    # -------------------------
    # COURSES & LESSONS
    # -------------------------
    path('courses/', views.course_list, name='course_list'),
    path('courses/<slug:slug>/', views.course_detail, name='course_detail'),
  path(
    'courses/<slug:course_slug>/lessons/<int:lesson_id>/',
    views.lesson_view,
    name='lesson_view'
),
path(
    "courses/<slug:course_slug>/quiz/",
    views.course_quiz,
    name="course_quiz"
),
   
path(
    "courses/<slug:course_slug>/quiz/result/",
    views.course_quiz_result,
    name="course_quiz_result"
),

path(
    'certificate/<int:certificate_id>/',
    views.certificate_view,
    name='certificate_view'
),
path(
    "certificate/<int:cert_id>/download/",
    views.certificate_download,
    name="certificate_download"
),
path(
  "certificates/<int:cert_id>/preview/",
  views.certificate_preview,
  name="certificate_preview"
),







    # -------------------------
    # GAMES
    # -------------------------
    path('games/', views.game_list, name='game_list'),
    path('games/<slug:slug>/play/', views.game_play, name='game_play'),

    # -------------------------
    # NEWS + JOBS DETAILS
    # -------------------------
    path("news/<str:item_id>/", views.view_news, name="view_news"),
    path("jobs/<str:item_id>/", views.view_job, name="view_job"),

    # -------------------------
    # API (USED BY REFRESH BUTTON)
    # -------------------------
    path("api/news/", api_news_items, name="api_news_items"),
    path("api/jobs/", api_job_items, name="api_job_items"),
    
    


# # -------------------------
# # HACKING LAB SYSTEM
# # -------------------------
# path("labs/", views.lab_list, name="lab_list"),
# path("labs/<slug:slug>/", views.lab_detail, name="lab_detail"),

# path("labs/<slug:slug>/start/", views.start_lab, name="start_lab"),
# path("labs/<slug:slug>/stop/", views.stop_lab, name="stop_lab"),
# path("labs/<slug:slug>/complete/", views.complete_lab, name="complete_lab"),

# path("labs/<slug:slug>/shell/", views.web_shell, name="web_shell"),
# -------------------------
# HACKING LAB SYSTEM
# -------------------------

# ✅ AI LAB GUIDE (MUST BE FIRST)
path("labs/ai-guide/", views.lab_ai_guide, name="lab_ai_guide"),

# Lab list
path("labs/", views.lab_list, name="lab_list"),

# Lab actions
path("labs/<slug:slug>/start/", views.start_lab, name="start_lab"),
path("labs/<slug:slug>/stop/", views.stop_lab, name="stop_lab"),
path("labs/<slug:slug>/complete/", views.complete_lab, name="complete_lab"),
path("labs/<slug:slug>/shell/", views.web_shell, name="web_shell"),

# Lab detail (KEEP THIS LAST)
path("labs/<slug:slug>/", views.lab_detail, name="lab_detail"),




path(
    "verify/<uuid:certificate_id>/",
    views.certificate_public_view,
    name="certificate_public_view"
),
#   path(
#         "challenges/<slug:slug>/file/<str:filename>/",
#         view_challenge_file,
#         name="challenge_file_view",
#     ),

path(
    "challenges/<slug:slug>/file/<path:filename>/",
    view_challenge_file,
    name="challenge_file_view",
),

   
path(
    "delete-account/",
    views.delete_account,
    name="delete_account"
),


    
]

# Static files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
