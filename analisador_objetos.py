import cv2
import numpy as np
import imutils
from imutils import contours
from scipy.spatial import distance as dist
import sys
import os

try:
    from pyzbar.pyzbar import decode
    HAS_PYZBAR = True
except (ImportError, FileNotFoundError, OSError) as e:
    HAS_PYZBAR = False
    print(f"[AVISO] pyzbar nao pode ser carregado. Fallback ativado. Erro: {e}")

# Imports dos nossos módulos personalizados
from utils_imagem import remover_reflexos_especulares, extrair_metricas_morfologicas, get_dominant_color, get_color_name
from gerador_pdf import gerar_laudo_pdf

def midpoint(ptA, ptB):
    return ((ptA[0] + ptB[0]) * 0.5, (ptA[1] + ptB[1]) * 0.5)

class AnalisadorObjetos:
    def __init__(self, aruco_size_cm=5.0):
        # Tamanho real do lado do marcador ArUco em centímetros impresso
        self.aruco_size_cm = aruco_size_cm
        self.logs = []

    def log(self, msg):
        """Armazena os logs para retornar à API depois e printa no console"""
        self.logs.append(msg)
        print(msg)

    def analisar(self, image_path):
        self.logs = []
        self.log(f"Carregando imagem: {image_path}")

        image = cv2.imread(image_path)
        if image is None:
            self.log("Erro ao carregar a imagem. Verifique o caminho.")
            return {"success": False, "error": "Imagem não encontrada ou inválida.", "logs": "\n".join(self.logs)}

        orig = image.copy()

        self.log("Buscando identificacao do paciente (QR Code/Barcode)...")
        patient_id = "Paciente_Desconhecido"

        if HAS_PYZBAR:
            codigos_barras = decode(image)
            for barcode in codigos_barras:
                patient_id = barcode.data.decode("utf-8")
                (x, y, w, h) = barcode.rect
                cv2.rectangle(orig, (x, y), (x + w, y + h), (0, 0, 255), 2)
                cv2.putText(orig, patient_id, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                self.log(f"-> ID Encontrado: {patient_id}")
                break # Pega o primeiro encontrado
        else:
            # Fallback usando OpenCV nativo
            qrDecoder = cv2.QRCodeDetector()
            data, bbox, _ = qrDecoder.detectAndDecode(image)
            if data and len(data) > 0:
                patient_id = data
                if bbox is not None:
                    pts = np.array(bbox[0], dtype=np.int32)
                    cv2.polylines(orig, [pts], True, (0, 0, 255), 2)
                    cv2.putText(orig, patient_id, (int(pts[0][0]), int(pts[0][1]) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                self.log(f"-> ID Encontrado via CV2: {patient_id}")

        if patient_id == "Paciente_Desconhecido":
            self.log("-> Nenhum ID legivel encontrado. Usando ID anonimo.")

        self.log("Aplicando tratamento para remover reflexos umidos...")
        image_sem_reflexo = remover_reflexos_especulares(image)

        self.log("Buscando marcador ArUco para calibracao...")
        aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
        aruco_params = cv2.aruco.DetectorParameters()
        detector = cv2.aruco.ArucoDetector(aruco_dict, aruco_params)

        corners, ids, rejected = detector.detectMarkers(image)

        if len(corners) == 0:
            self.log("[ERRO] Nenhum marcador ArUco detectado na imagem. Impossivel calibrar escala!")
            self.log("[AVISO] Usando valor fallback de Pixels por CM (PX_PER_CM = 40) para testes.")
            PX_PER_CM = 40.0
        else:
            marker_corners = corners[0][0]
            (topLeft, topRight, bottomRight, bottomLeft) = marker_corners
            
            cv2.polylines(orig, [marker_corners.astype(int)], True, (0, 255, 0), 2)
            
            aruco_px_width = dist.euclidean(topLeft, topRight)
            PX_PER_CM = aruco_px_width / self.aruco_size_cm
            self.log(f"-> ArUco Detectado! Calibracao: 1 cm = {PX_PER_CM:.2f} pixels.")

        gray = cv2.cvtColor(image_sem_reflexo, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (7, 7), 0)

        _, thresh_inv = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)
        _, thresh_norm = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)

        hsv = cv2.cvtColor(image_sem_reflexo, cv2.COLOR_BGR2HSV)
        _, s, _ = cv2.split(hsv)
        s = cv2.GaussianBlur(s, (7, 7), 0)
        _, thresh_sat = cv2.threshold(s, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)

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

        def filtrar_contornos(cnts):
            validos = []
            for c in cnts:
                area = cv2.contourArea(c)
                if area >= 500 and area <= (image_area * 0.7):
                    validos.append(c)
            validos = sorted(validos, key=cv2.contourArea, reverse=True)
            return validos

        cnts_inv_validos = filtrar_contornos(cnts_inv)
        cnts_norm_validos = filtrar_contornos(cnts_norm)
        cnts_sat_validos = filtrar_contornos(cnts_sat)

        todas_as_abordagens = [
            (cnts_sat_validos, "Saturacao (Anti-Sombra)"),
            (cnts_norm_validos, "Normal Grayscale"),
            (cnts_inv_validos, "Inverted Grayscale")
        ]

        cnts = []
        for abordagem, nome in todas_as_abordagens:
            if len(abordagem) > 0:
                cnts = abordagem
                self.log(f"-> Utilizando segmentacao por {nome}.")
                break

        if not cnts:
            msg = "Nenhum objeto detectado apos a calibracao."
            self.log(msg)
            return {"success": False, "error": msg, "logs": "\n".join(self.logs)}

        (cnts, _) = contours.sort_contours(cnts, method="left-to-right")

        num_objects = 0
        objetos_metricas = []

        for i, c in enumerate(cnts):
            if cv2.contourArea(c) < 500:
                continue
            if cv2.contourArea(c) > (image_area * 0.8):
                continue

            num_objects += 1
            
            mm = extrair_metricas_morfologicas(c)
            area_cm2 = mm["area_px"] / (PX_PER_CM ** 2)
            circularity = mm["circularity"]
            convexity = mm["convexity"]
            
            box = cv2.minAreaRect(c)
            box = cv2.cv.BoxPoints(box) if imutils.is_cv2() else cv2.boxPoints(box)
            box = np.array(box, dtype="int")
            
            cv2.drawContours(orig, [c], -1, (255, 255, 0), 2)
            
            rect_x, rect_y, rect_w, rect_h = cv2.boundingRect(c)
            dim_w = rect_w / PX_PER_CM
            dim_h = rect_h / PX_PER_CM
            
            sq = np.squeeze(c)
            if len(sq.shape) == 2:
                distances = dist.cdist(sq, sq, 'euclidean')
                max_dist_cm = np.max(distances) / PX_PER_CM
            else:
                max_dist_cm = max(dim_w, dim_h)
                
            mask = np.zeros(gray.shape, dtype="uint8")
            cv2.drawContours(mask, [c], -1, 255, -1)
            
            r, g, b = get_dominant_color(image, mask)
            nome_cor = get_color_name(r, g, b)
            
            self.log(f"\n--- Fragmento Cirurgico {num_objects} ---")
            self.log(f"Area: {area_cm2:.2f} cm² | Convexidade: {convexity:.2f} | Circularidade: {circularity:.2f}")
            self.log(f"Cor (RGB): ({r}, {g}, {b}) - {nome_cor}")
            
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

            cv2.putText(orig, f"{dim_w:.1f}x{dim_h:.1f}cm", (rect_x, rect_y - 15), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)

        base_dir = os.path.dirname(os.path.abspath(__file__))
        caminho_imagem_out = os.path.join(base_dir, "imgs", "imagem_analisada_medica.jpg")
        cv2.imwrite(caminho_imagem_out, orig)
        self.log(f"\nAnalise visual concluida! Imagem gerada: {caminho_imagem_out}")

        laudo_name = f"laudo_{patient_id.replace(' ', '_')}.pdf"
        laudo_path = os.path.join(base_dir, laudo_name)
        gerar_laudo_pdf(patient_id, objetos_metricas, caminho_imagem_out, laudo_path)
        
        return {
            "success": True,
            "logs": "\n".join(self.logs),
            "laudo_filename": laudo_name,
            "imagem_name": "imagem_analisada_medica.jpg"
        }

if __name__ == "__main__":
    if len(sys.argv) > 1:
        analisador = AnalisadorObjetos()
        resultado = analisador.analisar(sys.argv[1])
        print("Finalizado com sucesso:", resultado["success"])
