from django.urls import path
from .views import SolutionUpload

from . import views
from .views import ai_assistant

# from .views import quiz_feedback  # This line should be removed because you're no longer using quiz_feedback

urlpatterns = [
    # Remove the URL pattern that includes quiz_feedback

    path('', views.HomePageView.as_view(), name='home'),
    path('login/', views.LoginPageView.as_view(), name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.RegisterPageView.as_view(), name='register'),
    path('dashboard/', views.DashboardPageView.as_view(), name='dashboard'),
    path('dashboard/courses', views.CoursesPageView.as_view(), name='courses'),
    path('dashboard/notifications', views.NotificationsPageView.as_view(), name='notifications'),
    path('dashboard/videos', views.VideosPageView.as_view(), name='videos'),
    path('dashboard/homeworks', views.HomeworksPageView.as_view(), name='homeworks'),
    path('dashboard/solution-upload/', views.SolutionUpload.as_view(), name='solution'),
    path('dashboard/notes', views.NotesPageView.as_view(), name='notes'),
    path('solution-upload/', views.SolutionUpload.as_view(), name='solution_upload'),
    path('quizzes/generate/<int:note_id>/', views.generate_quiz_view, name='generate_quiz'),
     path('aiassistant/', ai_assistant, name='ai_assistant'),
]
