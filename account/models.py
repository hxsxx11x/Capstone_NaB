from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import BaseUserManager
from django.utils import timezone

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)


# Create your models here.
class CustomUser(AbstractUser):
    # 추가적인 사용자 필드들을 정의할 수 있습니다
    birthday = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=10, choices=[('man', '남성'), ('woman', '여성')], null=True,
                              blank=True)
    objects = CustomUserManager()

    class Meta:
        verbose_name = '사용자'
        verbose_name_plural = '사용자'
        
#정현욱 분석결과 db에 저장

class SelectedWorkout(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    workout_name = models.CharField(max_length=100)
    day = models.CharField(max_length=10, null=True)  # 요일을 저장하는 필드 추가, nullable로 변경_non-nullable인 경우에는 default값이 필요하다고 뜸
    timelog = models.DateTimeField(default=timezone.localtime) #현재 시간으로 저장
    def __str__(self):
        return f"{self.user.username}'s selected workout: {self.workout_name} on {self.day}"


class SelectedDiet(models.Model):
    diet_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    diet_name = models.CharField(max_length=100)
    day = models.CharField(max_length=10, null=True)  # 요일을 저장하는 필드 추가, nullable로 변경_non-nullable인 경우에는 default값이 필요하다고 뜸
    meal = models.name = models.CharField(max_length=20, null=True)
    timelog = models.DateTimeField(default=timezone.localtime) #현재 시간으로 저장
    def __str__(self):
        return f"{self.user.username}'s selected diet: {self.diet_name} on {self.day}"