import cv2
img = cv2.imread('imgs/peca_com_ArUco .png')
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
_, th_inv = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)
_, th = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)

cnts_inv, _ = cv2.findContours(th_inv, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
print("INV Contours:", sorted([cv2.contourArea(c) for c in cnts_inv], reverse=True)[:5])

cnts, _ = cv2.findContours(th, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
print("Normal Contours:", sorted([cv2.contourArea(c) for c in cnts], reverse=True)[:5])
