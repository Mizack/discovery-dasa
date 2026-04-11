import cv2
import numpy as np
import os
from fpdf import FPDF

# 1. Gerar a imagem do ArUco
# Usamos o dicionário padrão 4x4 e o ID 0 (que foi configurado no analisador)
aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
# Criando a imagem com 500x500 pixels (boa qualidade de impressão)
marker_img = cv2.aruco.generateImageMarker(aruco_dict, 0, 500)

# Adicionar uma margem branca grande (Quiet Zone) necessária para detecção
margem = 50
marker_com_margem = cv2.copyMakeBorder(
    marker_img, margem, margem, margem, margem, 
    cv2.BORDER_CONSTANT, value=[255, 255, 255]
)

# Salvar temporariamente
caminho_img_temp = "aruco_id0_temp.jpg"
cv2.imwrite(caminho_img_temp, marker_com_margem)

# 2. Criar um PDF em formato A4 garantindo o tamanho Exato de 5cm (50mm) do marcador negro
pdf = FPDF(unit='mm', format='A4')
pdf.add_page()
pdf.set_font('Arial', 'B', 16)
pdf.cell(0, 10, 'Aruco Marker - Escala Oficial (5x5 cm)', ln=True, align='C')

pdf.set_font('Arial', '', 12)
pdf.cell(0, 8, 'INSTRUCOES PARA IMPRESSAO:', ln=True)
pdf.cell(0, 8, '1. Imprima isso em Papel A4.', ln=True)
pdf.cell(0, 8, '2. MUITO IMPORTANTE: Na tela de impressao, coloque "Escala = 100%" ou "Tamanho Real".', ln=True)
pdf.cell(0, 8, '   Nunca use "Ajustar a pagina".', ln=True)
pdf.cell(0, 8, '3. Apos imprimir, recorte o quadrado mantendo uma margem branca de pelo', ln=True)
pdf.cell(0, 8, '   menos 1 cm ao redor do marcador preto.', ln=True)
pdf.ln(20)

# Inserindo no PDF
# Largura desejada do preto = 50mm. O nosso jpg tem margem (10% de cada lado no código acima = 50px de borda pra 500px de marker)
# Tamanho total da imagem pra que a parte preta meça 50mm:
# TotalPx = 600px. Parte Preta = 500px.
# mmTotal / TotalPx = mmPreto / PretoPx => mmTotal = (50 * 600) / 500 = 60 mm.
pdf.image(caminho_img_temp, x=75, y=90, w=60) # Centralizado aprox no meio (210/2 - 30 = 75)

# Salvar
pdf.output("ARUCO_PARA_IMPRESSAO.pdf", "F")
os.remove(caminho_img_temp)

print("✅ Arquivo PDF gerado com sucesso: ARUCO_PARA_IMPRESSAO.pdf")
print("Basta abrir e imprimir em tamanho real (100%).")
