from django.db import models
from django.utils import timezone
# Create your models here.

class History(models.Model):
    email_address = models.CharField(max_length=50)
    upload_images = models.TextField()
    result_images = models.TextField()
    upload_time = models.DateTimeField(default=timezone.now())
    type = models.CharField(max_length=60)

    class Meta:
        db_table = 'history'

