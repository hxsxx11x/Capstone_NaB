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

def login(request):
    response_data = {}
    if request.method == "GET":
        return render(request, 'login.html')

    elif request.method == "POST":
        login_email = request.POST.get('email', None)  # 딕셔너리형태
        login_password = request.POST.get('password', None)

        if not (login_email and login_password):
            response_data['error'] = "이메일과 비밀번호를 입력해주세요"
        if not (Account.objects.filter(mem_email=login_email).exists()):
            response_data['error'] = "가입되지 않은 이메일입니다."
        else:
            account = Account.objects.get(mem_email=login_email)
            if account.mem_password == login_password:
                request.session['user'] = account.mem_email
                return HttpResponse('로그인 성공')
            else:
                response_data['error'] = "비밀번호가 틀렸습니다"
    return render(request, 'login.html', response_data)  # register를 요청받으면 register.html 로 응답.