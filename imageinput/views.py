from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from imutils.perspective import four_point_transform
from imutils.contours import sort_contours
from main.models import UserBia
from datetime import datetime
from django.contrib.auth.decorators import login_required
from main.apps import MainConfig
import matplotlib.pyplot as plt
import pytesseract
import imutils
import cv2
import io
import re
import requests
import numpy as np
import os
import easyocr


def fileupload(request):
    if request.method == 'POST' and 'image' in request.FILES:

        '''
        pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        uploaded_image = request.FILES['image']
        image = cv2.imdecode(np.frombuffer(uploaded_image.read(), np.uint8), cv2.IMREAD_COLOR)
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        text = pytesseract.image_to_string(rgb_image, lang='kor+eng')
        print(text)
        '''

        uploaded_image = request.FILES['image']
        image = cv2.imdecode(np.frombuffer(uploaded_image.read(), np.uint8), cv2.IMREAD_COLOR)
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = MainConfig.reader.readtext(rgb_image, detail=0)

        results_string =''.join(''.join(map(str, sublist)) for sublist in results)

        height = re.findall(r"(\d{3}\.\d{1})cm", results_string)
        weight = re.findall(r'체중\(kg\)\s*(\d{2}\.\d{1})', results_string)
        skeletal = re.findall(r'Skeletal Muscle Mass\s*(\d{2}\.\d{1})', results_string)
        fat =  re.findall(r'Fat Mass\s*(\d{2}\.\d{1})', results_string)
        BMI = re.findall(r'(\d{2}\.\d{1})\s*제지방량', results_string)
        percent_fat = re.findall(r'Percent Body Fat\s*(\d{2}\.\d{1})', results_string)
        bmr = re.findall(r'기초대사량\s*(\d{4})', results_string)

        
        print("height:", height[-1])
        print("weight:", weight[-1])
        print("skeletal:",skeletal[0])
        print("fat:",fat[-1])
        print("BMI:",BMI[-1])
        print("percent_fat:",percent_fat[-1])
        print("bmr:",bmr[0])

        #ocr로 읽은 정보 프론트로 보냄
        context = {'height':height,
                   'weight':weight,
                   'skeletal':skeletal,
                   'fat':fat,
                   'BMI':BMI,
                   'percent_fat':percent_fat,
                   'bmr':bmr,
                   }


        if 'confirm' in request.POST:  # 사용자가 값을 확인하고 폼을 제출한 경우
            height = float(request.POST.get('height', 0))
            weight = float(request.POST.get('weight', 0))
            skeletal = float(request.POST.get('skeletal', 0))
            fat = float(request.POST.get('fat', 0))
            BMI = float(request.POST.get('bmi', 0))
            percent_fat = float(request.POST.get('percent_fat', 0))
            bmr = float(request.POST.get('bmr', 0))

            request.session['bia_data'] = {
                'height': height,
                'weight': weight,
                'skeletal': skeletal,
                'fat': fat,
                'percent_fat': percent_fat,
                'bmi': BMI,
                'bmr': bmr
            }

            '''
                bia_num = models.AutoField(primary_key=True)
                date = models.DateField()
                username = models.CharField(max_length=100)
                age = models.IntegerField()
                height = models.FloatField()
                weight = models.FloatField()
                skeletal = models.FloatField()
                fat = models.FloatField()
                fat_per = models.FloatField()
                bmi = models.FloatField()
                status = models.CharField(max_length=100)
                bmr = models.FloatField()
            '''


            #return redirect('biaengine:status')
            return redirect('significants:significants')

        else:
            context = {
                'height': height[-1] if height else 0,
                'weight': weight[-1] if weight else 0,
                'skeletal': skeletal[0] if skeletal else 0,
                'fat': fat[-1] if fat else 0,
                'bmi': BMI[-1] if BMI else 0,
                'percent_fat': percent_fat[-1] if percent_fat else 0,
                'bmr': bmr[0] if bmr else 0
            }
            return render(request, 'confirm_values.html', context)


        '''
        image_width = image.shape[1]
        image_height = image.shape[0]
        ratio = image_width / image_height
        scanned_image = make_scan_image(image, width=image_width, ksize=(5, 5), min_threshold=75, max_threshold=200)
        display_image(scanned_image)
        return HttpResponse(text)
        '''
    else:
        return render(request, 'image_upload.html')

def confirm(request):
    if request.method == 'POST':
        height = float(request.POST.get('height', 0))
        weight = float(request.POST.get('weight', 0))
        skeletal = float(request.POST.get('skeletal', 0))
        fat = float(request.POST.get('fat', 0))
        BMI = float(request.POST.get('bmi', 0))
        percent_fat = float(request.POST.get('percent_fat', 0))
        bmr = float(request.POST.get('bmr', 0))

        request.session['bia_data'] = {
            'height': height,
            'weight': weight,
            'skeletal': skeletal,
            'fat': fat,
            'percent_fat': percent_fat,
            'bmi': BMI,
            'bmr': bmr
        }

        return redirect('significants:significants')
    else:
        return redirect('image:upload')

def calculate_age(birthday):
    today = datetime.now().date()
    age = today.year - birthday.year
    if (today.month, today.day) < (birthday.month, birthday.day):
        age -= 1
    return age

@login_required
def make_scan_image(image, width, ksize=(5, 5), min_threshold=75, max_threshold=200):
    image_list_title = []
    image_list = []

    org_image = image.copy()

    # 이미지를 grayscale로 변환하고 blur를 적용
    # 모서리를 찾기위한 이미지 연산
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, ksize, 0)
    edged = cv2.Canny(blurred, min_threshold, max_threshold)

    image_list_title = ['gray', 'blurred', 'edged']
    image_list = [gray, blurred, edged]

    # contours를 찾아 크기순으로 정렬
    cnts = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)


    cnts = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)

    for c in cnts:
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.02 * peri, True)

        # contours가 크기순으로 정렬되어 있기때문에 제일 첫번째 사각형을 영역으로 판단하고 break
        if len(approx) == 4:
            cv2.drawContours(org_image, [approx], -1, (0, 255, 0), 2)

    plt.imshow(org_image)
    plt.title("Detected Rectangles")
    plt.show()

    return org_image

@login_required
def display_image(image, window_name='Image'):
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)  # 윈도우 크기를 조정할 수 있는 창 생성
    cv2.imshow(window_name, image)  # 이미지를 창에 표시
    cv2.waitKey(0)  # 키 입력 대기
    cv2.destroyAllWindows()  # 모든 창 닫기

'''
# 이미지 로드
image = cv2.imread('tino.jpg')

# 그레이스케일로 변환
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# Canny 엣지 검출
edges = cv2.Canny(gray, 50, 150)

# 윤곽선 찾기
contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

# 추출된 윤곽선을 원본 이미지에 그리기 (선택사항)
cv2.drawContours(image, contours, -1, (0, 255, 0), 2)

# 결과 이미지 출력 (선택사항)
cv2.imshow('Contour Detection', image)
cv2.waitKey(0)
cv2.destroyAllWindows()
'''

#pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
# image = cv2.imread(r'C:\Users\22805\Downloads\2.png')
# rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
# text = pytesseract.image_to_string(rgb_image, lang='kor')
# print(text)

