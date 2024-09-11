from django.contrib import auth, messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from main.models import UserBia, WorkoutData, DietData
from .models import CustomUser, CustomUserManager, SelectedWorkout
from .forms import UserForm, UserUpdateForm
from django.contrib.auth.decorators import login_required
from .models import SelectedWorkout
from django.utils import timezone


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

    if request.method == 'POST':
        if 'make_model' in request.POST:
            return redirect(reverse('biaengine:makemodel'))

    context = {'username': account.username}

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
        entries = UserBia.objects.filter(username=username).order_by('date')
        dates = [entry.date.strftime("%Y-%m-%d") for entry in entries]
        weights = [entry.weight for entry in entries]
        bmi = [entry.bmi for entry in entries]

        return render(request, 'biagraph.html', {'user': account, 'dates': dates, 'weights': weights, 'bmi': bmi})
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
    chest_workouts = WorkoutData.objects.filter(part='가슴', target__contains='대흉근')
    if 'waist' in significants:
        chest_workouts = chest_workouts.exclude(etc__contains='허리')
    if 'shoulder' in significants:
        chest_workouts = chest_workouts.exclude(etc__contains='어깨')
    if 'elbow' in significants:
        chest_workouts = chest_workouts.exclude(etc__contains='팔꿈치')
    if 'knee' in significants:
        chest_workouts = chest_workouts.exclude(etc__contains='무릎')
    chest_workouts = chest_workouts.order_by('?')[:3]

    biceps_workouts = WorkoutData.objects.filter(part='팔', target__contains='이두근')
    if 'waist' in significants:
        biceps_workouts = biceps_workouts.exclude(etc__contains='허리')
    if 'shoulder' in significants:
        biceps_workouts = biceps_workouts.exclude(etc__contains='어깨')
    if 'elbow' in significants:
        biceps_workouts = biceps_workouts.exclude(etc__contains='팔꿈치')
    if 'knee' in significants:
        biceps_workouts = biceps_workouts.exclude(etc__contains='무릎')
    biceps_workouts = biceps_workouts.order_by('?')[:1]

    # 등 및 삼두 운동 선택
    back_workouts = WorkoutData.objects.filter(part='등', target__contains='광배근')
    if 'waist' in significants:
        back_workouts = back_workouts.exclude(etc__contains='허리')
    if 'shoulder' in significants:
        back_workouts = back_workouts.exclude(etc__contains='어깨')
    if 'elbow' in significants:
        back_workouts = back_workouts.exclude(etc__contains='팔꿈치')
    if 'knee' in significants:
        back_workouts = back_workouts.exclude(etc__contains='무릎')
    back_workouts = back_workouts.order_by('?')[:3]

    triceps_workouts = WorkoutData.objects.filter(part='팔', target__contains='삼두근')
    if 'waist' in significants:
        triceps_workouts = triceps_workouts.exclude(etc__contains='허리')
    if 'shoulder' in significants:
        triceps_workouts = triceps_workouts.exclude(etc__contains='어깨')
    if 'elbow' in significants:
        triceps_workouts = triceps_workouts.exclude(etc__contains='팔꿈치')
    if 'knee' in significants:
        triceps_workouts = triceps_workouts.exclude(etc__contains='무릎')
    triceps_workouts = triceps_workouts.order_by('?')[:1]

    # 어깨 및 하체 운동 선택
    shoulder_workouts = WorkoutData.objects.filter(part='어깨', target__contains='전면삼각근')
    if 'waist' in significants:
        shoulder_workouts = shoulder_workouts.exclude(etc__contains='허리')
    if 'shoulder' in significants:
        shoulder_workouts = shoulder_workouts.exclude(etc__contains='어깨')
    if 'elbow' in significants:
        shoulder_workouts = shoulder_workouts.exclude(etc__contains='팔꿈치')
    if 'knee' in significants:
        shoulder_workouts = shoulder_workouts.exclude(etc__contains='무릎')
    shoulder_workouts = shoulder_workouts.order_by('?')[:2]

    leg_workouts = WorkoutData.objects.filter(part='하체', target__contains='대퇴사두근')
    if 'waist' in significants:
        leg_workouts = leg_workouts.exclude(etc__contains='허리')
    if 'shoulder' in significants:
        leg_workouts = leg_workouts.exclude(etc__contains='어깨')
    if 'elbow' in significants:
        leg_workouts = leg_workouts.exclude(etc__contains='팔꿈치')
    if 'knee' in significants:
        leg_workouts = leg_workouts.exclude(etc__contains='무릎')
    leg_workouts = leg_workouts.order_by('?')[:2]

    day_parts = {
        '월': ['가슴', '이두'],
        '화': ['등', '삼두'],
        '수': ['어깨', '하체'],
        '목': ['가슴', '이두'],
        '금': ['등', '삼두'],
        '토': ['어깨', '하체'],
        '일': ['가슴', '이두']
    }

    # 사용자가 선택한 요일에 운동 배정
    days = {'mon': '월', 'tue': '화', 'wed': '수', 'thu': '목', 'fri': '금', 'sat': '토', 'sun': '일'}
    selected_days = [days[day] for day in ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun'] if
                     f'exercise_selected_{day}' in significants]

    unselected_days = [day for day in ['월', '화', '수', '목', '금', '토', '일'] if day not in selected_days]
    for day in unselected_days:
        day_workouts[day].append('오늘은 운동 쉬는 날!')

    if not selected_days:
        selected_days = ['월', '화', '수', '목', '금', '토']

    for day in selected_days:
        parts = day_parts[day]
        for part in parts:
            if part == '가슴':
                day_workouts[day].extend(chest_workouts.values_list('name', flat=True))
            elif part == '이두':
                day_workouts[day].extend(biceps_workouts.values_list('name', flat=True))
            elif part == '등':
                day_workouts[day].extend(back_workouts.values_list('name', flat=True))
            elif part == '삼두':
                day_workouts[day].extend(triceps_workouts.values_list('name', flat=True))
            elif part == '어깨':
                day_workouts[day].extend(shoulder_workouts.values_list('name', flat=True))
            elif part == '하체':
                day_workouts[day].extend(leg_workouts.values_list('name', flat=True))

    print(selected_days)
    print(day_workouts)
    return day_workouts


def result_view(request):
    current_username = request.user.username
    user_bia = UserBia.objects.filter(username=current_username).order_by('-bia_num').first()

    if user_bia:
        significants = user_bia.significants
        recommend_exercise = 'recommendexercise_yse' in significants
        waist_issue = 'waist' in significants
        elbow_issue = 'elbow' in significants
        knee_issue = 'knee' in significants
        shoulder_issue = 'shoulder' in significants
        is_issue = waist_issue or elbow_issue or knee_issue or shoulder_issue   
        recommend_diet = 'recommenddiet_yes' in significants
        
        if recommend_exercise:
            # 저장된 운동 목록이 있으면 불러옴, 없으면 새로 생성
            if SelectedWorkout.objects.filter(user=request.user).exists():
                userid = request.user.id
                selected_workouts = SelectedWorkout.objects.filter(user=userid).order_by('-id').first()
                print(f"Workout: {selected_workouts.workout_name}, Logged at: {selected_workouts.timelog}")
                current_time = timezone.localtime()
                time_difference = current_time - selected_workouts.timelog
                print(f"{time_difference}")
                diff_minute = time_difference.seconds //60 # 분단위로 변경
                print(f"{diff_minute}")
                
                #운동리스트가 저장된지 2분이 지난 경우 다시생성(발표때 너무 길다고 판단되면 시간 변경)
                if diff_minute < 2:
                    day_workouts = get_saved_workouts(request.user)
                else:
                    day_workouts = select_workouts(significants)
                    save_selected_workouts(request.user, day_workouts)

            else:
                day_workouts = select_workouts(significants)
                save_selected_workouts(request.user, day_workouts)
        else:
            pass
        if recommend_diet:
            final_user_bmr = calculrate_kcal(request.user, significants)

            #식단 생성(미완)
            # select_diet(request.user ,significants, final_user_bmr)
            pass
        else:
            pass
    else:
        day_workouts = {}

    # 운동 데이터에 설명 추가
    workout_data = {}
    for day, workout_list in day_workouts.items():
        workout_data[day] = []
        for workout in workout_list:
            workout_name = workout  # workout은 문자열
            if workout_name == '일요일은 쉬는 날!':
                workout_data[day].append({'name': workout_name, 'caption': ''})
            else:
                workout_obj = WorkoutData.objects.filter(name=workout_name).first()
                if workout_obj:
                    workout_data[day].append({'name': workout_obj.name, 'caption': workout_obj.caption})
                else:
                    workout_data[day].append({'name': workout_name, 'caption': '설명이 없습니다.'})

    context = {
        'user_id': current_username,
        'status': user_bia.status if user_bia else '상태 정보 없음',
        'day_workouts': workout_data,
        'is_issue': is_issue
    }

    return render(request, 'result.html', context)

# 정현욱 분석결과 db에 저장

#db에 운동을 저장하는 함수
def save_selected_workouts(user, selected_workouts):
    SelectedWorkout.objects.filter(user=user).delete()
    
    for day, workouts in selected_workouts.items():
        for workout in workouts:
            selected_workout = SelectedWorkout(
                user=user,
                workout_name=workout,
                day=day
            )
            selected_workout.save()

#db에 저장된 운동들을 가져오는 함수
def get_saved_workouts(user):
    selected_workouts = SelectedWorkout.objects.filter(user=user)
    day_workouts = {day: [] for day in ['월', '화', '수', '목', '금', '토', '일']}
    
    for workout in selected_workouts:
        day_workouts[workout.day].append(workout.workout_name)
    
    return day_workouts

#기초대사량+활동대사량 계산 함수(단위: kcal)
def calculrate_kcal(user,significants):
    current_username = user.username
    user_bia = UserBia.objects.filter(username=current_username).order_by('-bia_num').first()

    days = {'mon': '월', 'tue': '화', 'wed': '수', 'thu': '목', 'fri': '금', 'sat': '토', 'sun': '일'}
    exercise_selected_days = [days[day] for day in ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun'] if
                     f'exercise_selected_{day}' in significants]
    exercise_selected_days_number = len(exercise_selected_days)
    print(exercise_selected_days_number)
    
    #기초대사량 + 활동대사량
    if exercise_selected_days_number == 0:
        user_bmr = user_bia.bmr * 1.2
    elif exercise_selected_days_number < 3:
        user_bmr = user_bia.bmr * 1.375
    elif 3 <= exercise_selected_days_number <=5:
        user_bmr = user_bia.bmr * 1.555
    elif 6 <= exercise_selected_days_number <=7 and "inactive_occupation" in significants:
        user_bmr = user_bia.bmr * 1.725
    elif 6 <= exercise_selected_days_number <= 7 and "active_occupation" in significants:
        user_bmr = user_bia.bmr * 1.9
    else:
        pass

    #목표까지 고려한 bmr
    if "target_diet" in significants:
        total_user_bmr = user_bmr * 0.8
    elif "target_keep" in significants:
        total_user_bmr = user_bmr
    elif "target_bulkup" in significants:
        total_user_bmr = user_bmr * 1.2
    else:
        total_user_bmr = user_bmr
    
    #간식 추천시 bmr
    if "recommendsnack_yes" in significants:
        final_user_bmr = total_user_bmr - 200
    elif "recommendsnack_no" in significants:
        final_user_bmr = total_user_bmr
    else:
        final_user_bmr = total_user_bmr
    
    final_user_bmr = int(final_user_bmr)
    print(f"최종 칼로리: {final_user_bmr}")
    
    return final_user_bmr

#식단 생성 함수
# def select_diet(user, significants, final_user_bmr):
#     current_username = user.username
#     user_bia = UserBia.objects.filter(username=current_username).order_by('-bia_num').first()

#     #탄단지 분배(5:3:2)
#     user_carbohydrate_kcal = final_user_bmr * 0.5
#     user_protein_kcal = final_user_bmr * 0.3
#     user_province_kcal = final_user_bmr * 0.2
    
#     #탄단지 그램으로 변경
#     user_carbohydrate_gram = user_carbohydrate_kcal / 4
#     user_protein_gram = user_protein_kcal / 4
#     user_province_gram = user_province_kcal / 9
#     print(f"탄수화물(g): {user_carbohydrate_gram}")
#     print(f"단백질(g): {user_protein_gram}" )
#     print(f"지방(g): {user_province_gram}")

#     #한끼로 변경
#     one_meal_kcal = final_user_bmr/3
#     one_meal_user_protein_gram = user_protein_gram/3
#     one_meal_user_carbohydrate_gram = user_carbohydrate_gram/3

#     # 요일별 식단 선택 로직
#     day_diet = {
#         '월': [],
#         '화': [],
#         '수': [],
#         '목': [],
#         '금': [],
#         '토': [],
#         '일': []
#     }

#     meals = {'breakfast': '아침', 'lunch': '점심', 'dinner': '저녁'}
#     selected_diet_meals = [meals[meal] for meal in ['breakfast', 'lunch', 'dinner'] if
#                      f'diet_selected_{meal}' in significants]
    
#     selected_diet_meals_count= len(selected_diet_meals)

#     if selected_diet_meals_count == 0:
#         selected_diet_meals = [meals[meal] for meal in ['breakfast', 'lunch', 'dinner']]

#     # 식사에서 탄수화물
#     carbohydrate_diet = DietData.objects.filter(type='탄수화물', type2='식사')
#     if 'allergy_buckwheat' in significants:
#         carbohydrate_diet = carbohydrate_diet.exclude(etc__contains='메밀')
#     if 'allergy_wheat' in significants:
#         carbohydrate_diet = carbohydrate_diet.exclude(etc__contains='밀')
#     if 'allergy_soybean' in significants:
#         carbohydrate_diet = carbohydrate_diet.exclude(etc__contains='대두')
#     if 'allergy_peanut' in significants:
#         carbohydrate_diet = carbohydrate_diet.exclude(etc__contains='땅콩')
#     if 'allergy_walnut' in significants:
#         carbohydrate_diet = carbohydrate_diet.exclude(etc__contains='호두')
#     if 'allergy_pine_nut' in significants:
#         carbohydrate_diet = carbohydrate_diet.exclude(etc__contains='잣')
#     if 'allergy_sulfurousacids' in significants:
#         carbohydrate_diet = carbohydrate_diet.exclude(etc__contains='아황산류')
#     if 'allergy_peach' in significants:
#         carbohydrate_diet = carbohydrate_diet.exclude(etc__contains='복숭아')
#     if 'allergy_tomato' in significants:
#         carbohydrate_diet = carbohydrate_diet.exclude(etc__contains='토마토')
#     if 'allergy_eggs' in significants:
#         carbohydrate_diet = carbohydrate_diet.exclude(etc__contains='계란')
#     if 'allergy_milk' in significants:
#         carbohydrate_diet = carbohydrate_diet.exclude(etc__contains='우유')
#     if 'allergy_shrimp' in significants:
#         carbohydrate_diet = carbohydrate_diet.exclude(etc__contains='새우')
#     if 'allergy_macherel' in significants:
#         carbohydrate_diet = carbohydrate_diet.exclude(etc__contains='고등어')
#     if 'allergy_squid' in significants:
#         carbohydrate_diet = carbohydrate_diet.exclude(etc__contains='오징어')
#     if 'allergy_crab' in significants:
#         carbohydrate_diet = carbohydrate_diet.exclude(etc__contains='게')
#     if 'allergy_shellfish' in significants:
#         carbohydrate_diet = carbohydrate_diet.exclude(etc__contains='조개류')
#     if 'allergy_pork' in significants:
#         carbohydrate_diet = carbohydrate_diet.exclude(etc__contains='돼기고기')
#     if 'allergy_beef' in significants:
#         carbohydrate_diet = carbohydrate_diet.exclude(etc__contains='쇠고기')
#     if 'allergy_chicken' in significants:
#         carbohydrate_diet = carbohydrate_diet.exclude(etc__contains='닭고기')
#     carbohydrate_diet = carbohydrate_diet.order_by('?')[:selected_diet_meals_count]

#     #식사에서 단백질
#     protein_diet = DietData.objects.filter(type='단백질', type2='식사')
#     if 'allergy_buckwheat' in significants:
#         protein_diet = protein_diet.exclude(etc__contains='메밀')
#     if 'allergy_wheat' in significants:
#         protein_diet = protein_diet.exclude(etc__contains='밀')
#     if 'allergy_soybean' in significants:
#         protein_diet = protein_diet.exclude(etc__contains='대두')
#     if 'allergy_peanut' in significants:
#         protein_diet = protein_diet.exclude(etc__contains='땅콩')
#     if 'allergy_walnut' in significants:
#         protein_diet = protein_diet.exclude(etc__contains='호두')
#     if 'allergy_pine_nut' in significants:
#         protein_diet = protein_diet.exclude(etc__contains='잣')
#     if 'allergy_sulfurousacids' in significants:
#         protein_diet = protein_diet.exclude(etc__contains='아황산류')
#     if 'allergy_peach' in significants:
#         protein_diet = protein_diet.exclude(etc__contains='복숭아')
#     if 'allergy_tomato' in significants:
#         protein_diet = protein_diet.exclude(etc__contains='토마토')
#     if 'allergy_eggs' in significants:
#         protein_diet = protein_diet.exclude(etc__contains='계란')
#     if 'allergy_milk' in significants:
#         protein_diet = protein_diet.exclude(etc__contains='우유')
#     if 'allergy_shrimp' in significants:
#         protein_diet = protein_diet.exclude(etc__contains='새우')
#     if 'allergy_macherel' in significants:
#         protein_diet = protein_diet.exclude(etc__contains='고등어')
#     if 'allergy_squid' in significants:
#         protein_diet = protein_diet.exclude(etc__contains='오징어')
#     if 'allergy_crab' in significants:
#         protein_diet = protein_diet.exclude(etc__contains='게')
#     if 'allergy_shellfish' in significants:
#         protein_diet = protein_diet.exclude(etc__contains='조개류')
#     if 'allergy_pork' in significants:
#         protein_diet = protein_diet.exclude(etc__contains='돼기고기')
#     if 'allergy_beef' in significants:
#         protein_diet = protein_diet.exclude(etc__contains='쇠고기')
#     if 'allergy_chicken' in significants:
#         protein_diet = protein_diet.exclude(etc__contains='닭고기')
#     protein_diet = protein_diet.order_by('?')[:selected_diet_meals_count]

#     #식사에서 지방
#     province_diet = DietData.objects.filter(type='지방', type2='식사')
#     if 'allergy_buckwheat' in significants:
#         province_diet = province_diet.exclude(etc__contains='메밀')
#     if 'allergy_wheat' in significants:
#         province_diet = province_diet.exclude(etc__contains='밀')
#     if 'allergy_soybean' in significants:
#         province_diet = province_diet.exclude(etc__contains='대두')
#     if 'allergy_peanut' in significants:
#         province_diet = province_diet.exclude(etc__contains='땅콩')
#     if 'allergy_walnut' in significants:
#         province_diet = province_diet.exclude(etc__contains='호두')
#     if 'allergy_pine_nut' in significants:
#         province_diet = province_diet.exclude(etc__contains='잣')
#     if 'allergy_sulfurousacids' in significants:
#         province_diet = province_diet.exclude(etc__contains='아황산류')
#     if 'allergy_peach' in significants:
#         province_diet = province_diet.exclude(etc__contains='복숭아')
#     if 'allergy_tomato' in significants:
#         province_diet = province_diet.exclude(etc__contains='토마토')
#     if 'allergy_eggs' in significants:
#         province_diet = province_diet.exclude(etc__contains='계란')
#     if 'allergy_milk' in significants:
#         province_diet = province_diet.exclude(etc__contains='우유')
#     if 'allergy_shrimp' in significants:
#         province_diet = province_diet.exclude(etc__contains='새우')
#     if 'allergy_macherel' in significants:
#         province_diet = province_diet.exclude(etc__contains='고등어')
#     if 'allergy_squid' in significants:
#         province_diet = province_diet.exclude(etc__contains='오징어')
#     if 'allergy_crab' in significants:
#         province_diet = province_diet.exclude(etc__contains='게')
#     if 'allergy_shellfish' in significants:
#         province_diet = province_diet.exclude(etc__contains='조개류')
#     if 'allergy_pork' in significants:
#         province_diet = province_diet.exclude(etc__contains='돼기고기')
#     if 'allergy_beef' in significants:
#         province_diet = province_diet.exclude(etc__contains='쇠고기')
#     if 'allergy_chicken' in significants:
#         province_diet = province_diet.exclude(etc__contains='닭고기')
#     province_diet = province_diet.order_by('?')[:selected_diet_meals_count]

#     day_type = {
#             '월': ['가슴', '이두'],
#             '화': ['등', '삼두'],
#             '수': ['어깨', '하체'],
#             '목': ['가슴', '이두'],
#             '금': ['등', '삼두'],
#             '토': ['어깨', '하체'],
#             '일': ['가슴', '이두']
#         }