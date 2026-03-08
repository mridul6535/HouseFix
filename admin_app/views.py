from django.shortcuts import render, redirect
from admin_app.models import *
from web_app.models import *
from django.core.files.storage import FileSystemStorage
from django.utils.datastructures import MultiValueDictKeyError
from django.contrib import messages
from django.core.mail import send_mail
from django.contrib.auth import authenticate, login
from django.urls import reverse
from django.contrib.auth.hashers import make_password
from worker_app.views import worker_login_page
import random
from django.conf import settings
from django.shortcuts import get_object_or_404


# Create your views here.

def admin_login_page(request):
    return render(request, 'admin_login.html')


def admin_login(request):
    print("ADMIN LOGIN VIEW HIT")

    if request.method == "POST":
        name = request.POST.get("admin_name")
        pswd = request.POST.get("password")

        user = authenticate(request, username=name, password=pswd)

        if user is not None:
            print("LOGIN SUCCESS")
            login(request, user)
            return redirect('dashboard')
        else:
            print("LOGIN FAILED")
            return redirect('admin_login_page')

    return redirect('admin_login_page')

def admin_logout(request):
    del request.session['admin_name']
    del request.session['admin_email']
    return redirect(admin_login_page)


def dashboard(request):
    if not request.session.get('admin_email'):
        return redirect(admin_login_page)
    pending_req = MaintenanceRequest.objects.filter(status="pending")
    req_count = pending_req.count()
    pay_count = MaintenanceRequest.objects.filter(payment="paid").count()
    total_pay = pay_count * 1500
    all_req = MaintenanceRequest.objects.all()
    all_req_count = all_req.count()
    all_emp = WorkerDB.objects.all().count()
    user_count = Users.objects.all().count()
    return render(request, 'dashboard.html',
                  {"req_count": req_count, 'all_req': all_req, 'all_emp': all_emp,
                   'pay_count': pay_count, 'total_pay': total_pay, 'pending_req': pending_req,
                   'all_req_count': all_req_count, 'user_count': user_count})


def show_contact(request):
    contact = ContactDB.objects.all()
    contact_count = contact.count()
    return render(request, 'show_contact.html', {"contact": contact, "contact_count": contact_count})


def all_users(request):
    users = Users.objects.all()
    return render(request, 'all_users.html', {"users": users})


def block_user(request, user_id):
    user = Users.objects.get(id=user_id)
    sub = "Notice of Account Suspension {id}".format(id=user.id)
    msg = """
    Dear {user_name},

    This is to formally inform you that your account has been temporarily suspended from accessing our Maintenance Management System.

    The action has been taken due to a violation of our platform policies or terms of service. As a result, you will not be able to submit new maintenance requests or access your account until further notice.

    If you believe this action has been taken in error or would like further clarification, you may contact the Administration Team for review.

    We remain committed to maintaining a secure and professional environment for all users.

    Sincerely,
    Administration Team
    """.format(
        user_name=user.username
    )
    send_mail(
        subject=sub,
        message=msg,
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[request.session['email']]
    )
    return redirect(all_users)


#  CRUD category (complete)
def add_category(request):
    return render(request, 'add_category.html')


def save_category(request):
    if request.method == "POST":
        cat_name = request.POST.get("category")
        cat_desc = request.POST.get("description")
        cat_photo = request.FILES.get('category_image')
        obj = CategoryDB(category_name=cat_name, category_description=cat_desc, category_photo=cat_photo)
        messages.success(request, 'category added successfully')
        obj.save()
        return redirect(add_category)


def show_category(request):
    category = CategoryDB.objects.all()
    return render(request, 'show_cat.html', {"category": category})


def edit_page(request, cat_id):
    cat = CategoryDB.objects.get(id=cat_id)
    return render(request, "edit_category.html", {"cat": cat})


def update_category(request, cat_id):
    if request.method == "POST":
        cat_name = request.POST.get("category")
        cat_desc = request.POST.get("description")
        try:
            img = request.FILES["category_image"]
            fs = FileSystemStorage()
            file = fs.save(img.name, img)
        except MultiValueDictKeyError:
            file = CategoryDB.objects.get(id=cat_id).category_photo
        messages.success(request, 'category updated successfully')
        CategoryDB.objects.filter(id=cat_id).update(category_name=cat_name, category_description=cat_desc,
                                                    category_photo=file)
        return redirect(show_category)


def del_category(request, cat_id):
    CategoryDB.objects.filter(id=cat_id).delete()
    return redirect(show_category)


# end category (CRUD)


# worker
def worker_card(request):
    worker = WorkerDB.objects.all()
    return render(request, 'worker_request.html', {"worker": worker})


# this page is for admin to send to worker as a link
def worker_verification(request, emp_id):
    worker = get_object_or_404(WorkerDB, user_id=emp_id)

    if request.method == "POST":
        action = request.POST.get("action")

        if action == "send_otp":
            email = request.POST.get("email")

            otp = str(random.randint(100000, 999999))
            request.session['email_otp'] = otp

            send_mail(
                "Your OTP Code",
                f"Your verification code is {otp}",
                settings.EMAIL_HOST_USER,
                [email],
                fail_silently=False
            )

            messages.success(request, "OTP sent successfully.")
            return redirect('worker_verification', emp_id=emp_id)


        elif action == "verify":
            entered_otp = request.POST.get("email_otp")
            session_otp = request.session.get("email_otp")

            if not session_otp:
                messages.error(request, "Please generate OTP first.")
                return redirect('worker_verification', emp_id=emp_id)

            if entered_otp != session_otp:
                messages.error(request, "Invalid OTP.")
                return redirect('worker_verification', emp_id=emp_id)

            password = request.POST.get("password")
            confirm_password = request.POST.get("confirm_password")

            if password != confirm_password:
                messages.error(request, "Passwords do not match.")
                return redirect('worker_verification', emp_id=emp_id)

            worker.password = make_password(password)
            worker.save()

            del request.session['email_otp']

            messages.success(request, "Account activated successfully!")
            return redirect(worker_login_page)

    return render(request, "worker_verification.html", {"worker": worker})


#
# def save_worker_password(request, emp_id):
#     if request.method == "POST":
#         pswd = request.POST.get("password")
#         hash_pswd = make_password(pswd)
#         worker = WorkerDB.objects.get(id=emp_id)
#         worker.password = hash_pswd
#         worker.save()
#         return redirect(worker_login_page)


def worker_table(request):
    worker = WorkerDB.objects.all()
    return render(request, 'show_worker.html', {"worker": worker})


# revoking worker

def revoke_worker(request, emp_id):
    if request.method == "POST":
        worker = WorkerDB.objects.get(id=emp_id)
        user = worker.user
        user.role = 'rejected'
        user.save()
        worker.delete()

    messages.error(request, 'Revoked')
    sub = "Notification of Service Provider Status Revocation"

    msg = """
        Dear {user_name},

        We regret to inform you that your status as a Service Provider in our Maintenance Management System has been revoked, effective immediately.

        As a result, you will no longer be able to access or accept service assignments under your previous registration. Any pending tasks within the system will be reviewed and reassigned as necessary.

        This decision has been made in accordance with our company policies and operational requirements. If you believe this action has been taken in error or require further clarification, we encourage you to contact the Administration Team for assistance.

        We appreciate the time and effort you have contributed to our service network and thank you for your understanding.

        Sincerely,
        Administration Team
        """.format(
        user_name=user.username
    )
    send_mail(
        subject=sub,
        message=msg,
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[worker.email],
        fail_silently=True
    )
    return redirect(worker_table)


# Role changing

def change_role_approve(request, emp_id):
    if request.method == "POST":
        del request.session['role']
        worker = WorkerDB.objects.get(user_id=emp_id)
        user = worker.user
        user.role = 'worker'
        worker.role = 'worker'
        user.save()
        worker.save()
        request.session['worker'] = user.role
        messages.success(request, 'Approved')
        request.session['role'] = worker.role
        sub = "Service Provider Application Approved"
        dashboard_url = request.build_absolute_uri(reverse('worker_verification', kwargs={'emp_id': emp_id}))

        msg = """
        Dear {user_name},

        We are pleased to inform you that your request to become a Service Provider in our Maintenance Management System has been successfully approved.

        You may now access your account and begin accepting service assignments in accordance with your registered service category.

        To proceed, please use the link below to access your dashboard:
        {dashboard_link}

        We kindly remind you to maintain the highest level of professionalism, adhere to company policies, and ensure that job statuses are updated promptly within the system.

        Should you require any assistance or further clarification, please do not hesitate to contact the Administration Team.

        We appreciate your cooperation and look forward to your valuable contribution to our service network.

        Sincerely,
        Administration Team
        """.format(
            user_name=user.username,
            dashboard_link=dashboard_url
        )
        send_mail(
            subject=sub,
            message=msg,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[worker.email]
        )
        return redirect(worker_card)


def change_role_reject(request, emp_id):
    if request.method == "POST":
        role = request.POST.get('role')
        del request.session['role']
        messages.error(request, 'rejected')
        user = Users.objects.get(user_id=emp_id)
        user.role = role
        user.save()
        WorkerDB.objects.filter(id=emp_id).delete()
        request.session['role'] = role
        sub = "Service Provider Application Update"
        msg = """
        Dear {user_name},

        Thank you for your interest in becoming a Service Provider in our Maintenance Management System.

        After careful review of your application, we regret to inform you that your request has not been approved at this time.

        This decision may be based on eligibility criteria, documentation requirements, or current service capacity. Please note that this does not prevent you from submitting a new application in the future, subject to meeting the necessary requirements.

        If you require further clarification, you may contact the Administration Team for assistance.

        We appreciate your interest in working with us and thank you for your understanding.

        Sincerely,
        Administration Team
        """.format(
            user_name=user.username
        )
        send_mail(
            subject=sub,
            message=msg,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[request.session['email']]
        )
        return redirect(worker_card)


# end role changing


def request_card(request):
    req = MaintenanceRequest.objects.all()
    req_count = MaintenanceRequest.objects.filter(status="pending").count()
    return render(request, 'request_card.html', {"req": req, "req_count": req_count})


def in_progress_req(request):
    req = MaintenanceRequest.objects.all()
    req_count = MaintenanceRequest.objects.filter(status="pending").count()
    return render(request, 'request_in_progress.html', {"req": req, "req_count": req_count})


def completed_request(request):
    req = MaintenanceRequest.objects.all()
    return render(request, 'completed_request.html', {"req": req})


# assigning work


def assigning_table(request, req_id):
    worker = WorkerDB.objects.all()
    req = MaintenanceRequest.objects.get(id=req_id)
    return render(request, 'assign_work.html', {"worker": worker, 'req': req})


def send_work_request(request, req_id):
    if request.method == "POST":
        MaintenanceRequest.objects.filter(id=req_id).update(status='reviewing', worker=request.session['worker_name'])
        maintenance = MaintenanceRequest.objects.get(id=req_id)
        sub = 'Official Assignment of Maintenance Request – Request ID: {id} '.format(id=maintenance.id)
        msg = """
        Dear {worker},

        This is to formally inform you that you have been assigned a maintenance request. The details are as follows:

        Request ID: {id}
        Customer Name: {full_name}
        Service Type: {service_type}
        Problem Title: {problem_title}
        Description: {description}
        Location: {address}, {city}
        Request Date: {date}
        Current Status: {status}

        You are kindly requested to review the above information and proceed accordingly. 
        Please update the system once the work has commenced and upon completion.

        Should you require any clarification, please contact the administration office.

        Sincerely,
        Administration Team
        """.format(
            worker=maintenance.worker,
            id=maintenance.id,
            full_name=maintenance.full_name,
            service_type=maintenance.service_type,
            problem_title=maintenance.problem_title,
            description=maintenance.description,
            address=maintenance.address,
            city=maintenance.city,
            date=maintenance.date,
            status=maintenance.status
        )
        send_mail(
            subject=sub,
            message=msg,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[request.session['worker_email']]
        )
        return redirect(request_card)


def reject_request(request, req_id):
    if request.method == "POST":
        maintenance = get_object_or_404(MaintenanceRequest, id=req_id)
        maintenance.status = 'rejected(admin)'
        maintenance.save()
        sub = "Maintenance Request Update – Request ID - {id}"
        msg = """
        Dear {customer_name},

        This is to inform you that your maintenance request has been reviewed by the Administration Team.

        After careful evaluation, we regret to inform you that your request (Request ID: {id}) has not been approved for processing at this time.

        Request Details:

        Service Type: {service_type}
        Problem Title: {problem_title}
        Location: {address}, {city}
        Request Date: {date}

        This decision may be due to incomplete information, service limitations, policy guidelines, or other administrative considerations.

        If you believe additional clarification or documentation may assist in reconsideration, you are welcome to contact the Administration Team.

        We appreciate your understanding and thank you for using our services.

        Sincerely,
        Administration Team
        """.format(
            customer_name=maintenance.full_name,
            id=maintenance.id,
            service_type=maintenance.service_type,
            problem_title=maintenance.problem_title,
            address=maintenance.address,
            city=maintenance.city,
            date=maintenance.date
        )
        send_mail(
            subject=sub,
            message=msg,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[request.session['email']]
        )
        return redirect(request_card)


def add_subscription(request):
    return render(request, 'add subscription.html')


def show_subscription(request):
    sub = SubscriptionDB.objects.all()
    return render(request, 'show_subscription.html', {"sub": sub})


def save_subscription(request):
    if request.method == "POST":
        name = request.POST.get("plan_name")
        amount = request.POST.get("price")
        duration = request.POST.get("duration_months")
        response = request.POST.get("response_time")
        inspection = request.POST.get("inspections_per_year")
        discount = request.POST.get("spare_parts_discount")
        repair = request.POST.get("free_minor_repairs")
        emergency = request.POST.get("emergency_support")
        desc = request.POST.get("description")
        img = request.FILES.get("image")
        obj = SubscriptionDB(plan_name=name, price=amount, duration=duration,
                             inspections_per_year=inspection, discount=discount,
                             response_time=response, free_minor_repairs=repair,
                             emergency_support=emergency, description=desc, image=img)
        obj.save()
        return redirect(add_subscription)


def edit_subscription(request, plan_id):
    plan = SubscriptionDB.objects.get(id=plan_id)
    return render(request, 'edit_subscription.html', {"plan": plan})


def update_subscription(request, plan_id):
    if request.method == "POST":
        name = request.POST.get("plan_name")
        amount = request.POST.get("price")
        duration = request.POST.get("duration_months")
        response = request.POST.get("response_time")
        inspection = request.POST.get("inspections_per_year")
        discount = request.POST.get("spare_parts_discount")
        repair = request.POST.get("free_minor_repairs")
        emergency = request.POST.get("emergency_support")
        desc = request.POST.get("description")
        try:
            img = request.FILES["image"]
            fs = FileSystemStorage()
            file = fs.save(img.name, img)
        except MultiValueDictKeyError:
            file = SubscriptionDB.objects.get(id=plan_id).image
        SubscriptionDB.objects.filter(id=plan_id).update(plan_name=name, price=amount, duration=duration,
                                                         inspections_per_year=inspection, discount=discount,
                                                         response_time=response, free_minor_repairs=repair,
                                                         emergency_support=emergency, description=desc, image=file)
        return redirect(show_subscription)


def delete_subscription(request, plan_id):
    SubscriptionDB.objects.get(id=plan_id).delete()
    return redirect(show_subscription)


def subscribers(request):
    users = UserPlans.objects.all()
    return render(request, "subscribers.html", {"users": users})
