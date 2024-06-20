from django.shortcuts import render, redirect
from .forms import HealthSignificantsForm
from datetime import datetime
from main.models import UserBia
from django.contrib.auth.decorators import login_required

# Create your views here.

def significants(request):
    if request.method == 'POST':
        form = HealthSignificantsForm(request.POST)
        if form.is_valid():
            checked_significants = []

            if 'target' in request.POST:
                checked_significants.append(request.POST['target'])
            if 'recommendexercise' in request.POST:
                checked_significants.append(request.POST['recommendexercise'])
            if 'selected_recommendexercise' in request.POST:
                checked_significants.extend(request.POST.getlist('selected_recommendexercise'))
            if 'muscle' in request.POST:
                checked_significants.append(request.POST['muscle'])
            if 'cardio' in request.POST:
                checked_significants.append(request.POST['cardio'])
            if 'time' in request.POST:
                checked_significants.append(request.POST['time'])
            if 'health_significants' in request.POST:
                checked_significants.extend(request.POST.getlist('health_significants'))
            if 'recommenddiet' in request.POST:
                checked_significants.append(request.POST['recommenddiet'])
            if 'allergy' in request.POST:
                checked_significants.extend(request.POST.getlist('allergy'))
            if 'selected_recommenddiet' in request.POST:
                checked_significants.extend(request.POST.getlist('selected_recommenddiet'))
            if 'selected_meal' in request.POST:
                checked_significants.extend(request.POST.getlist('selected_meal'))
            if 'recommendsnack' in request.POST:
                checked_significants.append(request.POST['recommendsnack'])
            if 'selected_snack' in request.POST:
                checked_significants.extend(request.POST.getlist('selected_snack'))

            print("Checked Significants:",checked_significants)  # 디버깅 출력
            current_username = request.user.username
            bia = UserBia.objects.filter(username=current_username).order_by('-bia_num').first()

            '''
            bia.significants = ', '.join(checked_significants)
            bia.save()
            '''
            bia_data = request.session.get('bia_data', {})
            user_bia = UserBia(
                date=datetime.now(),
                username=request.user.username,
                age=25,
                height=bia_data.get('height', 0),
                weight=bia_data.get('weight', 0),
                skeletal=bia_data.get('skeletal', 0),
                fat=bia_data.get('fat', 0),
                fat_per=bia_data.get('percent_fat', 0),
                bmi=bia_data.get('bmi', 0),
                status=0,
                bmr=bia_data.get('bmr', 0),
                significants=', '.join(checked_significants)
            )
            user_bia.save()
            print('saved')

            request.session['checked_significants'] = checked_significants

            return redirect('biaengine:status')
    else:
        form = HealthSignificantsForm()
    return render(request, 'significants/check_significants.html', {'form': form})

