from django.db import models

# Create your models here.


class User(models.Model):
    gender = (('male', "男"), ('female', "女"),)
    name = models.CharField(max_length=128, unique=True, help_text="用户名")
    password = models.CharField(max_length=256, help_text="密码")
    email = models.EmailField(unique=True, help_text="邮箱")
    sex = models.CharField(max_length=32, choices=gender,
                           default="男", help_text="性别")
    age = models.IntegerField(null=True, help_text="年龄")
    phoneNumber = models.CharField(
        max_length=11, null=True, unique=True, help_text="手机号码")
    c_time = models.DateTimeField(auto_now_add=True, help_text="注册时间")
    has_confirmed = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["-c_time"]
        verbose_name = '用户'
        verbose_name_plural = '用户'


class ConfirmString(models.Model):
    code = models.CharField(max_length=256, help_text="注册码")
    user = models.OneToOneField('User', help_text="用户")
    c_time = models.DateTimeField(auto_now_add=True, help_text="提交时间")

    def __str__(self):
        return self.user.name+":"+self.code

    class Meta:
        ordering = ["-c_time"]
        verbose_name = "确认码"
        verbose_name_plural = "确认码"
