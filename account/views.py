from django.contrib import auth
from django.contrib.auth import authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from .models import Account


def signup(request):
    if request.method == 'POST':
        email = request.POST['email']
        password1 = request.POST['password1']
        password2 = request.POST['password2']
        username = request.POST['username']
        birthday = request.POST['birthday']
        gender = request.POST['gender']

        if password1 == password2:
            # 비밀번호 해싱
            #hashed_password = make_password(password1)

            try:
                # 사용자 생성 및 저장
                account = Account.objects.create(
                    mem_email=email,
                    mem_password=password1,
                    mem_username=username,
                    mem_birthday=birthday,
                    mem_gender=gender
                )

                # 홈 페이지로 리다이렉트
                return redirect('/')
            except Exception as e:
                # 사용자 생성 실패 시 에러 메시지 전달
                error_message = f"회원가입 실패: {str(e)}"
                return render(request, 'signup.html', {'error': error_message})
        else:
            # 비밀번호 불일치 시 에러 메시지 전달
            return render(request, 'signup.html', {'error': '비밀번호가 일치하지 않습니다.'})

    return render(request, 'signup.html')

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')  # 'home'은 홈페이지의 URL 이름에 따라 수정하세요
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})
