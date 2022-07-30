from pyexpat import model
from django.db import models
from django.utils import timezone
# Create your models here.


class User(models.Model):
    email_address = models.CharField(max_length=32)
    username = models.CharField(max_length=32)
    password = models.CharField(max_length=32)
    times = models.IntegerField(default=100)
    create_time = models.DateTimeField(default=timezone.now())
    is_login = models.IntegerField(default=0)

    # 四种功能的使用次数
    cd_use_time = models.IntegerField(default=0)
    td_use_time = models.IntegerField(default=0)
    te_use_time = models.IntegerField(default=0)
    tc_use_time = models.IntegerField(default=0)

    def verify_password(self, password):
        return self.password == password

    def has_login(self):
        return self.is_login == 1

    class Meta:
        db_table = 'user'

    def __str__(self):
        return self.username


class VertificationCode(models.Model):
    email_address = models.CharField(max_length=32)
    vertificationCode = models.IntegerField()
    
    def vertify(self, vertificationCode):
        return self.vertificationCode == vertificationCode

    class Meta:
        db_table = 'vtf_code'
    
    def __str__(self):
        return self.email_address + ':' + self.vertificationCode
    
