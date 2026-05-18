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


##################
import numpy as np
from skimage import color

def calculate_spatial_frequency_bandwidth(image):
    """
    2-D FFT를 사용하여 이미지 전력 스펙트럼의 반전력 대역폭(Half-power bandwidth) 비율을 계산합니다.
    """
    # 1. 흑백 변환 (휘도 정보만 사용)
    if image.ndim == 3:
        gray_image = color.rgb2gray(image)
    else:
        gray_image = image

    # 2. 2-D 고속 푸리에 변환 (FFT) 수행 및 0 주파수(DC) 중앙 이동
    f_transform = np.fft.fft2(gray_image)
    f_shift = np.fft.fftshift(f_transform)

    # 3. 전력 스펙트럼(Power Spectrum) 계산 (에너지)
    power_spectrum = np.abs(f_shift) ** 2

    # 4. 반전력 대역폭 (Half-power bandwidth) 계산
    max_power = np.max(power_spectrum)
    half_power_threshold = max_power / 2.0

    # 임계값 이상의 에너지를 가진 픽셀(주파수 성분) 개수 계산
    significant_pixels = np.sum(power_spectrum >= half_power_threshold)
    
    # 5. 해상도에 따른 편차를 없애기 위해 전체 영역 대비 비율로 정규화
    total_pixels = power_spectrum.size
    bandwidth_ratio = significant_pixels / total_pixels

    return float(bandwidth_ratio)

##################

from skimage.measure import shannon_entropy
from skimage.feature import hog
from skimage import img_as_ubyte
import math

# ---------------------------------------------------------
# 3. Spatial Entropy (공간 엔트로피)
# ---------------------------------------------------------
def calculate_spatial_entropy(image):
    """
    이미지의 흑백 히스토그램을 기반으로 섀넌 엔트로피를 계산합니다.
    시각적 '복잡성'과 픽셀 강도 분포의 정보량을 수치화합니다.
    """
    if image.ndim == 3:
        gray_image = color.rgb2gray(image)
    else:
        gray_image = image
        
    # 0-255 범위의 히스토그램을 위해 8비트 정수형으로 변환
    gray_image = img_as_ubyte(gray_image)
    
    # skimage의 shannon_entropy 함수로 계산 (H = -∑ p_i log2(p_i))
    entropy_value = shannon_entropy(gray_image)
    
    return float(entropy_value)
# ---------------------------------------------------------
# 4. Edge Density (에지 밀도)
# ---------------------------------------------------------
def calculate_edge_density(image):
    """
    Canny 에지 검출기를 사용하여 단위 면적당 에지 픽셀의 밀도를 계산합니다.
    밝기와 무관하게 장면의 혼잡도(clutter)나 인지적 부하를 측정합니다.
    """
    if image.ndim == 3:
        gray_image = color.rgb2gray(image)
    else:
        gray_image = image
        
    # Canny 에지 검출 (이전 프랙탈 차원 코드와 동일한 방식)
    edges = feature.canny(gray_image)
    
    # 에지 픽셀 수 / 전체 픽셀 수
    edge_count = np.sum(edges > 0)
    total_pixels = edges.size
    
    density = edge_count / total_pixels
    return float(density)

# ---------------------------------------------------------
# 5. Edge Orientation Entropy (에지 방향 엔트로피)
# ---------------------------------------------------------
def calculate_edge_orientation_entropy(image):
    """
    HOG(Histogram of Oriented Gradients)의 섀넌 엔트로피를 계산합니다.
    방향성 분포가 균일할수록(자연물) 엔트로피가 높고, 수직/수평 위주면(인공물) 낮습니다.
    """
    if image.ndim == 3:
        gray_image = color.rgb2gray(image)
    else:
        gray_image = image
        
    # HOG 특성 추출 (9개의 방향 빈 사용)
    fd = hog(gray_image, orientations=9, pixels_per_cell=(8, 8),
             cells_per_block=(2, 2), block_norm='L2-Hys', visualize=False)
    
    # 0인 값은 log 계산 시 무한대로 가므로 제외
    fd = fd[fd > 0]
    if len(fd) == 0:
        return 0.0
        
    # 히스토그램을 확률 분포(p_i)로 정규화
    p = fd / np.sum(fd)
    
    # 섀넌 엔트로피 직접 계산: H = -∑ p_i log2(p_i)
    orientation_entropy = -np.sum(p * np.log2(p))
    
    return float(orientation_entropy)