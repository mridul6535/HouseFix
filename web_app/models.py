from django.db import models


# Create your models here.
class Users(models.Model):
    username = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=100)
    role = models.CharField(default='user', max_length=10)


class WorkerDB(models.Model):
    user = models.OneToOneField(Users, on_delete=models.CASCADE)
    username = models.CharField(max_length=50)
    password = models.CharField(max_length=50)
    email = models.CharField(max_length=20)
    mobile = models.CharField(max_length=20)
    category = models.CharField(max_length=50)
    city = models.CharField(max_length=100)
    working_time = models.CharField(max_length=100)
    experience = models.CharField(max_length=100)
    role = models.CharField(default='user', max_length=10)
    id_image = models.ImageField(upload_to='ids/personal_id/')
    professional_id_image = models.ImageField(upload_to='ids/worker_id/')
    worker_image = models.ImageField(upload_to='worker_photo', blank=True)


class MaintenanceRequest(models.Model):
    user = models.CharField(max_length=50)
    full_name = models.CharField(max_length=50)
    problem_title = models.CharField(max_length=200)
    service_type = models.CharField(max_length=50)  # category
    problem_image = models.ImageField(upload_to='maintenance_images/', blank=True, null=True)
    city = models.CharField(max_length=50)
    pin_code = models.CharField(max_length=50)
    address = models.CharField(max_length=255)
    description = models.TextField()
    status = models.TextField(default='pending')
    worker = models.CharField(max_length=50, default='not assigned')
    worker_id = models.IntegerField(default=0)
    date = models.DateField(auto_now_add=True)
    work_started_date = models.DateField(default=None, null=True, blank=True)
    completed_date = models.DateField(default=None, null=True, blank=True)
    payment = models.CharField(max_length=100, default='pending', null=True)


class ContactDB(models.Model):
    username = models.CharField(max_length=100, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    message = models.TextField(null=True, blank=True)


class SubscriptionDB(models.Model):
    username = models.CharField(max_length=100, null=True, blank=True)
    plan_name = models.CharField(max_length=100, null=True, blank=True)
    price = models.IntegerField(blank=True, null=True)
    duration = models.IntegerField(blank=True, null=True)
    response_time = models.IntegerField(blank=True, null=True, help_text="Service response time in hours")
    inspections_per_year = models.IntegerField(blank=True, null=True)
    discount = models.IntegerField(blank=True, null=True)
    free_minor_repairs = models.CharField(max_length=50, blank=True, null=True)
    emergency_support = models.BooleanField(blank=True, null=True)
    seasonal_inspection = models.BooleanField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='subscription_plans/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)


class UserPlans(models.Model):
    username = models.CharField(max_length=100, null=True, blank=True)
    plan = models.CharField(max_length=100, null=True, blank=True)
    payment = models.CharField(default='pending', max_length=100, null=True, blank=True)
    start_date = models.DateField(max_length=100, null=True, blank=True)
    end_date = models.DateField(max_length=100, null=True, blank=True)
