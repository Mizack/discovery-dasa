import cv2
import numpy as np
import imutils
from imutils import contours
from imutils import perspective
from scipy.spatial import distance as dist
from sklearn.cluster import KMeans
import sys

def get_dominant_color(image, mask, k=1):
    # Apply mask
    masked = cv2.bitwise_and(image, image, mask=mask)
    
    # Reshape the image to be a list of pixels
    pixels = masked.reshape((masked.shape[0] * masked.shape[1], 3))
    
    # Remove black pixels (from the background of the mask)
    pixels = np.array([p for p in pixels if np.any(p)])
    
    if len(pixels) == 0:
        return (0, 0, 0)
        
    # Use KMeans to find the dominant color
    kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
    kmeans.fit(pixels)
    
    # Return the color as ints
    dominant = kmeans.cluster_centers_[0].astype(int)
    # BGR to RGB for better readability in output
    return (int(dominant[2]), int(dominant[1]), int(dominant[0]))

def midpoint(ptA, ptB):
    return ((ptA[0] + ptB[0]) * 0.5, (ptA[1] + ptB[1]) * 0.5)

# 1. Carregando a Imagem
image_path = "image_2.jpeg" if len(sys.argv) < 2 else sys.argv[1]
print(f"Carregando imagem: {image_path}")

image = cv2.imread(image_path)
if image is None:
    print("Erro ao carregar a imagem. Certifique-se de que o caminho é valido. Tente primeiro rodar: python gerar_imagem_teste.py")
    sys.exit()

# Tamanho do objeto de referência (ex: uma moeda de 2.7 cm de diâmetro)
REF_CM = 2.7

# 2. Pré processamento
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
gray = cv2.GaussianBlur(gray, (7, 7), 0)

# Detecção de bordas
edged = cv2.Canny(gray, 50, 100)
edged = cv2.dilate(edged, None, iterations=1)
edged = cv2.erode(edged, None, iterations=1)

# 3. Extração de Contornos
cnts = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
cnts = imutils.grab_contours(cnts)

if not cnts:
    print("Nenhum objeto encontrado na imagem.")
    sys.exit()

# Ordenar contornos da esquerda para a direita
(cnts, _) = contours.sort_contours(cnts, method="left-to-right")

pixelsPerMetric = None

# Cria uma cópia da imagem para desenhar
orig = image.copy()

num_objects = 0
for i, c in enumerate(cnts):
    # Ignorar contornos muito pequenos (ruídos)
    if cv2.contourArea(c) < 100:
        continue

    num_objects += 1
    # Computar bounding box
    box = cv2.minAreaRect(c)
    box = cv2.cv.BoxPoints(box) if imutils.is_cv2() else cv2.boxPoints(box)
    box = np.array(box, dtype="int")
    
    # Ordenar pontos da bounding box: top-left, top-right, bottom-right, bottom-left
    box = perspective.order_points(box)
    cv2.drawContours(orig, [box.astype("int")], -1, (0, 255, 0), 2)

    # Pegando os cantos da Bounding Box
    (tl, tr, br, bl) = box
    (tltrX, tltrY) = midpoint(tl, tr)
    (blbrX, blbrY) = midpoint(bl, br)
    (tlblX, tlblY) = midpoint(tl, bl)
    (trbrX, trbrY) = midpoint(tr, br)

    # Computando a distância euclidiana (em pixels)
    dA = dist.euclidean((tltrX, tltrY), (blbrX, blbrY)) # Altura
    dB = dist.euclidean((tlblX, tlblY), (trbrX, trbrY)) # Largura
    
    # Circunferência (Perímetro em pixels)
    perimetro_px = cv2.arcLength(c, True)

    # 4. Calibragem (Baseado no primeiro contorno que aparecer à esquerda)
    if pixelsPerMetric is None:
        # A referência é um círculo, então ambas dimensões (largura/altura) são o diâmetro. 
        # Pegaremos dB (largura) como referência.
        pixelsPerMetric = dB / REF_CM
        print(f"Calibrado! Fator de escala definido para as imagens subsequentes.")
        
    # Calculando dimensões reais
    dimA = dA / pixelsPerMetric # Altura cm
    dimB = dB / pixelsPerMetric # Largura cm
    circunferencia_cm = perimetro_px / pixelsPerMetric
    area_cm2 = cv2.contourArea(c) / (pixelsPerMetric ** 2)

    # 5. Cor
    mask = np.zeros(gray.shape, dtype="uint8")
    cv2.drawContours(mask, [c], -1, 255, -1)
    r, g, b = get_dominant_color(image, mask)

    print(f"\n--- Objeto {num_objects} ---")
    if num_objects == 1:
        print(">> Este é o OBJETO DE REFERÊNCIA")
    print(f"Dimensões (Largura x Altura): {dimB:.2f}cm x {dimA:.2f}cm")
    print(f"Circunferência (Perímetro): {circunferencia_cm:.2f}cm")
    print(f"Área: {area_cm2:.2f} cm²")
    print(f"Cor Dominante RGB convertida: ({r}, {g}, {b})")

    # Escrever medidas na imagem resultante
    cv2.putText(orig, f"{dimB:.1f}cm", (int(tltrX - 15), int(tltrY - 10)), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (255, 255, 255), 2)
    cv2.putText(orig, f"{dimA:.1f}cm", (int(trbrX + 10), int(trbrY)), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (255, 255, 255), 2)

# Salvar Imagem Comentada
cv2.imwrite("imagem_analisada.jpg", orig)
print("\nImagem 'imagem_analisada.jpg' gerada com as detecções e medidas visuais.")
