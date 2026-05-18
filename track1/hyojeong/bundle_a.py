import numpy as np
from scipy.stats import linregress
from skimage import color, feature

def calculate_fractal_dimension(image):
    """
    Box-counting 기법을 사용하여 이미지의 프랙탈 차원을 계산합니다.
    자연경관은 보통 1.3 ~ 1.5 사이의 값을 가집니다.
    """
    # 1. 흑백 변환 및 엣지 검출 (공간적 디테일 추출)
    if image.ndim == 3:
        gray_image = color.rgb2gray(image)
    else:
        gray_image = image
        
    # Canny 에지 검출기를 통해 이미지의 구조적 패턴만 남김
    edges = feature.canny(gray_image)
    
    # 엣지가 존재하는 픽셀 좌표 추출
    pixels = np.column_stack(np.where(edges > 0))
    if len(pixels) == 0:
        return 0.0 # 패턴이 없는 경우
        
    # 2. 박스 크기(s) 설정
    # 박스 크기를 2픽셀부터 이미지 최소 크기까지 2의 제곱수 비율로 늘려가며 확인
    max_dim = min(edges.shape)
    sizes = np.floor(np.logspace(1, np.log2(max_dim), num=10, base=2)).astype(int)
    sizes = np.unique(sizes) # 중복 크기 제거
    
    counts = []
    
    # 3. Box Counting 실행
    for size in sizes:
        # 이미지를 size x size 크기의 격자로 나누어 엣지가 포함된 격자 수 계산
        H, _, _ = np.histogram2d(pixels[:,0], pixels[:,1], 
                                 bins=(edges.shape[0]//size, edges.shape[1]//size))
        counts.append(np.sum(H > 0))
        
    # 4. Log-Log 회귀 분석
    # x = log(s), y = log(N(s))
    x = np.log(sizes)
    y = np.log(counts)
    
    # 선형 회귀 분석을 통해 기울기 추출
    slope, intercept, r_value, p_value, std_err = linregress(x, y)
    
    # 공식에 따라 기울기의 부호를 반전시킨 값이 프랙탈 차원 D
    fractal_dim = -slope
    
    return fractal_dim