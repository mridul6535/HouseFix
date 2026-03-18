from django.urls import path
from web_app import views

urlpatterns = [
    path('home/', views.home_page, name='home'),
    path('about/', views.about_page, name='about'),
    path('contact/', views.contact_page, name='contact'),
    path('save_contact/', views.save_contact, name='save_contact'),
    path('service/', views.service_page, name='service'),
    path('register/', views.reg_page, name='register'),
    path('login/', views.log_page, name='login'),
    path('reg_user/', views.reg_user, name='reg_user'),
    path('user_login/', views.user_login, name='user_login'),
    path('user_logout/', views.user_logout, name='user_logout'),
    path('add_worker/', views.add_worker, name='add_worker'),
    path('worker_request/', views.worker_request, name='worker_request'),
    path('worker_id/<worker>/', views.worker_id, name='worker_id'),
    # maintenance request
    path('request/', views.request_form, name='request'),
    path('manage_request/', views.manage_request, name='manage_request'),
    path('cancel_request/<int:request_id>/', views.cancel_request, name='cancel_request'),
    # payment
    path("stripe_payment/", views.stripe_payment, name="stripe_payment"),
    path("payment_success/", views.payment_success, name="payment_success"),
    path("payment_failed/", views.payment_failed, name="payment_failed"),
    # chatbot
    path("chatbot/", views.chatbot, name="chatbot"),
    # subscriptions
    path("single_plan/<int:plan_id>/", views.single_plan, name="single_plan"),
    path("stripe_subscription/", views.stripe_subscription, name="stripe_subscription"),
    # subscription payment
    path("plan_success/", views.plan_success, name="plan_success"),
    path("plan_failed/", views.plan_failed, name="plan_failed"),
]
