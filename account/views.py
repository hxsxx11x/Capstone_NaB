from django.contrib import auth, messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from main.models import UserBia, WorkoutData, DietMenu
from .models import CustomUser, CustomUserManager, SelectedWorkout
from .forms import UserForm, UserUpdateForm
from django.contrib.auth.decorators import login_required
from .models import SelectedWorkout, SelectedDiet
from django.utils import timezone
from datetime import datetime

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
        
        today = datetime.today()

        # 요일을 숫자로 가져오기 (0=월요일, 1=화요일, ...)
        day_of_week = today.weekday()

        # 요일을 한글로 매핑
        days_in_korean = ['월', '화', '수', '목', '금', '토', '일']

        # 오늘의 요일 출력
        print("현재 요일:", days_in_korean[day_of_week])
        current_day = days_in_korean[day_of_week]
        
        if SelectedDiet.objects.filter(user=request.user).exists():
            diets = get_saved_diets(request.user)
            print(f"{diets}")
            current_meal_plan = diets[current_day]

            context = {'user': account,'today_diets':current_meal_plan,}
            return render(request, 'dietmenu.html', context)

        else:
            context = {'user': account,}
        return render(request, 'dietmenu.html', context)
    else:
        # 인증되지 않은 사용자는 로그인 페이지로 리디렉션
        return redirect('/')

def biagraph_view(request):
    if request.user.is_authenticated:
        username = request.user.username
        account = CustomUser.objects.get(username=username)
        entries = UserBia.objects.filter(username=username).order_by('date')
        dates = [entry.date.strftime("%Y-%m-%d") for entry in entries]
        weights = [entry.weight for entry in entries]
        bmi = [entry.bmi for entry in entries]
        skeletal = [entry.skeletal for entry in entries]
        fat_per = [entry.fat_per for entry in entries]

        return render(request, 'biagraph.html', {'user': account, 'dates': dates, 'weights': weights, 'bmi': bmi,'skeletal':skeletal, 'fat_per':fat_per})
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


def show_today_workouts(request):
    today = datetime.today().strftime('%A')  # 오늘의 요일을 영어로 가져오기
    day_mapping = {'Monday': '월', 'Tuesday': '화', 'Wednesday': '수', 'Thursday': '목', 'Friday': '금', 'Saturday': '토',
                   'Sunday': '일'}
    current_day = day_mapping[today]  # 영어 요일을 한글로 변환

    # 현재 사용자의 오늘 요일에 해당하는 운동 가져오기
    selected_workouts = SelectedWorkout.objects.filter(user=request.user, day=current_day)

    workout_data = []
    for workout in selected_workouts:
        workout_info = WorkoutData.objects.filter(name=workout.workout_name).first()
        if workout_info:
            workout_data.append({
                'name': workout.workout_name,
                'caption': workout_info.caption,
            })

    context = {
        'workout_data': workout_data,
        'today': current_day,
    }
    return render(request, 'workoutmenu.html', context)

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
            if SelectedDiet.objects.filter(user=request.user).exists():
                userid = request.user.id
                selected_diets = SelectedDiet.objects.filter(user=userid).order_by('-diet_id').first()
                print(f"Diet: {selected_diets.diet_name}, Logged at: {selected_diets.timelog}")
                current_time = timezone.localtime()
                time_difference = current_time - selected_diets.timelog
                print(f"{time_difference}")
                diff_minute = time_difference.seconds //60 # 분단위로 변경
                print(f"{diff_minute}")
                
                if diff_minute < 2:
                    global day_diets
                    global global_final_user_bmr
                    day_diets = get_saved_diets(request.user)
                    global_final_user_bmr = calculrate_kcal(request.user, significants)
                else:
                    global_final_user_bmr = calculrate_kcal(request.user, significants)
                    #식단 생성
                    day_diets = select_diet(request.user ,significants, global_final_user_bmr)
                    save_selected_diets(request.user, day_diets)
            else:
                global_final_user_bmr = calculrate_kcal(request.user, significants)
                #식단 생성
                day_diets = select_diet(request.user ,significants, global_final_user_bmr)
                save_selected_diets(request.user, day_diets)
        else:
            pass
    else:
        day_workouts = {}

    if recommend_exercise and recommend_diet:
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

        meal_times = ["아침", "점심", "저녁", "간식"]  # 리스트로 변환
        
        context = {
        'user_id': current_username,
        'status': user_bia.status if user_bia else '상태 정보 없음',
        'day_workouts': workout_data,
        'day_diets':day_diets,
        'user_bmr':global_final_user_bmr,
        'meal_times': meal_times,
        'is_issue': is_issue,
    }
        return render(request, 'result.html', context)
    
    elif recommend_diet:
        meal_times = ["아침", "점심", "저녁", "간식"]  # 리스트로 변환
        context = {
        'user_id': current_username,
        'status': user_bia.status if user_bia else '상태 정보 없음',
        'is_issue': is_issue,
        'day_diets':day_diets,
        'user_bmr':global_final_user_bmr,
        'meal_times': meal_times,
        }
        return render(request, 'result.html', context)
    
    elif recommend_exercise:
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
            'is_issue': is_issue,
        }
        return render(request, 'result.html', context)


    else:
        context = {
        'user_id': current_username,
        'status': user_bia.status if user_bia else '상태 정보 없음',
        'is_issue': is_issue,
        }
        return render(request, 'result.html', context)

    return render(request, 'result.html')

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

def save_selected_diets(user, day_diet):
     for day, meals in day_diet.items():
        for meal_time, diet_list in meals.items():
            # 각 식사 시간대의 추천 식단을 하나의 문자열로 변환 (콤마로 구분)
            diet_name = ', '.join(diet_list) if diet_list else '식단 추천 없음'
            
            # SelectedDiet 모델에 저장
            selected_diet = SelectedDiet(
                user=user,
                diet_name=diet_name,
                day=day,              
                meal=meal_time,       
            )
            selected_diet.save()

def get_saved_diets(user):
    selected_diets = SelectedDiet.objects.filter(user=user)
    day_diet = {}
    
    # DB에서 불러온 데이터를 day_diet 형식으로 변환
    for diet in selected_diets:
        day = diet.day
        meal_time = diet.meal
        diet_name = diet.diet_name

        if day not in day_diet:
            day_diet[day] = {}
        
        # 각 요일의 식사 시간에 대해 식단 저장
        day_diet[day][meal_time] = diet_name.split(', ')  # 식단은 리스트로 변환하여 저장
    return day_diet

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
    elif exercise_selected_days_number <=5:
        user_bmr = user_bia.bmr * 1.555
    elif exercise_selected_days_number <= 7 and "inactive_occupation" in significants:
        user_bmr = user_bia.bmr * 1.725
    elif exercise_selected_days_number <= 7 and "active_occupation" in significants:
        user_bmr = user_bia.bmr * 1.9
    else:
        user_bmr = user_bia.bmr

    #목표까지 고려한 bmr
    if "target_diet" in significants:
        total_user_bmr = user_bmr * 0.8
    elif "target_keep" in significants:
        total_user_bmr = user_bmr
    elif "target_bulkup" in significants:
        total_user_bmr = user_bmr * 1.2
    else:
        total_user_bmr = user_bmr
    
    final_user_bmr = int(total_user_bmr)
    print(f"최종 칼로리: {final_user_bmr}")
    
    return final_user_bmr

#식단 생성 함수
def select_diet(user, significants, _final_user_bmr):
    
    current_username = user.username
    user_bia = UserBia.objects.filter(username=current_username).order_by('-bia_num').first()

    #간식 추천시 bmr
    if "recommendsnack_yes" in significants:
        final_user_bmr = _final_user_bmr - 200
    elif "recommendsnack_no" in significants:
        final_user_bmr = _final_user_bmr
    else:
        final_user_bmr = _final_user_bmr

    #탄단지 분배(5:3:2)
    user_carbohydrate_kcal = final_user_bmr * 0.5
    user_protein_kcal = final_user_bmr * 0.3
    user_province_kcal = final_user_bmr * 0.2
    
    #탄단지 그램으로 변경
    user_carbohydrate_gram = user_carbohydrate_kcal / 4
    user_protein_gram = user_protein_kcal / 4
    user_province_gram = user_province_kcal / 9

    print(f"탄수화물(g): {user_carbohydrate_gram}")
    print(f"단백질(g): {user_protein_gram}" )
    print(f"지방(g): {user_province_gram}")

    #한끼로 변경
    one_meal_kcal = final_user_bmr/3
    one_meal_user_protein_gram = user_protein_gram/3
    one_meal_user_carbohydrate_gram = user_carbohydrate_gram/3
    one_meal_user_province_gram = user_province_gram/3

    # 요일별 식단 선택 로직
    day_diet = {
        '월': [],
        '화': [],
        '수': [],
        '목': [],
        '금': [],
        '토': [],
        '일': []
    }

    meals = {'breakfast': '아침', 'lunch': '점심', 'dinner': '저녁'}
    selected_diet_meals = [meals[meal] for meal in ['breakfast', 'lunch', 'dinner'] if
                     f'diet_selected_{meal}' in significants]
   
    print(f"{selected_diet_meals}")
   
    selected_diet_meals_count= len(selected_diet_meals)

    unselected_diet_meals = [meal for meal in ['아침','점심','저녁'] if meal not in selected_diet_meals]

    print(f"{unselected_diet_meals}")
   
    if selected_diet_meals_count == 0:
        selected_diet_meals = [meals[meal] for meal in ['breakfast', 'lunch', 'dinner']]
        unselected_diet_meals = None

    # 식사에서 탄수화물
    carbohydrate_diet = DietMenu.objects.filter(type1 = '탄수화물', type2 = '식사')
    print(f"list_cabohydrate_diet: {carbohydrate_diet}")
    if 'allergy_buckwheat' in significants:
        carbohydrate_diet = carbohydrate_diet.exclude(etc__contains='메밀')
    if 'allergy_wheat' in significants:
        carbohydrate_diet = carbohydrate_diet.exclude(etc__contains='밀')
    if 'allergy_soybean' in significants:
        carbohydrate_diet = carbohydrate_diet.exclude(etc__contains='대두')
    if 'allergy_peanut' in significants:
        carbohydrate_diet = carbohydrate_diet.exclude(etc__contains='땅콩')
    if 'allergy_walnut' in significants:
        carbohydrate_diet = carbohydrate_diet.exclude(etc__contains='호두')
    if 'allergy_pine_nut' in significants:
        carbohydrate_diet = carbohydrate_diet.exclude(etc__contains='잣')
    if 'allergy_sulfurousacids' in significants:
        carbohydrate_diet = carbohydrate_diet.exclude(etc__contains='아황산류')
    if 'allergy_peach' in significants:
        carbohydrate_diet = carbohydrate_diet.exclude(etc__contains='복숭아')
    if 'allergy_tomato' in significants:
        carbohydrate_diet = carbohydrate_diet.exclude(etc__contains='토마토')
    if 'allergy_eggs' in significants:
        carbohydrate_diet = carbohydrate_diet.exclude(etc__contains='계란')
    if 'allergy_milk' in significants:
        carbohydrate_diet = carbohydrate_diet.exclude(etc__contains='우유')
    if 'allergy_shrimp' in significants:
        carbohydrate_diet = carbohydrate_diet.exclude(etc__contains='새우')
    if 'allergy_macherel' in significants:
        carbohydrate_diet = carbohydrate_diet.exclude(etc__contains='고등어')
    if 'allergy_squid' in significants:
        carbohydrate_diet = carbohydrate_diet.exclude(etc__contains='오징어')
    if 'allergy_crab' in significants:
        carbohydrate_diet = carbohydrate_diet.exclude(etc__contains='게')
    if 'allergy_shellfish' in significants:
        carbohydrate_diet = carbohydrate_diet.exclude(etc__contains='조개류')
    if 'allergy_pork' in significants:
        carbohydrate_diet = carbohydrate_diet.exclude(etc__contains='돼기고기')
    if 'allergy_beef' in significants:
        carbohydrate_diet = carbohydrate_diet.exclude(etc__contains='쇠고기')
    if 'allergy_chicken' in significants:
        carbohydrate_diet = carbohydrate_diet.exclude(etc__contains='닭고기')
    carbohydrate_diet = carbohydrate_diet.order_by('?')[:1]
    print(f"result_carbohydrate_diet: {carbohydrate_diet}")

    #식사에서 단백질
    protein_diet = DietMenu.objects.filter(type1='단백질', type2='식사')
    print(f"list_protein_diet: {protein_diet}")

    if 'allergy_buckwheat' in significants:
        protein_diet = protein_diet.exclude(etc__icontains='메밀')
    if 'allergy_wheat' in significants:
        protein_diet = protein_diet.exclude(etc__contains='밀')
    if 'allergy_soybean' in significants:
        protein_diet = protein_diet.exclude(etc__contains='대두')       
    if 'allergy_peanut' in significants:
        protein_diet = protein_diet.exclude(etc__contains='땅콩')
    if 'allergy_walnut' in significants:
        protein_diet = protein_diet.exclude(etc__contains='호두')
    if 'allergy_pine_nut' in significants:
        protein_diet = protein_diet.exclude(etc__contains='잣')
    if 'allergy_sulfurousacids' in significants:
        protein_diet = protein_diet.exclude(etc__contains='아황산류')
    if 'allergy_peach' in significants:
        protein_diet = protein_diet.exclude(etc__contains='복숭아')
    if 'allergy_tomato' in significants:
        protein_diet = protein_diet.exclude(etc__contains='토마토')
    if 'allergy_eggs' in significants:
        protein_diet = protein_diet.exclude(etc__contains='계란')
    if 'allergy_milk' in significants:
        protein_diet = protein_diet.exclude(etc__contains='우유')
    if 'allergy_shrimp' in significants:
        protein_diet = protein_diet.exclude(etc__contains='새우')
    if 'allergy_macherel' in significants:
        protein_diet = protein_diet.exclude(etc__contains='고등어')
    if 'allergy_squid' in significants:
        protein_diet = protein_diet.exclude(etc__contains='오징어')
    if 'allergy_crab' in significants:
        protein_diet = protein_diet.exclude(etc__contains='게')
    if 'allergy_shellfish' in significants:
        protein_diet = protein_diet.exclude(etc__contains='조개류')
    if 'allergy_pork' in significants:
        protein_diet = protein_diet.exclude(etc__contains='돼기고기')
    if 'allergy_beef' in significants:
        protein_diet = protein_diet.exclude(etc__contains='쇠고기')
    if 'allergy_chicken' in significants:
        protein_diet = protein_diet.exclude(etc__contains='닭고기')
    protein_diet = protein_diet.order_by('?')[:1]
    print(f"result_protein_diet: {protein_diet}")

    #식사에서 반찬
    province_diet = DietMenu.objects.filter(type1='반찬', type2='식사')
    print(f"list_province_diet: {province_diet}")

    if 'allergy_buckwheat' in significants:
        province_diet = province_diet.exclude(etc__contains='메밀')
    if 'allergy_wheat' in significants:
        province_diet = province_diet.exclude(etc__contains='밀')
    if 'allergy_soybean' in significants:
        province_diet = province_diet.exclude(etc__contains='대두')
    if 'allergy_peanut' in significants:
        province_diet = province_diet.exclude(etc__contains='땅콩')
    if 'allergy_walnut' in significants:
        province_diet = province_diet.exclude(etc__contains='호두')
    if 'allergy_pine_nut' in significants:
        province_diet = province_diet.exclude(etc__contains='잣')
    if 'allergy_sulfurousacids' in significants:
        province_diet = province_diet.exclude(etc__contains='아황산류')
    if 'allergy_peach' in significants:
        province_diet = province_diet.exclude(etc__contains='복숭아')
    if 'allergy_tomato' in significants:
        province_diet = province_diet.exclude(etc__contains='토마토')
    if 'allergy_eggs' in significants:
        province_diet = province_diet.exclude(etc__contains='계란')
    if 'allergy_milk' in significants:
        province_diet = province_diet.exclude(etc__contains='우유')
    if 'allergy_shrimp' in significants:
        province_diet = province_diet.exclude(etc__contains='새우')
    if 'allergy_macherel' in significants:
        province_diet = province_diet.exclude(etc__contains='고등어')
    if 'allergy_squid' in significants:
        province_diet = province_diet.exclude(etc__contains='오징어')
    if 'allergy_crab' in significants:
        province_diet = province_diet.exclude(etc__contains='게')
    if 'allergy_shellfish' in significants:
        province_diet = province_diet.exclude(etc__contains='조개류')
    if 'allergy_pork' in significants:
        province_diet = province_diet.exclude(etc__contains='돼기고기')
    if 'allergy_beef' in significants:
        province_diet = province_diet.exclude(etc__contains='쇠고기')
    if 'allergy_chicken' in significants:
        province_diet = province_diet.exclude(etc__contains='닭고기')
    province_diet = province_diet.order_by('?')[:1]
    print(f"result_province_diet: {province_diet}")

    all_diet = DietMenu.objects.filter(type1='ALL', type2='식사')
    print(f"all_diet__list: {all_diet}")
    if 'allergy_buckwheat' in significants:
        all_diet = all_diet.exclude(etc__contains='메밀')
    if 'allergy_wheat' in significants:
        all_diet = all_diet.exclude(etc__contains='밀')
    if 'allergy_soybean' in significants:
        all_diet = all_diet.exclude(etc__contains='대두')
    if 'allergy_peanut' in significants:
        all_diet = all_diet.exclude(etc__contains='땅콩')
    if 'allergy_walnut' in significants:
        all_diet = all_diet.exclude(etc__contains='호두')
    if 'allergy_pine_nut' in significants:
        all_diet = all_diet.exclude(etc__contains='잣')
    if 'allergy_sulfurousacids' in significants:
        all_diet = all_diet.exclude(etc__contains='아황산류')
    if 'allergy_peach' in significants:
        all_diet = all_diet.exclude(etc__contains='복숭아')
    if 'allergy_tomato' in significants:
        all_diet = all_diet.exclude(etc__contains='토마토')
    if 'allergy_eggs' in significants:
        all_diet = all_diet.exclude(etc__contains='계란')
    if 'allergy_milk' in significants:
        all_diet = all_diet.exclude(etc__contains='우유')
    if 'allergy_shrimp' in significants:
        all_diet = all_diet.exclude(etc__contains='새우')
    if 'allergy_macherel' in significants:
        all_diet = all_diet.exclude(etc__contains='고등어')
    if 'allergy_squid' in significants:
        all_diet = all_diet.exclude(etc__contains='오징어')
    if 'allergy_crab' in significants:
        all_diet = all_diet.exclude(etc__contains='게')
    if 'allergy_shellfish' in significants:
        all_diet = all_diet.exclude(etc__contains='조개류')
    if 'allergy_pork' in significants:
        all_diet = all_diet.exclude(etc__contains='돼기고기')
    if 'allergy_beef' in significants:
        all_diet = all_diet.exclude(etc__contains='쇠고기')
    if 'allergy_chicken' in significants:
        all_diet = all_diet.exclude(etc__contains='닭고기')
    all_diet = all_diet.order_by('?')[:1]
    print(f"all_diet__result: {all_diet}")

    kimchi = DietMenu.objects.filter(type1='김치', type2='식사')
    print(f"all_diet__list: {kimchi}")
    kimchi = kimchi.order_by('?')[:1]
    print(f"all_diet__result: {kimchi}")


    if 'recommendsnack_yes' in significants:
        snack = DietMenu.objects.filter(type2='간식')
        print(f"snack__list: {snack}")

        if 'allergy_buckwheat' in significants:
            snack = snack.exclude(etc__contains='메밀')
        if 'allergy_wheat' in significants:
            snack = snack.exclude(etc__contains='밀')
        if 'allergy_soybean' in significants:
            snack = snack.exclude(etc__contains='대두')
        if 'allergy_peanut' in significants:
            snack = snack.exclude(etc__contains='땅콩')
        if 'allergy_walnut' in significants:
            snack = snack.exclude(etc__contains='호두')
        if 'allergy_pine_nut' in significants:
            snack = snack.exclude(etc__contains='잣')
        if 'allergy_sulfurousacids' in significants:
            snack = snack.exclude(etc__contains='아황산류')
        if 'allergy_peach' in significants:
            snack = snack.exclude(etc__contains='복숭아')
        if 'allergy_tomato' in significants:
            snack = snack.exclude(etc__contains='토마토')
        if 'allergy_eggs' in significants:
            snack = snack.exclude(etc__contains='계란')
        if 'allergy_milk' in significants:
            snack = snack.exclude(etc__contains='우유')
        if 'allergy_shrimp' in significants:
            snack = snack.exclude(etc__contains='새우')
        if 'allergy_macherel' in significants:
            snack = snack.exclude(etc__contains='고등어')
        if 'allergy_squid' in significants:
            snack = snack.exclude(etc__contains='오징어')
        if 'allergy_crab' in significants:
            snack = snack.exclude(etc__contains='게')
        if 'allergy_shellfish' in significants:
            snack = snack.exclude(etc__contains='조개류')
        if 'allergy_pork' in significants:
            snack = snack.exclude(etc__contains='돼기고기')
        if 'allergy_beef' in significants:
            snack = snack.exclude(etc__contains='쇠고기')
        if 'allergy_chicken' in significants:
            snack = snack.exclude(etc__contains='닭고기')
        snack = snack.order_by('?')[:1]
        print(f"result_snack: {snack}")
    elif 'recommendsnack_no' in significants:
        snack = None


    # '반찬' '김치' => '반찬', '김치' 로 수정
    if all_diet:
        day_type = {
            '월': {
                '아침': ['ALL'],
                '점심': ['탄수화물', '단백질', '반찬', '김치'],
                '저녁': ['탄수화물', '단백질', '반찬', '김치'],
                '간식': ['간식']
            },
            '화': {
                '아침': ['ALL'],
                '점심': ['탄수화물', '단백질', '반찬', '김치'],
                '저녁': ['탄수화물', '단백질', '반찬', '김치'],
                '간식': ['간식']
            },
            '수': {
                '아침': ['ALL'],
                '점심': ['탄수화물', '단백질', '반찬', '김치'],
                '저녁': ['탄수화물', '단백질', '반찬', '김치'],
                '간식': ['간식']
            },
            '목': {
                '아침': ['ALL'],
                '점심': ['탄수화물', '단백질', '반찬', '김치'],
                '저녁': ['탄수화물', '단백질', '반찬', '김치'],
                '간식': ['간식']
            },
            '금': {
                '아침': ['ALL'],
                '점심': ['탄수화물', '단백질', '반찬', '김치'],
                '저녁': ['탄수화물', '단백질', '반찬', '김치'],
                '간식': ['간식']
            },
            '토': {
                '아침': ['ALL'],
                '점심': ['탄수화물', '단백질', '반찬', '김치'],
                '저녁': ['탄수화물', '단백질', '반찬', '김치'],
                '간식': ['간식']
            },
            '일': {
                '아침': ['ALL'],
                '점심': ['탄수화물', '단백질', '반찬', '김치'],
                '저녁': ['탄수화물', '단백질', '반찬', '김치'],
                '간식': ['간식']
            }
        }
    else:
        day_type = {
            '월': {
                '아침': ['탄수화물', '단백질', '김치'],
                '점심': ['탄수화물', '단백질', '반찬', '김치'],
                '저녁': ['탄수화물', '단백질', '반찬', '김치'],
                '간식': ['간식']
            },
            '화': {
                '아침': ['탄수화물', '단백질', '김치'],
                '점심': ['탄수화물', '단백질', '반찬', '김치'],
                '저녁': ['탄수화물', '단백질', '반찬', '김치'],
                '간식': ['간식']
            },
            '수': {
                '아침': ['탄수화물', '단백질', '김치'],
                '점심': ['탄수화물', '단백질', '반찬', '김치'],
                '저녁': ['탄수화물', '단백질', '반찬', '김치'],
                '간식': ['간식']
            },
            '목': {
                '아침': ['탄수화물', '단백질', '김치'],
                '점심': ['탄수화물', '단백질', '반찬', '김치'],
                '저녁': ['탄수화물', '단백질', '반찬', '김치'],
                '간식': ['간식']
            },
            '금': {
                '아침': ['탄수화물', '단백질', '김치'],
                '점심': ['탄수화물', '단백질', '반찬', '김치'],
                '저녁': ['탄수화물', '단백질', '반찬', '김치'],
                '간식': ['간식']
            },
            '토': {
                '아침': ['탄수화물', '단백질', '김치'],
                '점심': ['탄수화물', '단백질', '반찬', '김치'],
                '저녁': ['탄수화물', '단백질', '반찬', '김치'],
                '간식': ['간식']
            },
            '일': {
                '아침': ['탄수화물', '단백질', '김치'],
                '점심': ['탄수화물', '단백질', '반찬', '김치'],
                '저녁': ['탄수화물', '단백질', '반찬', '김치'],
                '간식': ['간식']
            }
        }

    # 사용자가 선택한 요일에 식단 배정
    days = {'mon': '월', 'tue': '화', 'wed': '수', 'thu': '목', 'fri': '금', 'sat': '토', 'sun': '일'}

    selected_days = [days[day] for day in ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun'] if f'diet_selected_{day}' in significants]
    unselected_days = [day for day in ['월', '화', '수', '목', '금', '토', '일'] if day not in selected_days]

    if not selected_days:
        selected_days = ['월', '화', '수', '목', '금', '토']
        unselected_days = ['일']

    # 선택되지 않은 요일에 대한 기본 처리: 모든 식사 시간대에 대해 '식단 추천 없음'을 넣음
    for day in unselected_days:
        day_diet[day] = {}
        for meal_time in ['아침', '점심', '저녁','간식']:
            day_diet[day][meal_time] = ['식단 추천 없음']

    # 선택된 요일에 대해 식사 시간별로 식단 추천 추가
    for day in selected_days:
        day_diet[day] = {}
        for meal_time, types in day_type[day].items():
            print(f"meal_time: {meal_time}")
            day_diet[day][meal_time] = []  # 각 시간대에 대해 빈 리스트 초기화
            if meal_time.strip() in [m.strip() for m in selected_diet_meals]:
                for _type in types:
                    if _type == '탄수화물':
                        day_diet[day][meal_time].extend(carbohydrate_diet.values_list('name', flat=True))
                    elif _type == '단백질':
                        day_diet[day][meal_time].extend(protein_diet.values_list('name', flat=True))
                    elif _type == '반찬':
                        day_diet[day][meal_time].extend(province_diet.values_list('name', flat=True))
                    elif _type == 'ALL':
                        day_diet[day][meal_time].extend(all_diet.values_list('name', flat=True))
                    elif _type == '김치':
                        day_diet[day][meal_time].extend(kimchi.values_list('name', flat=True))
                    elif _type == '간식':
                        if snack==None:
                            day_diet[day][meal_time] = ['식단 추천 없음']
                        else:
                            day_diet[day][meal_time].extend(snack.values_list('name', flat=True))
                    else:
                        day_diet[day][meal_time] = ['식단 추천 없음']
            elif meal_time.strip() in [m.strip() for m in unselected_diet_meals]:
                 for _type in types:
                    day_diet[day][meal_time] = ['식단 추천 없음']
            else:
                day_diet[day][meal_time] = ['식단 추천 없음']


    # 결과 출력
    print(f"selected_days: {selected_days}")
    for day, meals in day_diet.items():
        print(f"요일: {day}")
        for meal_time, diet in meals.items():
            print(f"  {meal_time}: {', '.join(diet) if diet else '추천 없음'}")

    return day_diet
