from django import forms

class HealthSignificantsForm(forms.Form):
    HEALTH_SIGNIFICANTS_CHECKES = (
        ('weight_high', '근력 운동이 익숙함'),
        ('weight_low', '근력 운동이 익숙하지 않음'),
        ('cardio_high', '유산소 운동이 익숙함'),
        ('cardio_low', '유산소 운동이 익숙하지 않음'),
        ('under1hour', '운동 시간 1시간 이내'),
        ('over1hour', '운동 시간 1시간 이상'),
        ('shoulder', '어깨 부상'),
        ('elbow', '팔꿈치 부상'),
        ('waist', '허리 부상'),
        ('knee', '무릎 부상'),
    )
    health_significants = forms.MultipleChoiceField(
        widget=forms.CheckboxSelectMultiple,
        choices=HEALTH_SIGNIFICANTS_CHECKES,
        required=False,
    )