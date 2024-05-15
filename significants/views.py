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
            checked_significants = form.cleaned_data['health_significants']
            print("Checked Significants:",checked_significants)  # 디버깅 출력
            current_username = request.user.username
            bia = UserBia.objects.filter(username=current_username).order_by('-bia_num').first()
            bia.significants = ', '.join(checked_significants)
            bia.save()

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

            return redirect('biaengine:status')
    else:
        form = HealthSignificantsForm()
    return render(request, 'significants/check_significants.html', {'form': form})

