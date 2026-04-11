import cv2
import numpy as np
import imutils
from imutils import perspective
from scipy.spatial import distance as dist
import sys

# Test different thresholds to see what yields closer to 9.7x12.95

PX_PER_CM = 40
image = cv2.imread('imgs/image6.jpeg')
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
gray = cv2.GaussianBlur(gray, (5, 5), 0)
edged = cv2.Canny(gray, 50, 150)
edged = cv2.dilate(edged, None, iterations=1)
edged = cv2.erode(edged, None, iterations=1)

cnts = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
cnts = imutils.grab_contours(cnts)
cnts = sorted(cnts, key=cv2.contourArea, reverse=True)[:5]

paper_contour = None
for c in cnts:
    peri = cv2.arcLength(c, True)
    approx = cv2.approxPolyDP(c, 0.015 * peri, True)
    if len(approx) == 4 and cv2.contourArea(c) > 10000:
        paper_contour = approx
        break

if paper_contour is not None:
    pts = paper_contour.reshape(4, 2)
    rect = np.zeros((4, 2), dtype='float32')
    s = pts.sum(axis=1)
    rect[0] = pts[np.argmin(s)]
    rect[2] = pts[np.argmax(s)]
    diff = np.diff(pts, axis=1)
    rect[1] = pts[np.argmin(diff)]
    rect[3] = pts[np.argmax(diff)]
    
    (tl, tr, br, bl) = rect
    widthA = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
    widthB = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
    maxWidth = max(int(widthA), int(widthB))
    heightA = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
    heightB = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
    maxHeight = max(int(heightA), int(heightB))
    
    WARPED_WIDTH = int(21.0 * PX_PER_CM)
    WARPED_HEIGHT = int(29.7 * PX_PER_CM)
    if maxWidth > maxHeight:
        WARPED_WIDTH = int(29.7 * PX_PER_CM)
        WARPED_HEIGHT = int(21.0 * PX_PER_CM)
        
    dst = np.array([[0, 0], [WARPED_WIDTH - 1, 0], [WARPED_WIDTH - 1, WARPED_HEIGHT - 1], [0, WARPED_HEIGHT - 1]], dtype='float32')
    M = cv2.getPerspectiveTransform(rect, dst)
    warped = cv2.warpPerspective(image, M, (WARPED_WIDTH, WARPED_HEIGHT))
    
    gray_w = cv2.cvtColor(warped, cv2.COLOR_BGR2GRAY)
    gray_w = cv2.GaussianBlur(gray_w, (9, 9), 0)
    
    # Mode 1: OTSU (Current)
    _, thresh1 = cv2.threshold(gray_w, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)
    thresh1 = cv2.dilate(thresh1, None, iterations=3)
    thresh1 = cv2.erode(thresh1, None, iterations=3)
    
    # Mode 2: Adaptive Mean
    thresh2 = cv2.adaptiveThreshold(gray_w, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV, 51, 10)
    thresh2 = cv2.dilate(thresh2, None, iterations=2)
    thresh2 = cv2.erode(thresh2, None, iterations=2)
    
    # Mode 3: OTSU + Morphology Open
    _, thresh3 = cv2.threshold(gray_w, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (15, 15))
    thresh3 = cv2.morphologyEx(thresh3, cv2.MORPH_OPEN, kernel, iterations=2)
    
    for name, thresh in [('OTSU', thresh1), ('ADAPTIVE', thresh2), ('OPENING', thresh3)]:
        cnts_w, _ = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for c in cnts_w:
            if cv2.contourArea(c) > 1000 and cv2.contourArea(c) < (WARPED_WIDTH * WARPED_HEIGHT * 0.3):
                box = cv2.minAreaRect(c)
                box = cv2.boxPoints(box)
                box = perspective.order_points(box)
                dA = dist.euclidean((box[0][0], box[0][1]), (box[3][0], box[3][1]))
                dB = dist.euclidean((box[0][0], box[0][1]), (box[1][0], box[1][1]))
                print(f"{name}: {dA/PX_PER_CM:.2f}cm x {dB/PX_PER_CM:.2f}cm")
                break
