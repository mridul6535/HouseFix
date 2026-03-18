from django.shortcuts import render, redirect
from web_app.models import *
from admin_app.models import *
from django.core.mail import send_mail
from django.contrib import messages
from django.contrib.auth.hashers import check_password
from django.core.files.storage import FileSystemStorage
from django.utils.datastructures import MultiValueDictKeyError
from django.conf import settings
from django.utils import timezone


def worker_login_page(request):
    return render(request, 'worker_login.html')


def worker_login(request):
    if request.method == "POST":
        name = request.POST.get("worker_name")
        mail = request.POST.get("worker_email")
        pswd = request.POST.get("password")

        worker = WorkerDB.objects.filter(username=name).first()

        if not worker:
            messages.error(request, 'Worker does not exist !')
            return redirect('login')

        if not check_password(pswd, worker.password):
            messages.error(request, 'Wrong Password !')
            return redirect('login')

        request.session['worker_id'] = worker.id
        request.session['worker_name'] = name
        request.session['worker_email'] = mail

        return redirect('worker_request')


def worker_logout(request):
    del request.session['worker_name']
    del request.session['worker_email']
    return redirect('home')


def worker_dash(request):
    if not request.session.get('worker_email'):
        return redirect('login')

    worker = WorkerDB.objects.get(username=request.session['worker_name'])

    show_work = MaintenanceRequest.objects.filter(worker=request.session['worker_name'])

    work_count = MaintenanceRequest.objects.filter(
        worker=request.session['worker_name'],
        status='accepted'
    ).count()

    return render(request, 'dashboard_w.html', {
        'show_work': show_work,
        "work_count": work_count,
        'worker': worker
    })


def worker_profile(request, worker_id):
    profile = WorkerDB.objects.get(id=worker_id)
    return render(request, 'profile.html', {"profile": profile})


def edit_worker(request, worker_id):
    cat = CategoryDB.objects.all()
    worker = WorkerDB.objects.get(id=worker_id)
    return render(request, 'edit_worker.html', {"worker": worker, "cat": cat})


def update_worker(request, worker_id):
    if request.method == "POST":

        del request.session['worker_name']

        name = request.POST.get("username")
        loc = request.POST.get("city")
        cat = request.POST.get("category")
        exp = request.POST.get("experience")
        time = request.POST.get("working_time")

        request.session['worker_name'] = name

        try:
            fs = FileSystemStorage()
            img = request.FILES['worker_image']
            file = fs.save(img.name, img)
        except MultiValueDictKeyError:
            file = WorkerDB.objects.get(id=worker_id).worker_image

        WorkerDB.objects.filter(id=worker_id).update(
            city=loc,
            category=cat,
            experience=exp,
            working_time=time,
            worker_image=file,
            username=name
        )

        messages.success(request, 'Updated Successfully')

        return redirect('worker_request')


def job_request(request):
    worker = WorkerDB.objects.get(username=request.session['worker_name'])

    show_work = WorkerDB.objects.all()

    req = MaintenanceRequest.objects.filter(worker=request.session['worker_name'])

    req_count = MaintenanceRequest.objects.count()

    return render(request, 'request_card_w.html', {
        "req": req,
        "req_count": req_count,
        'show_work': show_work,
        'worker': worker
    })


def all_jobs(request):
    worker = WorkerDB.objects.get(username=request.session['worker_name'])

    all_job = MaintenanceRequest.objects.filter(worker=request.session['worker_name'])

    return render(request, 'all_jobs.html', {
        "all_job": all_job,
        'worker': worker
    })


def accept_job(request, req_id):
    if request.method == "POST":
        w_id = request.POST.get("worker_id")

        MaintenanceRequest.objects.filter(id=req_id).update(
            status='accepted',
            worker=request.session['worker_name'],
            worker_id=w_id
        )

        return redirect('worker_request')


def reject_job(request, req_id):
    if request.method == "POST":
        name = request.POST.get("subject")
        sub = request.POST.get("worker")
        mail_to = request.POST.get("to_email")
        msg = request.POST.get("message")

        MaintenanceRequest.objects.filter(id=req_id).update(
            status='rejected(worker)',
            worker=name
        )

        send_mail(
            subject=sub,
            message=msg,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[mail_to]
        )

        return redirect('worker_request')


def start_work(request, job_id):
    if request.method == "POST":
        sts = request.POST.get("status")

        date = timezone.now().date()

        MaintenanceRequest.objects.filter(id=job_id).update(
            status=sts,
            work_started_date=date
        )

        return redirect('worker_request')


def completed_work(request, job_id):
    job = MaintenanceRequest.objects.get(id=job_id)

    return render(request, 'work_completed.html', {"job": job})


def work_completed(request, job_id):
    if request.method == "POST":

        date = timezone.now().date()

        try:
            img = request.FILES['completion_image']
            fs = FileSystemStorage()
            file = fs.save(img.name, img)

        except MultiValueDictKeyError:
            file = MaintenanceRequest.objects.get(id=job_id).problem_image

        MaintenanceRequest.objects.filter(id=job_id).update(
            status='completed',
            problem_image=file,
            completed_date=date
        )

        return redirect('worker_request')
