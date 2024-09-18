# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class AccountCustomuser(models.Model):
    id = models.BigAutoField(primary_key=True)
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.IntegerField()
    username = models.CharField(unique=True, max_length=150)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.CharField(max_length=254)
    is_staff = models.IntegerField()
    is_active = models.IntegerField()
    date_joined = models.DateTimeField()
    birthday = models.DateField(blank=True, null=True)
    gender = models.CharField(max_length=10, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'account_customuser'


class AccountCustomuserGroups(models.Model):
    id = models.BigAutoField(primary_key=True)
    customuser = models.ForeignKey(AccountCustomuser, models.DO_NOTHING)
    group = models.ForeignKey('AuthGroup', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'account_customuser_groups'
        unique_together = (('customuser', 'group'),)


class AccountCustomuserUserPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    customuser = models.ForeignKey(AccountCustomuser, models.DO_NOTHING)
    permission = models.ForeignKey('AuthPermission', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'account_customuser_user_permissions'
        unique_together = (('customuser', 'permission'),)


class AuthGroup(models.Model):
    name = models.CharField(unique=True, max_length=150)

    class Meta:
        managed = False
        db_table = 'auth_group'


class AuthGroupPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)
    permission = models.ForeignKey('AuthPermission', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_group_permissions'
        unique_together = (('group', 'permission'),)


class AuthPermission(models.Model):
    name = models.CharField(max_length=255)
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING)
    codename = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'auth_permission'
        unique_together = (('content_type', 'codename'),)


class DietData(models.Model):
    diet_num = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    kcal = models.FloatField()
    category = models.CharField(max_length=100)
    carb = models.FloatField()
    fat = models.FloatField()
    protein = models.FloatField()
    etc = models.CharField(max_length=100)
    caption = models.CharField(max_length=500)

    class Meta:
        managed = False
        db_table = 'diet_data'


class DjangoAdminLog(models.Model):
    action_time = models.DateTimeField()
    object_id = models.TextField(blank=True, null=True)
    object_repr = models.CharField(max_length=200)
    action_flag = models.PositiveSmallIntegerField()
    change_message = models.TextField()
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING, blank=True, null=True)
    user = models.ForeignKey(AccountCustomuser, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'django_admin_log'


class DjangoContentType(models.Model):
    app_label = models.CharField(max_length=100)
    model = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'django_content_type'
        unique_together = (('app_label', 'model'),)


class DjangoMigrations(models.Model):
    id = models.BigAutoField(primary_key=True)
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_migrations'


class DjangoSession(models.Model):
    session_key = models.CharField(primary_key=True, max_length=40)
    session_data = models.TextField()
    expire_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_session'


class User(models.Model):
    mem_idx = models.AutoField(primary_key=True)
    mem_email = models.CharField(unique=True, max_length=100)
    mem_password = models.CharField(max_length=100)
    mem_username = models.CharField(max_length=20)
    mem_birthday = models.DateField()
    mem_gender = models.CharField(max_length=8)

    class Meta:
        managed = False
        db_table = 'user'


class UserBia(models.Model):
    bia_num = models.AutoField(primary_key=True)
    date = models.DateField()
    username = models.CharField(max_length=100)
    age = models.IntegerField()
    height = models.FloatField()
    weight = models.FloatField()
    skeletal = models.FloatField()
    fat = models.FloatField()
    fat_per = models.FloatField()
    bmi = models.FloatField()
    status = models.CharField(max_length=100)
    bmr = models.FloatField()
    significants = models.CharField(max_length=100, null=True)
    class Meta:
        managed = False
        db_table = 'user_bia'


class WorkoutData(models.Model):
    work_num = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    part = models.CharField(max_length=100)
    target = models.CharField(max_length=100)
    category = models.CharField(max_length=100)
    etc = models.CharField(max_length=100)
    difficulty = models.CharField(max_length=100)
    caption = models.CharField(max_length=500)

    class Meta:
        managed = False
        db_table = 'workout_data'

class DietMenu(models.Model):
    menu_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    serving = models.FloatField()
    calorie = models.FloatField()
    carbohydrate = models.FloatField()
    protein = models.FloatField()
    province = models.FloatField()
    type1 = models.CharField(max_length=100)
    type2 = models.CharField(max_length=100)
    etc = models.CharField(max_length=100)
    class Meta:
        managed = False
        db_table = 'diet_menu'
