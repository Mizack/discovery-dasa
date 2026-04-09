import cv2
import numpy as np

# Cria uma imagem de fundo branco 800x600
image = np.ones((600, 800, 3), dtype="uint8") * 255

# 1. Desenha a "moeda" de referência (à esquerda)
# Uma moeda azul (usando BGR no OpenCV)
cv2.circle(image, (150, 300), 50, (255, 0, 0), -1)

# 2. Desenha um alvo irregular e não-uniforme (à direita)
# Uma forma com cor RGB (e.g. verde escuro (0, 150, 0)) com um buraco, ou apenas poligonal.
pontos = np.array([
    [400, 100], [600, 150], [650, 350], [700, 500], [500, 550], [350, 450]
], np.int32)
pontos = pontos.reshape((-1, 1, 2))
cv2.fillPoly(image, [pontos], (0, 150, 0))

# Salva a imagem combinada
cv2.imwrite("imgs/imagem_teste.jpg", image)
print("Imagem de teste 'imgs/imagem_teste.jpg' criada com sucesso!")
