from django.db import models
from django.core.validators import MinLengthValidator

class Account(models.Model):
    mem_idx = models.AutoField(primary_key=True)
    mem_email = models.EmailField(unique=True)
    mem_password = models.CharField(max_length=50, validators=[MinLengthValidator(6)])
    mem_username = models.CharField(max_length=20)
    mem_birthday = models.DateField()
    mem_gender = models.CharField(max_length=10, choices=[('man', '남성'), ('woman', '여성'), ('unsigned', '미정')])

    class Meta:
        managed = False
        db_table = 'user'