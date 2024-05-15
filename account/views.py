from django.contrib import auth, messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.shortcuts import render, redirect
from main.models import UserBia, WorkoutData
from .models import CustomUser, CustomUserManager, SelectedWorkout
from .forms import UserForm, UserUpdateForm
from django.contrib.auth.decorators import login_required


def signup_view(request):
    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            try:
                form.save()
                username = form.cleaned_data.get('id_username')
                raw_password = form.cleaned_data.get('id_password1')
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
    return redirect('/')


def profile_view(request):
    # 세션에서 현재 사용자 정보 가져오기
    username = request.user.username
    user_bia = UserBia.objects.filter(username=username).order_by('-bia_num').first()

    if not username:
        return redirect('/')  # 로그인 상태가 아니라면 로그인 페이지로 리다이렉트
    # 사용자 정보를 가져오기
    account = CustomUser.objects.get(username=username)
    
    context = {'username': account.username,
               'status': user_bia.status if user_bia else '상태 정보가 없습니다. 체성분 검사를 실행해주세요!'}
    
    return render(request, 'profile.html', context)

def delete_view(request):
    request.user.delete()
    logout(request)
    messages.success(request, '탈퇴 되었습니다.')
    return redirect('/')

def userInformation_view(request):
    if request.user.is_authenticated:
        # 인증된 사용자인 경우
        username = request.user.username
        account = CustomUser.objects.get(username=username)
        context = {'user': account}
        return render(request, 'userInformation.html', context)
    else:
        # 인증되지 않은 사용자는 로그인 페이지로 리디렉션
        return redirect('/')

def update_view(request):
    if request.user.is_authenticated:
        # 인증된 사용자인 경우
        username = request.user.username
        account = CustomUser.objects.get(username=username)
        form = UserUpdateForm(instance=account)
        if request.method == 'POST':
            form = UserUpdateForm(request.POST, instance=account)
            form.username = username
            if form.is_valid():
                form.save()
                return redirect('/')
        context = {'user': account, 'form': form}
        return render(request, 'update.html', context)
    else:
        # 인증되지 않은 사용자는 로그인 페이지로 리디렉션
        return redirect('/')

def dietmenu_view(request):
    if request.user.is_authenticated:
        username = request.user.username
        account = CustomUser.objects.get(username=username)
        context = {'user': account}
        return render(request, 'dietmenu.html', context)
    else:
        # 인증되지 않은 사용자는 로그인 페이지로 리디렉션
        return redirect('/')

def biagraph_view(request):
    if request.user.is_authenticated:
        username = request.user.username
        account = CustomUser.objects.get(username=username)
        context = {'user': account}
        return render(request, 'biagraph.html', context)
    else:
        # 인증되지 않은 사용자는 로그인 페이지로 리디렉션
        return redirect('/')

def select_workouts(significants):
    # 요일별 운동 종목 선택 로직
    day_workouts = {
        '월': [],
        '화': [],
        '수': [],
        '목': [],
        '금': [],
        '토': [],
        '일': []
    }

    # 가슴 및 이두 운동 선택
    chest_workouts = WorkoutData.objects.filter(part='가슴', target__contains='대흉근').exclude(
        etc__contains='허리부담' if 'waist' in significants else '').order_by('?')[:3]
    biceps_workouts = WorkoutData.objects.filter(part='팔', target__contains='이두근').exclude(
        etc__contains='허리부담' if 'waist' in significants else '').order_by('?')[:1]

    # 등 및 삼두 운동 선택
    back_workouts = WorkoutData.objects.filter(part='등', target__contains='광배근').exclude(
        etc__contains='허리부담' if 'waist' in significants else '').order_by('?')[:3]
    triceps_workouts = WorkoutData.objects.filter(part='팔', target__contains='삼두근').exclude(
        etc__contains='허리부담' if 'waist' in significants else '').order_by('?')[:1]

    # 어깨 및 하체 운동 선택
    shoulder_workouts = WorkoutData.objects.filter(part='어깨', target__contains='전면삼각근').exclude(
        etc__contains='허리부담' if 'waist' in significants else '').order_by('?')[:2]
    leg_workouts = WorkoutData.objects.filter(part='하체', target__contains='대퇴사두근').exclude(
        etc__contains='허리부담' if 'waist' in significants else '').order_by('?')[:2]

    # 운동 프로그램 구성
    for day in ['월', '목']:
        day_workouts[day].extend(list(chest_workouts) + list(biceps_workouts))
    for day in ['화', '금']:
        day_workouts[day].extend(list(back_workouts) + list(triceps_workouts))
    for day in ['수', '토']:
        day_workouts[day].extend(list(shoulder_workouts) + list(leg_workouts))
    for day in ['일']:
        day_workouts[day].extend(['일요일은 쉬는 날!'])
    return day_workouts

def result_view(request):
    current_username = request.user.username
    user_bia = UserBia.objects.filter(username=current_username).order_by('-bia_num').first()

    if user_bia:
        significants = user_bia.significants
        workouts = select_workouts(significants)
        
    else:
        workouts = {}

    context = {
        'user_id': current_username,
        'status': user_bia.status if user_bia else '상태 정보 없음',
        'day_workouts': workouts,
    }

    return render(request, 'result.html', context)

def save_selected_workouts(user, selected_workouts):
    for day, workouts in selected_workouts.items():
        for workout, significant in workouts.items():
            selected_workout = SelectedWorkout(user=user, workout_name=workout, significant_body_part=significant)
            selected_workout.save()