from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class UserForm(UserCreationForm):
    email = forms.EmailField(label="email")
    birthday = forms.DateField(label="birthday", widget=forms.DateInput(attrs={'type': 'date'}))
    gender = forms.ChoiceField(choices=[('man', '남성'), ('woman', '여성'), ('unsigned', '미정')], label="gender")

    class Meta:
        model = User
        fields = ("username", "password1", "password2", "email", "birthday", "gender")