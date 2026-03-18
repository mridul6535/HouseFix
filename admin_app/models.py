from django.db import models
from web_app.models import Users


# Create your models here.class User(AbstractUser):
# class User(AbstractUser):
#     email = models.EmailField(unique=True)
#     name=models.CharField(max_length=100,null=True)
#     default_role = "user"
#     role = models.CharField(max_length=50, default=default_role)
#     username = None
#     USERNAME_FIELD = 'email'
#     REQUIRED_FIELDS = []


class CategoryDB(models.Model):
    category_name = models.CharField(max_length=100, unique=True)
    category_description = models.CharField(max_length=1000)
    category_photo = models.ImageField(upload_to="category_image", null=True)


class Notification(models.Model):
    user = models.ForeignKey(Users, on_delete=models.CASCADE)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
