from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout
import mysql.connector

db = mysql.connector.connect(
    host="localhost",
    user="root",
    passwd="1111",
    database="NaB"
)

def signup_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')  # 'home'은 홈페이지의 URL 이름에 따라 수정하세요
    else:
        form = UserCreationForm()
    return render(request, 'signup.html', {'form': form})

def logout_view(request):
    if request.method == 'POST':
        logout(request)
        return redirect('home')  # 'home'은 홈페이지의 URL 이름에 따라 수정하세요

def home_view(request):
    return render(request, 'home.html')

