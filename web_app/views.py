import datetime

from django.shortcuts import render, redirect
from web_app.models import *
from admin_app.models import CategoryDB
from django.contrib import messages
from django.contrib.auth.hashers import check_password, make_password
import stripe
from huggingface_hub import InferenceClient
from django.core.mail import send_mail
from django.conf import settings


# Create your views here.

def home_page(request):
    sub = SubscriptionDB.objects.all()
    response = request.session.pop("response", "")
    message = request.session.pop("message", "")
    return render(request, 'index.html', {"response": response, 'message': message, "sub": sub})


def about_page(request):
    return render(request, 'about.html')


def contact_page(request):
    return render(request, 'contact.html')


def reg_page(request):
    return render(request, 'reg.html')


def service_page(request):
    return render(request, 'services.html')


def log_page(request):
    return render(request, 'log.html')


def save_contact(request):
    if request.method == "POST":
        name = request.POST.get("name")
        mail = request.POST.get("email")
        msg = request.POST.get("message")
        obj = ContactDB(username=name, email=mail, message=msg)
        obj.save()
        return redirect(contact_page)


def reg_user(request):
    if request.method == "POST":
        name = request.POST.get("username")
        mail = request.POST.get("email")
        pswd = request.POST.get("password")
        role = request.POST.get("role")
        hash_pswd = make_password(pswd)
        if Users.objects.filter(username=name).exists():
            messages.error(request, 'Username already exist')
            return redirect(log_page)
        elif Users.objects.filter(email=mail).exists():
            messages.error(request, 'Email already exist')
            return redirect(reg_page)
        obj = Users(username=name, email=mail, password=hash_pswd, role=role)
        messages.success(request, 'successfully registered')
        obj.save()
        return redirect(log_page)


# verify worker using email and user using username
def user_login(request):
    if request.method == "POST":
        name = request.POST.get("username")
        mail = request.POST.get("email")
        pswd = request.POST.get("password")

        user = Users.objects.filter(username=name, email=mail).first()

        if not user:
            messages.error(request, "User  Not Found")
            return redirect(reg_page)

        if not check_password(pswd, user.password):
            messages.error(request, "Password does not match")
            return redirect(log_page)

        request.session['role'] = user.role
        request.session['username'] = name
        request.session['email'] = mail
        request.session['id'] = user.id

        return redirect(home_page)


def user_logout(request):
    request.session.flush()
    return redirect(home_page)


def add_worker(request):
    cat = CategoryDB.objects.all()
    return render(request, 'add_worker.html', {"cat": cat})


def worker_request(request):
    if request.method == "POST":
        user = request.session.get("email")
        user_obj = Users.objects.get(email=user)
        name = request.POST.get("username")
        mail = request.POST.get("email")
        mob = request.POST.get("mobile")
        # password will be saved during verification
        cat = request.POST.get("category")
        loc = request.POST.get("city")
        time = request.POST.get("working_time")
        exp = request.POST.get("experience")
        id_photo = request.FILES.get("id_image")
        pro_image = request.FILES.get("pro_id_image")
        worker_img = request.FILES.get("worker_image")
        role = request.POST.get("role")
        messages.success(request, 'request submitted successfully')
        obj = WorkerDB(mobile=mob, category=cat, city=loc, worker_image=worker_img,
                       working_time=time, experience=exp, id_image=id_photo
                       , professional_id_image=pro_image, role=role, user=user_obj,
                       username=name, email=mail)
        user_obj.role = role
        user_obj.save()
        user = Users.objects.get(username=request.session.get('username'))
        request.session['role'] = role
        obj.save()
        sub = "New Service Provider Registration Request Submitted"

        msg = """
        Dear Administration Team,

        This is to inform you that a new request has been submitted to register as a Service Provider (Worker) in the House Maintenance Management System.

        Applicant Details:
        ----------------------------------------
        Username: {user_name}
        Email: {user_email}
        Contact Number: {user_phone}
        Requested Service Category: {service_category}
        ----------------------------------------

        Please review the submitted details and take the necessary action to approve or reject the request within the system.

        Kindly log in to the admin dashboard to proceed with the verification process.

        Thank you.

        System Notification
        """.format(
            user_name=name,
            user_email=mail,
            user_phone=mob,
            service_category=cat
        )
        send_mail(
            subject=sub,
            message=msg,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[mail]
        )
        return redirect(home_page)


# request section

def request_form(request):
    cat = CategoryDB.objects.all()
    return render(request, "request.html", {"cat": cat, })


def manage_request(request):
    req = MaintenanceRequest.objects.filter(user=request.session['username'])
    return render(request, 'request_status.html', {"req": req})


def worker_id(request, worker):
    work = WorkerDB.objects.get(username=worker)
    return render(request, 'worker_card.html', {"work": work})


# payment and request saving together
stripe.api_key = settings.STRIPE_SECRET_KEY


def stripe_payment(request):
    if request.method == "POST":
        obj = MaintenanceRequest.objects.create(
            user=request.POST.get("username"),
            full_name=request.POST.get("full_name"),
            problem_title=request.POST.get("problem_title"),
            service_type=request.POST.get("category_name"),
            city=request.POST.get("city"),
            pin_code=request.POST.get("pin_code"),
            address=request.POST.get("address"),
            description=request.POST.get("description"),
            problem_image=request.FILES.get('problem_image'),
            payment="unpaid",
            status='pending'
        )
        request.session['maintenance_id'] = obj.id

        checkout_session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{
                "price_data": {
                    "currency": "usd",
                    "product_data": {
                        "name": "Maintenance Booking Fee",
                    },
                    "unit_amount": 1500,
                },
                "quantity": 1,
            }],
            mode="payment",
            metadata={"request_id": obj.id},
            success_url="http://localhost:8000/HouseFix/payment_success/",
            cancel_url="http://localhost:8000/HouseFix/payment_failed/",
        )

        return redirect(checkout_session.url)


def payment_success(request):
    messages.success(request, 'Request Submitted Successfully')

    obj_id = request.session.get('maintenance_id')
    obj = MaintenanceRequest.objects.filter(id=obj_id).first()

    if not obj:
        messages.error(request, "Invalid maintenance request.")
        return redirect(request_form)

    obj.payment = 'paid'
    obj.save()

    maintenance = obj
    sub = "New Maintenance Request Submitted"

    msg = f"""
Dear Administration Team,

A new maintenance request has been submitted.

Request ID: {maintenance.id}
Submitted By: {maintenance.full_name}
Email: {request.session.get('email')}
Service Category: {maintenance.service_type}
Description: {maintenance.description}
"""

    send_mail(
        subject=sub,
        message=msg,
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[request.session.get('admin_email')],
        fail_silently=False
    )

    return redirect(manage_request)


def payment_failed(request):
    messages.error(request, 'Payment Failed. Request not completed. ')
    obj_id = request.session.get('maintenance_id')
    obj = MaintenanceRequest.objects.get(id=obj_id)
    obj.payment = 'failed'
    obj.status = 'pending'
    obj.save()
    return redirect(request_form)


def cancel_request(request, request_id):
    messages.error(request, 'request cancelled')
    MaintenanceRequest.objects.filter(id=request_id).delete()
    return redirect(manage_request)


# Create client once
client = InferenceClient(model="meta-llama/Llama-3.1-8B-Instruct", token=settings.HF_API_KEY)


def chatbot(request):
    if request.method == "POST":
        user_message = request.POST.get("message")

        try:
            response = client.chat_completion(
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": user_message}
                ],
                max_tokens=250,
                temperature=0.7
            )

            reply = response.choices[0].message.content

        except Exception:
            reply = "AI service is temporarily unavailable."

        request.session["response"] = reply
        request.session["message"] = user_message

    return redirect(home_page)


# subscription
def single_plan(request, plan_id):
    plan = SubscriptionDB.objects.get(id=plan_id)
    return render(request, 'single_plan.html', {"plan": plan})


def stripe_subscription(request):
    if request.method == "POST":
        duration = int(request.POST.get("year"))
        price = int(request.POST.get("price"))
        plan_name = request.POST.get("plan")
        u_name = request.session.get('username')

        date = datetime.date.today()
        next_year = date.replace(year=date.year + duration)

        obj = UserPlans(username=u_name, plan=plan_name, start_date=date, end_date=next_year)
        obj.save()
        request.session['plan_id'] = obj.id

        product = stripe.Product.create(name=plan_name, )
        stripe_price = stripe.Price.create(unit_amount=price * 100, currency="inr", recurring={"interval": "year", },
                                           product=product.id, )

        checkout_session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{
                "price": stripe_price.id,
                "quantity": 1,
            }],
            mode="subscription",
            success_url="http://localhost:8000/HouseFix/plan_success/",
            cancel_url="http://localhost:8000/HouseFix/plan_failed/",
        )

        return redirect(checkout_session.url)


def plan_success(request):
    plan_id = request.session.get('plan_id')
    plan = SubscriptionDB.objects.get(id=plan_id)
    plan.payment = 'paid'
    return redirect(home_page)


def plan_failed(request):
    plan_id = request.session.get('plan_id')
    plan = SubscriptionDB.objects.filter(id=plan_id)
    plan.delete()
    return redirect(home_page)
