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

def order_points_rect(pts):
    # Order points: top-left, top-right, bottom-right, bottom-left
    rect = np.zeros((4, 2), dtype="float32")
    s = pts.sum(axis=1)
    rect[0] = pts[np.argmin(s)]
    rect[2] = pts[np.argmax(s)]
    diff = np.diff(pts, axis=1)
    rect[1] = pts[np.argmin(diff)]
    rect[3] = pts[np.argmax(diff)]
    return rect

image_path = "imgs/image_2.jpeg" if len(sys.argv) < 2 else sys.argv[1]
print(f"Carregando imagem: {image_path}")

image = cv2.imread(image_path)
if image is None:
    print("Erro ao carregar a imagem. Verifique o caminho.")
    sys.exit()

# Dimensões exatas de uma folha A4 em centímetros
A4_WIDTH_CM = 21.0
A4_HEIGHT_CM = 29.7
# Densidade fixa de pixels por centímetro desejada na correção
PX_PER_CM = 40
WARPED_WIDTH = int(A4_WIDTH_CM * PX_PER_CM)
WARPED_HEIGHT = int(A4_HEIGHT_CM * PX_PER_CM)

# 1. Encontrar a Folha A4 usando um detector de bordas canny robusto
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
gray = cv2.GaussianBlur(gray, (5, 5), 0)
edged = cv2.Canny(gray, 50, 150)
edged = cv2.dilate(edged, None, iterations=1)
edged = cv2.erode(edged, None, iterations=1)

cnts = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
cnts = imutils.grab_contours(cnts)
# Ordena por área para pegar os maiores objetos primeiro. A folha A4 costuma ser o maior objeto
cnts = sorted(cnts, key=cv2.contourArea, reverse=True)[:5]

paper_contour = None
for c in cnts:
    # Aproximar o contorno. A folha tem 4 pontas
    peri = cv2.arcLength(c, True)
    # Use 0.015 em vez de 0.02 para ser mais detalhista na quina
    approx = cv2.approxPolyDP(c, 0.015 * peri, True)
    if len(approx) == 4 and cv2.contourArea(c) > 10000:
        paper_contour = approx
        break

if paper_contour is None:
    print("\n[ERRO] Não consegui detectar uma folha de papel com 4 pontas limpas na sua foto.")
    # ...
    sys.exit()

# 2. Bird's Eye View (Correção de Perspectiva 3D)
pts = paper_contour.reshape(4, 2)
rect = order_points_rect(pts)

# Sem expansão de margens de compensação. Utilizando as coordenadas brutas.

# --- NOVO: DEBUG PARA O USUARIO ---
# Desenhar as bordas COMPENSADAS do papel na imagem para visualização
debug_img = image.copy()
# Desenhar linhas conectando os cantos expandidos
pts_expandidos = rect.astype("int")
cv2.polylines(debug_img, [pts_expandidos], True, (255, 0, 0), 10) # Linha Azul Ciano bem grossa
for ponto in pts_expandidos:
    cv2.circle(debug_img, tuple(ponto), 25, (0, 0, 255), -1) # Bolas Vermelhas maiores

cv2.imwrite("imgs/debug_papel.jpg", debug_img)
print("IMAGEM DE DEBUG: 'imgs/debug_papel.jpg' gerada! O polígono azul marca as extremidades exatas lidas da folha.")


# Checando proporção retrato/paisagem
(tl, tr, br, bl) = rect
widthA = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
widthB = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
maxWidth = max(int(widthA), int(widthB))

heightA = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
heightB = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
maxHeight = max(int(heightA), int(heightB))

if maxWidth > maxHeight: # Folha na horizontal
    WARPED_WIDTH = int(A4_HEIGHT_CM * PX_PER_CM)
    WARPED_HEIGHT = int(A4_WIDTH_CM * PX_PER_CM)

dst = np.array([
    [0, 0],
    [WARPED_WIDTH - 1, 0],
    [WARPED_WIDTH - 1, WARPED_HEIGHT - 1],
    [0, WARPED_HEIGHT - 1]], dtype="float32")

# Aplica a transformação de perspectiva
M = cv2.getPerspectiveTransform(rect, dst)
warped = cv2.warpPerspective(image, M, (WARPED_WIDTH, WARPED_HEIGHT))

# 3. Analisar Objetos dentro dessa "Folha A4 perfeitamente plana"
# Em uma folha branca, os objetos em cima dela costumam criar diferenças mais evidentes
gray_w = cv2.cvtColor(warped, cv2.COLOR_BGR2GRAY)
gray_w = cv2.GaussianBlur(gray_w, (9, 9), 0)

# Usa limiar binário de OTSU em vez de adaptativo. O OTSU separa perfeitamente o 
# "claro" (papel) do "escuro" (objetos) de forma sólida, e não cria "anéis" ao redor,
# que era o motivo de objetos estarem sendo duplicados ou anulados.
_, thresh = cv2.threshold(gray_w, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)

# Engrossa para unificar qualquer pedacinho solto do objeto
thresh = cv2.dilate(thresh, None, iterations=3)
thresh = cv2.erode(thresh, None, iterations=3)

# Agora o RETR_EXTERNAL funciona listando só um bloco sólido por objeto!
cnts_w = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
cnts_w = imutils.grab_contours(cnts_w)

if not cnts_w:
    print("A folha foi detectada, mas nenhum objeto relevante foi encontrado por cima dela.")
    sys.exit()

(cnts_w, _) = contours.sort_contours(cnts_w, method="left-to-right")

orig_w = warped.copy()
num_objects = 0
for i, c in enumerate(cnts_w):
    # Ignorar sujeiras muito pequenas
    if cv2.contourArea(c) < 300: 
        continue
        
    # Ignorar a PRÓPRIA folha ou borda da mesa (se ocupar mais de 30% da área total vizualizada)
    area_total_px = WARPED_WIDTH * WARPED_HEIGHT
    if cv2.contourArea(c) > area_total_px * 0.30:
        continue

    num_objects += 1
    # Bounding Box e pontos
    box = cv2.minAreaRect(c)
    box = cv2.cv.BoxPoints(box) if imutils.is_cv2() else cv2.boxPoints(box)
    box = np.array(box, dtype="int")
    box = perspective.order_points(box)
    cv2.drawContours(orig_w, [box.astype("int")], -1, (0, 255, 0), 2)

    (tl, tr, br, bl) = box
    (tltrX, tltrY) = midpoint(tl, tr)
    (blbrX, blbrY) = midpoint(bl, br)
    (tlblX, tlblY) = midpoint(tl, bl)
    (trbrX, trbrY) = midpoint(tr, br)

    dA = dist.euclidean((tltrX, tltrY), (blbrX, blbrY))
    dB = dist.euclidean((tlblX, tlblY), (trbrX, trbrY))
    
    perimetro_px = cv2.arcLength(c, True)

    # Convertendo pelas dimensões estritas da nossa Folha Plana (PX_PER_CM)
    dimA = dA / PX_PER_CM 
    dimB = dB / PX_PER_CM
    circunferencia_cm = perimetro_px / PX_PER_CM
    area_cm2 = cv2.contourArea(c) / (PX_PER_CM ** 2)

    mask = np.zeros(gray_w.shape, dtype="uint8")
    cv2.drawContours(mask, [c], -1, 255, -1)
    r, g, b = get_dominant_color(warped, mask)

    print(f"\n--- Objeto Detectado na Folha: {num_objects} ---")
    print(f"Dimensões (Largura x Altura): {dimB:.2f}cm x {dimA:.2f}cm")
    print(f"Circunferência (Perímetro): {circunferencia_cm:.2f}cm")
    print(f"Área: {area_cm2:.2f} cm²")
    print(f"Cor Dominante BGR invertido -> RGB: ({r}, {g}, {b})")

    cv2.putText(orig_w, f"{dimB:.2f}cm", (int(tltrX - 30), int(tltrY - 15)), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
    cv2.putText(orig_w, f"{dimA:.2f}cm", (int(trbrX + 15), int(trbrY)), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

cv2.imwrite("imgs/imagem_analisada.jpg", orig_w)
print(f"\nMatemática Corrigida com Sucesso! Foram encontrados {num_objects} objetos na folha.")
print("Imagem 'imgs/imagem_analisada.jpg' está perfeitamente plana e corrigida.")
