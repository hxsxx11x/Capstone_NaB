from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import CustomUser  # CustomUser 모델 import

class UserForm(UserCreationForm):
    email = forms.EmailField(label="email")
    birthday = forms.DateField(label="birthday", widget=forms.DateInput(attrs={'type': 'date'}))
    gender = forms.ChoiceField(choices=[('man', '남성'), ('woman', '여성'),], label="gender")

    class Meta:
        model = CustomUser
        fields = ("username", "password1", "password2", "email", "birthday", "gender")

class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField(label="email")
    birthday = forms.DateField(label="birthday", widget=forms.DateInput(attrs={'type': 'date'}))
    gender = forms.ChoiceField(choices=[('man', '남성'), ('woman', '여성')], label="gender")
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'birthday', 'gender']