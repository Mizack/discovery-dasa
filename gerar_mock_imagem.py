import cv2
import numpy as np
import os

# Create imgs dir if not exists
os.makedirs("imgs", exist_ok=True)

# 1. Create a background (Surgical Blue Tray)
img = np.ones((800, 1000, 3), dtype=np.uint8)
img[:] = [150, 100, 50] # Azul cirúrgico (BGR)

# 2. Draw a mock tissue (irregular red/pink blob)
# Create a mask for a blob
blob = np.zeros((800, 1000), dtype=np.uint8)
# Draw some overlapping circles to make an irregular shape
cv2.circle(blob, (500, 400), 100, 255, -1)
cv2.circle(blob, (550, 450), 80, 255, -1)
cv2.circle(blob, (430, 380), 90, 255, -1)
cv2.ellipse(blob, (480, 500), (120, 60), 30, 0, 360, 255, -1)

# Color it pink/red (BGR)
img[blob == 255] = [80, 100, 200]

# Add a fake "specular reflection" (glare spot - pure white)
cv2.circle(img, (500, 400), 15, (255, 255, 255), -1)

# 3. Generate ArUco marker
aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
marker_img = cv2.aruco.generateImageMarker(aruco_dict, 0, 100) # 100x100 pixels
marker_img_bgr = cv2.cvtColor(marker_img, cv2.COLOR_GRAY2BGR)
# Place a white square first
img[40:160, 40:160] = [255, 255, 255]
# Place the marker inside the white square
img[50:150, 50:150] = marker_img_bgr

cv2.imwrite("imgs/mock_teste.jpeg", img)
print("Imagem de mock criada em 'imgs/mock_teste.jpeg' (Sem QR code, deve retornar ID Desconhecido)")
