from django.shortcuts import render, redirect
from .forms import HealthSignificantsForm
from main.models import UserBia
from django.contrib.auth.decorators import login_required

# Create your views here.

def significants(request):
    if request.method == 'POST':
        form = HealthSignificantsForm(request.POST)
        if form.is_valid():
            checked_significants = form.cleaned_data['health_significants']
            current_username = request.user.username
            bia = UserBia.objects.filter(username=current_username).order_by('-bia_num').first()
            bia.significants = ', '.join(checked_significants)
            bia.save()

            return redirect('biaengine:status')
    else:
        form = HealthSignificantsForm()
    return render(request, 'significants/check_significants.html', {'form': form})

