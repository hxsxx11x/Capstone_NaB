from django.contrib import auth, messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.shortcuts import render, redirect
from .forms import UserForm


def signup_view(request):
    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            try:
                form.save()
                username = form.cleaned_data.get('email')
                raw_password = form.cleaned_data.get('password1')
                user = authenticate(username=username, password=raw_password)  # 사용자 인증
                # 홈 페이지로 리다이렉트
                return redirect('/')
            except Exception as e:
                # 사용자 생성 실패 시 에러 메시지 전달
                print(f"An exception occurred: {e}")
                return render(request, 'signup.html', )
    else:
        form = UserForm()

    return render(request, 'signup.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.success(request, '로그아웃 되었습니다.')
    return redirect('main')

def profile_view(request):
    # 세션에서 현재 사용자 정보 가져오기
    username = request.user.username

    if not username:
        return redirect('login')  # 로그인 상태가 아니라면 로그인 페이지로 리다이렉트

    # 사용자 정보를 가져오기
    account = User.objects.get(username=username)
    context = {'username': account.username}
    return render(request, 'profile.html', context)

def delete_view(request):
    request.user.delete()
    logout(request)
    messages.success(request, '탈퇴 되었습니다.')
    return redirect('main')