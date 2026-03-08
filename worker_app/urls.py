from django.urls import path
from worker_app import views

urlpatterns = [
    #login/logout
    path("worker_login_page/", views.worker_login_page, name='worker_login_page'),
    path("worker_login/", views.worker_login, name='worker_login'),
    path("worker_logout/", views.worker_logout, name='worker_logout'),
    #login/logout
    path("worker_dashboard/", views.worker_dash, name='worker_dashboard'),
    path("all_jobs/", views.all_jobs, name='all_jobs'),
    path("worker_profile/<int:worker_id>/", views.worker_profile, name='worker_profile'),
    path("edit_worker/<int:worker_id>/", views.edit_worker, name='edit_worker'),
    path("update_worker/<int:worker_id>/", views.update_worker, name='update_worker'),
    path("job_request/", views.job_request, name='job_request'),
    path("accept_job/<int:req_id>/", views.accept_job, name='accept_job'),
    path("reject_job/<int:req_id>/", views.reject_job, name='reject_job'),
    # work
    # start
    path("start_work/<int:job_id>/", views.start_work, name='start_work'),
    # complete form
    path("completed_work/<int:job_id>/", views.completed_work, name='completed_work'),
    path("work_completed/<int:job_id>/", views.work_completed, name='work_completed'),
]
