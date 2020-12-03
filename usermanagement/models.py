from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


# Create your models here.
class UserExtend(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_email_verified = models.BooleanField(default=False)
    is_logged_in_verified = models.BooleanField(default=False)
    uploaded_file_name = models.TextField(default="None")
    @receiver(post_save, sender=User)
    def create_user_extend(sender, instance, created, **kwargs):
        if created:
            UserExtend.objects.create(user=instance)

    @receiver(post_save, sender=User)
    def save_user_extend(sender, instance, **kwargs):
        instance.userextend.save()
