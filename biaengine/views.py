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
import h5py
import tensorflow as tf
import keras
from keras import layers
from sklearn.model_selection import train_test_split
from sklearn.utils import class_weight
from keras.callbacks import EarlyStopping, ModelCheckpoint
from keras.utils import to_categorical
from sklearn.preprocessing import StandardScaler

@login_required
# 모델을 이용해 건강 상태 예측
def status_predict(request):
    current_username = request.user.username
    bia = UserBia.objects.filter(username=current_username).order_by('-bia_num').first()
    if bia:
        bmi = bia.bmi
        weight = bia.weight
        skeletal = bia.skeletal

        skeletal_ratio = (skeletal / weight) * 100

        if bmi < 18.5:
            status = "저체중"
        elif 18.5 <= bmi < 23:
            if skeletal_ratio < 48:
                status = "적정체중"
            else:
                status = "근육형 적정체중"
        elif 23 <= bmi < 25:
            if skeletal_ratio < 48:
                status = "과체중"
            else:
                status = "근육형 과체중"
        elif 25 <= bmi < 30:
            status = "1단계 비만"
        elif 30 <= bmi < 35:
            status = "2단계 비만"
        else:
            status = "3단계 비만"

        bia.status = status
        bia.save()

        request.session['user_id'] = current_username
        request.session['status'] = status

    return redirect('account:result')

'''
# 학습 모델 생성
def make_model(request):
    # hyperparameters
    training_epochs = 100  # EarlyStopping이 적용되므로 큰값으로 설정
    batch_size = 100  # 임의의 값
    learning_rate = 0.01  # 임의의 값
    input_size = 9  # 고정된 값(건강상태를 제외한 데이터)
    hidden_size1 = 128  # 임의의 값 (hidden layer의 노드 개수)
    hidden_size2 = 64  # 임의의 값 (hidden layer의 노드 개수)
    output_size = 8  # 고정된값(0~7_건강상태)
    patience = 10  # 임의의 값(epochs와 data수 고려)

    current_dir = os.path.dirname(__file__)
    csv_path = os.path.join(current_dir, 'test.csv')

    bia_data = pd.read_csv(csv_path, names=["성별", "나이", "신장", "체중", "골격근량", "체지방률", "BMI", "체지방량", "건강상태", "기초대사량"],
                           low_memory=False)  # 번호는 의미없는 값이기에 제거

    print(bia_data.head())
    bia_data['성별'] = bia_data['성별'].map({'남': 0, '여': 1})
    bia_data['건강상태'] = bia_data['건강상태'].map(
        {'저체중': 0, '적정체중': 1, '근육형 적정체중': 2, '근육형 과체중': 3, '과체중': 4, '1단계 비만': 5, '2단계 비만': 6, '3단계 비만': 7})
    bia_features = bia_data.copy()
    bia_labels = bia_features.pop('건강상태')
    bia_features = np.array(bia_features)
    bia_features = bia_features.astype(np.float32)
    bia_labels = np.array(bia_labels)

    # 데이터 전처리
    scaler = StandardScaler()
    bia_features = scaler.fit_transform(bia_features)

    # one-hot incoding 예)6 -> [0,0,0,0,0,0,1,0] 각 확률을 의미하며 6일 확률이 1(100%)이라는 뜻
    bia_labels = to_categorical(bia_labels, num_classes=output_size)

    print(bia_labels)
    print(bia_features)
    print(type(bia_features))
    print(type(bia_labels))
    print("Features data type:", bia_features.dtype)
    print("Labels data type:", bia_labels.dtype)
    print("Features shape:", bia_features.shape)
    print("Labels shape:", bia_labels.shape)

    class_weights = class_weight.compute_class_weight('balanced', classes=np.unique(bia_data['건강상태']),
                                                      y=bia_data['건강상태'])
    class_weight_dict = dict(enumerate(class_weights))

    # 8:2 비율로 train+validation:test 분할
    data_bia_train_val, data_bia_test, label_bia_train_val, label_bia_test = train_test_split(bia_features, bia_labels,
                                                                                              test_size=0.2,
                                                                                              shuffle=True,
                                                                                              random_state=0)  # ramdom_state 값은 고정_한 번 섞은 이후 디버깅할 때마다 바뀌지 않게함

    # 모델 생성
    bia_model = keras.Sequential([
        layers.Dense(hidden_size1, activation='relu', input_shape=(input_size,)),
        layers.Dense(hidden_size2, activation='relu'),
        layers.Dense(output_size, activation='softmax')
    ])

    # 모델 구조 확인 -> 역피라미드 형태(점점 결과값에 수렴해 가기 위함)
    bia_model.summary()

    # Adam과 CategoricalCrossentropy사용
    bia_model.compile(
        optimizer=keras.optimizers.Adam(learning_rate),
        loss=keras.losses.CategoricalCrossentropy(from_logits=False),
        metrics=['accuracy']
    )

    # 학습 전 예측
    predictions = bia_model.predict(data_bia_train_val[:1])
    print(data_bia_train_val[:1])
    print(label_bia_train_val[:1])
    print(np.argmax(predictions, axis=1))
    type(np.argmax(predictions, axis=1))

    estopping = EarlyStopping(monitor='val_loss', patience=patience)  # overfitting 방지
    mcheckpoint = ModelCheckpoint('model_best.keras', monitor='val_accuracy', save_best_only=True)

    # 6:2:2로 train:vaildation:test 나눈 후 학습
    # history = bia_model.fit(data_bia_train_val, label_bia_train_val, batch_size=batch_size, validation_split=0.25, epochs=training_epochs, callbacks=[estopping, mcheckpoint])
    history = bia_model.fit(
        bia_features, bia_labels,
        epochs=training_epochs,
        batch_size=batch_size,
        validation_split=0.2,
        callbacks=[estopping, mcheckpoint],
        class_weight=class_weight_dict  # 클래스 가중치 적용
    )
    # 모델 정확도 및 손실측정
    loss, accuracy = bia_model.evaluate(data_bia_test, label_bia_test)
    # 현재 모델 성능
    print(f"model loss: {loss}")  # model loss: 0.008371715433895588
    print(f"model accuracy: {accuracy}")  # model accuracy: 0.9976850152015686

    # 학습 후 예측
    predictions = bia_model.predict(bia_features)
    print(data_bia_train_val[:1])
    print(label_bia_train_val[:1])
    print(np.argmax(predictions, axis=1))
    bia_model.save("bia_model.h5")
    bia_model.save("bia_model.keras")
'''

