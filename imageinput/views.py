from django.shortcuts import render, redirect
from .forms import FileUploadForm
from .models import FileUpload
import cv2
import pytesseract
import matplotlib.pyplot as plt
import os
import numpy as np
from django.http import HttpResponse, JsonResponse

def fileupload(request):
    if request.method == 'POST' and request.FILES['image']:
        pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        uploaded_image = request.FILES['image']
        image = cv2.imdecode(np.frombuffer(uploaded_image.read(), np.uint8), cv2.IMREAD_COLOR)
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        text = pytesseract.image_to_string(rgb_image, lang='kor')
        print(text)
        return HttpResponse(text)
    else:
        return render(request, 'image_upload.html')

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
