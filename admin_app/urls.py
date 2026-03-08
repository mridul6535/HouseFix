from django.urls import path
from admin_app import views

urlpatterns = [
    path('', views.admin_login_page, name='admin_login_page'),
    path('admin_login/', views.admin_login, name='admin_login'),
    path('admin_logout/', views.admin_logout, name='admin_logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('show_contact/', views.show_contact, name='show_contact'),
    path('add_category/', views.add_category, name='add_category'),
    path('save_category/', views.save_category, name='save_category'),
    path('edit_page/<int:cat_id>/', views.edit_page, name='edit_page'),
    path('update_category/<int:cat_id>/', views.update_category, name='update_category'),
    path('delete_category/<int:cat_id>/', views.del_category, name='delete_category'),
    path('show_category/', views.show_category, name='show_category'),
    path('all_users/', views.all_users, name='all_users'),
    path('block_user/<int:user_id>/', views.block_user, name='block_user'),
    # end category
    # worker approval
    path('worker_request/', views.worker_card, name='worker_card'),
    path('worker_verification/<int:emp_id>/', views.worker_verification, name='worker_verification'),
    # to send as alink
    # path('save_worker_password/<int:emp_id>/', views.save_worker_password, name='save_worker_password'),#used to save password(w)
    path('revoke_worker/<int:emp_id>/', views.revoke_worker, name='revoke_worker'),
    path('change_role_approve/<int:emp_id>/', views.change_role_approve, name='change_role_approve'),
    path('change_role_reject/<int:emp_id>/', views.change_role_reject, name='change_role_reject'),
    # end worker
    path("worker_table/", views.worker_table, name="worker_table"),
    # maintenance request
    path('request_card/', views.request_card, name='request_card'),
    path('in_progress/', views.in_progress_req, name='in_progress'),
    path('completed_request/', views.completed_request, name='completed_request'),
    path('send_work_request/<int:req_id>/', views.send_work_request, name='send_work_request'),
    path('assigning_table/<int:req_id>/', views.assigning_table, name='assigning_table'),
    path('reject_request/<int:req_id>/', views.reject_request, name='reject_request'),
    # subscription
    path('add_subscription/', views.add_subscription, name='add_subscription'),
    path('show_subscription/', views.show_subscription, name='show_subscription'),
    path('save_subscription/', views.save_subscription, name='save_subscription'),
    path('edit_subscription/<int:plan_id>/', views.edit_subscription, name='edit_subscription'),
    path('update_subscription/<int:plan_id>/', views.update_subscription, name='update_subscription'),
    path('delete_subscription/<int:plan_id>/', views.delete_subscription, name='delete_subscription'),
    path('subscribers/', views.subscribers, name='subscribers'),
]