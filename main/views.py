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
def main(request):
    return render(request, 'main.html')

