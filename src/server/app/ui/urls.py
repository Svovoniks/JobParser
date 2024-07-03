from django.urls import include, path

from . import views

analytics_urls = [
    path("", views.analytics, name="analytics"),
    path("vacancy_resume_ratio/", views.vacancy_resume_ratio, name="ratio analysis"),
    path("resume_averages/", views.resume_averages, name="resume averages analysis"),
    path("vacancy_averages/", views.vacancy_averages, name="vacancy average analysis"),
]

urlpatterns = [
    path("vacancies/", views.vacancies, name="vacancies"),
    path("resumes/", views.resumes, name="resumes"),
    path("tasks/", views.tasks, name="tasks"),
    path("task/<int:task_id>/", views.task, name="task"),
    path("resume_skills/<str:resume_id>/", views.resume_skills, name="resume_skills"),
    path("resume_roles/<str:resume_id>/", views.resume_roles, name="resume_roles"),
    path("vacancy_skills/<int:vacancy_id>/", views.vacancy_skills, name="vacancy_skills"),
    path("vacancy_roles/<int:vacancy_id>/", views.vacancy_roles, name="vacancy_roles"),
    path("analytics/", include(analytics_urls))
]
