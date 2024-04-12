from django.http import HttpResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.shortcuts import redirect

from main.models import UserBia, WorkoutData, DietData


import pandas as pd
import numpy as np
import math
import os

import tensorflow as tf
from tensorflow.keras import layers


# 학습 모델 생성
def make_model():
    np.set_printoptions(precision=3, suppress=True)

    bia_train = pd.read_csv("test.csv", names=["번호","성별","나이","신장","체중","골격근량","체지방률","BMI","체지방량","건강상태","기초대사량"], low_memory=False)

    print(bia_train.head())
    print('train complete')

    bia_train['성별'] = bia_train['성별'].map({'남': 0, '여': 1})
    bia_train['건강상태'] = bia_train['건강상태'].map({'저체중': 0, '적정체중': 1,'근육형 적정체중': 2, '근육형 과체중': 3, '과체중': 4, '1단계 비만': 5, '2단계 비만': 6, '3단계 비만': 7})
    bia_features = bia_train.copy()
    bia_labels = bia_features.pop('건강상태')

    bia_features = np.array(bia_features)
    print(bia_features)

    bia_features = bia_features.astype(np.float32)
    print(bia_features)

    bia_model = tf.keras.Sequential([
        layers.Dense(64),
        layers.Dense(1)
    ])

    bia_model.compile(loss = tf.keras.losses.MeanSquaredError(),
                      optimizer = tf.keras.optimizers.Adam())

    bia_model.fit(bia_features, bia_labels, epochs=1000)

    bia_model.save("bia_model_1000.h5")
    bia_model.save("bia_model_1000.keras")

@login_required
# 모델을 이용해 건강 상태 예측
def status_predict(request):
    current_username = request.user.username
    bia = UserBia.objects.filter(username=current_username).order_by('-bia_num').first()

    if bia:
        new_data = np.array([[
            bia.bia_num,
            0,
            25,
            bia.height,
            bia.weight,
            bia.skeletal,
            bia.fat_per,
            bia.bmi,
            bia.fat,
            bia.bmr]])

        current_dir = os.path.dirname(__file__)
        model_path = os.path.join(current_dir, 'bia_model.keras')

        new_data = new_data.astype(np.float32)
        bia_model = tf.keras.models.load_model(model_path)
        predictions=bia_model.predict(new_data)
        print(predictions)

        predictions = int(round(predictions[0][0]))
        print(predictions)

        if predictions == 0:
            status = "저체중"
        elif predictions == 1:
            status = '적정체중'
        elif predictions == 2:
            status = '근육형 적정체중'
        elif predictions == 3:
            status = '근육형 과체중'
        elif predictions == 4:
            status = '과체중'
        elif predictions == 5:
            status = '1단계 비만'
        elif predictions == 6:
            status = '2단계 비만'
        else:
            status = '3단계 비만'

        bia.status = status
        bia.save()
        print(predictions)

        request.session['user_id'] = current_username
        request.session['status'] = status

    return redirect('account:result')