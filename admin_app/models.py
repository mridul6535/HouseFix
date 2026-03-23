from django.db import models
from web_app.models import Users


# Create your models here.class User(AbstractUser):


class CategoryDB(models.Model):
    category_name = models.CharField(max_length=100, unique=True)
    category_description = models.CharField(max_length=1000)
    category_photo = models.ImageField(upload_to="category_image", null=True)


class Notification(models.Model):
    user = models.ForeignKey(Users, on_delete=models.CASCADE)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
