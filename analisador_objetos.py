import cv2
import numpy as np
import imutils
from imutils import contours
from scipy.spatial import distance as dist
import sys
from pyzbar.pyzbar import decode

# Imports dos nossos módulos personalizados
from utils_imagem import remover_reflexos_especulares, extrair_metricas_morfologicas, get_dominant_color, get_color_name
from gerador_pdf import gerar_laudo_pdf

def midpoint(ptA, ptB):
    return ((ptA[0] + ptB[0]) * 0.5, (ptA[1] + ptB[1]) * 0.5)

# Tamanho real do lado do marcador ArUco em centímetros impresso
ARUCO_SIZE_CM = 5.0

# 1. Carregamento da Imagem
image_path = "imgs/image_2.jpeg" if len(sys.argv) < 2 else sys.argv[1]
print(f"Carregando imagem: {image_path}")

image = cv2.imread(image_path)
if image is None:
    print("Erro ao carregar a imagem. Verifique o caminho.")
    sys.exit()

orig = image.copy()

# 2. Leitura de QR Code/Barcode (Rastreabilidade do Paciente)
print("Buscando identificacao do paciente (QR Code/Barcode)...")
codigos_barras = decode(image)
patient_id = "Paciente_Desconhecido"
for barcode in codigos_barras:
    patient_id = barcode.data.decode("utf-8")
    (x, y, w, h) = barcode.rect
    cv2.rectangle(orig, (x, y), (x + w, y + h), (0, 0, 255), 2)
    cv2.putText(orig, patient_id, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
    print(f"-> ID Encontrado: {patient_id}")
    break # Pega o primeiro encontrado

if patient_id == "Paciente_Desconhecido":
    print("-> Nenhum ID legivel encontrado. Usando ID anonimo.")

# 3. Tratamento de Reflexos Especulares (Glare)
print("Aplicando tratamento para remover reflexos umidos...")
image_sem_reflexo = remover_reflexos_especulares(image)

# 4. Encontrar o Marcador ArUco para Calibracao de Escala
print("Buscando marcador ArUco para calibracao...")
# Carrega o dicionario padrao 4x4
aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
aruco_params = cv2.aruco.DetectorParameters()
detector = cv2.aruco.ArucoDetector(aruco_dict, aruco_params)

corners, ids, rejected = detector.detectMarkers(image)

if len(corners) == 0:
    print("[ERRO] Nenhum marcador ArUco detectado na imagem. Impossivel calibrar escala!")
    # Criar um fallback temporário pra não quebrar se quiserem testar agora
    print("[AVISO] Usando valor fallback de Pixels por CM (PX_PER_CM = 40) para testes.")
    PX_PER_CM = 40.0
else:
    # Usar o primeiro marcador encontrado para pegar a escala
    marker_corners = corners[0][0]
    (topLeft, topRight, bottomRight, bottomLeft) = marker_corners
    
    # Desenhar ArUco
    cv2.polylines(orig, [marker_corners.astype(int)], True, (0, 255, 0), 2)
    
    # Calcular tamanho em pixels da aresta do ArUco
    aruco_px_width = dist.euclidean(topLeft, topRight)
    PX_PER_CM = aruco_px_width / ARUCO_SIZE_CM
    print(f"-> ArUco Detectado! Calibracao: 1 cm = {PX_PER_CM:.2f} pixels.")

# 5. Segmentacao e Analise de Objetos (Pecas Cirurgicas)
gray = cv2.cvtColor(image_sem_reflexo, cv2.COLOR_BGR2GRAY)
gray = cv2.GaussianBlur(gray, (7, 7), 0)

# Aplicar threshold OTSU em tons de cinza
_, thresh_inv = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)
_, thresh_norm = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)

# Aplicar threshold OTSU no canal de Saturação (ótimo para ignorar sombras pretas/cinzas no fundo)
hsv = cv2.cvtColor(image_sem_reflexo, cv2.COLOR_BGR2HSV)
_, s, _ = cv2.split(hsv)
s = cv2.GaussianBlur(s, (7, 7), 0)
_, thresh_sat = cv2.threshold(s, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)

# Morfologia para varrer sujeiras
kernel = np.ones((5,5), np.uint8)
thresh_inv = cv2.morphologyEx(thresh_inv, cv2.MORPH_OPEN, kernel)
thresh_norm = cv2.morphologyEx(thresh_norm, cv2.MORPH_OPEN, kernel)
thresh_sat = cv2.morphologyEx(thresh_sat, cv2.MORPH_OPEN, kernel)

thresh_inv = cv2.dilate(thresh_inv, None, iterations=3)
thresh_inv = cv2.erode(thresh_inv, None, iterations=3)
thresh_norm = cv2.dilate(thresh_norm, None, iterations=3)
thresh_norm = cv2.erode(thresh_norm, None, iterations=3)
thresh_sat = cv2.dilate(thresh_sat, None, iterations=3)
thresh_sat = cv2.erode(thresh_sat, None, iterations=3)

cnts_inv = cv2.findContours(thresh_inv.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
cnts_inv = imutils.grab_contours(cnts_inv)

cnts_norm = cv2.findContours(thresh_norm.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
cnts_norm = imutils.grab_contours(cnts_norm)

cnts_sat = cv2.findContours(thresh_sat.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
cnts_sat = imutils.grab_contours(cnts_sat)

image_area = image.shape[0] * image.shape[1]

# Filtra invalidos de ambas as abordagens
def filtrar_contornos(cnts):
    validos = []
    for c in cnts:
        area = cv2.contourArea(c)
        if area >= 500 and area <= (image_area * 0.7):
            validos.append(c)
    # IMPORTANTE: Ordenar pelo maior primeiro para evitar comparar ruídos
    validos = sorted(validos, key=cv2.contourArea, reverse=True)
    return validos

cnts_inv_validos = filtrar_contornos(cnts_inv)
cnts_norm_validos = filtrar_contornos(cnts_norm)
cnts_sat_validos = filtrar_contornos(cnts_sat)

# Escolhe a abordagem que conseguiu destacar a peca (e nao o fundo)
# Priorizamos a Saturação para tecidos úmidos/com cor, pois a sombra tem saturação 0
todas_as_abordagens = [
    (cnts_sat_validos, "Saturacao (Anti-Sombra)"),
    (cnts_norm_validos, "Normal Grayscale"),
    (cnts_inv_validos, "Inverted Grayscale")
]

cnts = []
for abordagem, nome in todas_as_abordagens:
    if len(abordagem) > 0:
        cnts = abordagem
        print(f"-> Utilizando segmentacao por {nome}.")
        break

if not cnts:
    print("Nenhum objeto detectado apos a calibracao.")
    sys.exit()

# Ordenar da esquerda para a direita
(cnts, _) = contours.sort_contours(cnts, method="left-to-right")

num_objects = 0
objetos_metricas = []

for i, c in enumerate(cnts):
    # Ignorar detritos muito pequenos ou o proprio marcador (se ficou no threshold)
    if cv2.contourArea(c) < 500:
        continue
    
    # Ignorar caso a area seja gigantesca (borda da imagem)
    if cv2.contourArea(c) > (image.shape[0] * image.shape[1] * 0.8):
        continue

    num_objects += 1
    
    # Extrair Métricas Morfologicas da nossa utils_imagem
    mm = extrair_metricas_morfologicas(c)
    area_cm2 = mm["area_px"] / (PX_PER_CM ** 2)
    circularity = mm["circularity"]
    convexity = mm["convexity"]
    
    # Bounding Box tradicional para Largura e Altura
    box = cv2.minAreaRect(c)
    box = cv2.cv.BoxPoints(box) if imutils.is_cv2() else cv2.boxPoints(box)
    box = np.array(box, dtype="int")
    
    # Desenhar o contorno exato da peca
    cv2.drawContours(orig, [c], -1, (255, 255, 0), 2)
    
    # Ordenar cantos para calcular largura/altura correta da caixa abrangente
    # order_points needs to be implemented or we can just use bounding rect
    rect_x, rect_y, rect_w, rect_h = cv2.boundingRect(c)
    dim_w = rect_w / PX_PER_CM
    dim_h = rect_h / PX_PER_CM
    
    # Diâmetro de Feret Máximo
    sq = np.squeeze(c)
    if len(sq.shape) == 2:
        distances = dist.cdist(sq, sq, 'euclidean')
        max_dist_cm = np.max(distances) / PX_PER_CM
    else:
        max_dist_cm = max(dim_w, dim_h)
        
    # Cor Dominante
    mask = np.zeros(gray.shape, dtype="uint8")
    cv2.drawContours(mask, [c], -1, 255, -1)
    
    # Passamos imagem ORIGINAL para extrair a cor real do tecido sem as edições (ou a sem_reflexo)
    r, g, b = get_dominant_color(image, mask)
    nome_cor = get_color_name(r, g, b)
    
    print(f"\n--- Fragmento Cirurgico {num_objects} ---")
    print(f"Area: {area_cm2:.2f} cm² | Convexidade: {convexity:.2f} | Circularidade: {circularity:.2f}")
    print(f"Cor (RGB): ({r}, {g}, {b}) - {nome_cor}")
    
    # Preparar dict para o PDF
    dados_obj = {
        "dim_w": dim_w,
        "dim_h": dim_h,
        "max_feret": max_dist_cm,
        "area_cm2": area_cm2,
        "circularity": circularity,
        "convexity": convexity,
        "color": (r, g, b),
        "color_name": nome_cor
    }
    objetos_metricas.append(dados_obj)

    # Marcacao Visual Textual (usamos centro puro)
    cv2.putText(orig, f"{dim_w:.1f}x{dim_h:.1f}cm", (rect_x, rect_y - 15), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)

# Salvar a imagem processada
caminho_imagem_out = "imgs/imagem_analisada_medica.jpg"
cv2.imwrite(caminho_imagem_out, orig)
print(f"\nAnalise visual concluida! Imagem gerada: {caminho_imagem_out}")

# 6. Gerar Laudo PDF
gerar_laudo_pdf(patient_id, objetos_metricas, caminho_imagem_out, f"laudo_{patient_id.replace(' ', '_')}.pdf")
