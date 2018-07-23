from django.db import models
from django.utils import timezone
import datetime
# Create your models here.

class Flows(models.Model):
    pub_date = models.DateTimeField('date published')
    test_set = models.IntegerField(default=0)
    flow_name = models.CharField(max_length=200)
    tx = models.IntegerField(default=0)
    rx = models.IntegerField(default=0)
    drop_count = models.IntegerField(default=0)
    drop_time = models.IntegerField(default=0)
    description = models.CharField(max_length=200)

    def __str__(self):
        return self.flow_name+', drop: '+str(self.drop_count)

    def was_published_recently(self):
        return self.pub_date >= timezone.now() - datetime.timedelta(days=1)

class Document(models.Model):
    path = models.FileField(upload_to='documents/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
