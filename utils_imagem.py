import cv2
import numpy as np
import math
from sklearn.cluster import KMeans

def remover_reflexos_especulares(imagem):
    """
    Remove reflexos brilhantes (glare) muito comuns em tecidos molhados 
    (peças cirúrgicas) sob luzes fortes. Utiliza inpainting.
    """
    # Converter para tons de cinza
    gray = cv2.cvtColor(imagem, cv2.COLOR_BGR2GRAY)
    
    # Aplicar threshold para encontrar pixels muito brilhantes (próximos de 255)
    # Valores acima de 220 ou 230 são geralmente luzes especulares.
    _, mask = cv2.threshold(gray, 220, 255, cv2.THRESH_BINARY)
    
    # Expandir um pouco a máscara para garantir que bordas do reflexo sejam removidas
    mask = cv2.dilate(mask, None, iterations=2)
    
    # Usa inpainting para restaurar a cor da região baseada nas proximidades
    imagem_restaurada = cv2.inpaint(imagem, mask, inpaintRadius=3, flags=cv2.INPAINT_TELEA)
    return imagem_restaurada

def extrair_metricas_morfologicas(contorno):
    """
    Extrai métricas avançadas do contorno, cruciais para análise patológica.
    """
    area = cv2.contourArea(contorno)
    perimetro = cv2.arcLength(contorno, True)
    
    # Bounding Box e Aspect Ratio
    x, y, w, h = cv2.boundingRect(contorno)
    aspect_ratio = float(w) / h if h > 0 else 0
    
    # Convexity (Área da lesão dividida pela área do seu Fecho Convexo)
    hull = cv2.convexHull(contorno)
    hull_area = cv2.contourArea(hull)
    convexity = float(area) / hull_area if hull_area > 0 else 0
    
    # Circularity (Quão próximo a forma é de um círculo perfeito)
    circularity = (4 * math.pi * area) / (perimetro ** 2) if perimetro > 0 else 0
    
    return {
        "area_px": area,
        "perimetro_px": perimetro,
        "aspect_ratio": aspect_ratio,
        "convexity": convexity,
        "circularity": circularity
    }

def get_dominant_color(image, mask, k=1):
    """
    Busca a cor dominante do objeto. Em uma evolução futura, 
    uma matriz de calibração MacBeth deve ser multiplicada aqui.
    """
    masked = cv2.bitwise_and(image, image, mask=mask)
    pixels = masked.reshape((-1, 3))
    pixels = pixels[np.any(pixels != [0, 0, 0], axis=1)]
    
    if len(pixels) == 0:
        return (0, 0, 0)
        
    kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
    kmeans.fit(pixels)
    dominant = kmeans.cluster_centers_[0].astype(int)
    # BGR para RGB
    return (int(dominant[2]), int(dominant[1]), int(dominant[0]))
