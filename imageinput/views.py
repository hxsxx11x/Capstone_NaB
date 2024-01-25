from django.shortcuts import render
from .forms import ImageUploadForm

import cv2
import numpy as np

from django.http import JsonResponse

def image_upload(request):
    if request.method == 'POST':
        image = request.FILES.get('image')
        return JsonResponse({'message': 'success', 'filename': image.name})
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