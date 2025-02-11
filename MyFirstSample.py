import cv2
import numpy as np
import matplotlib
matplotlib.use('TkAgg')

import math

# --- Initialization of Variables and Arrays --------------------------------------------

kernel_Dilate = np.ones((5,5),np.uint8)

# --- Generation and Transformation of Images -------------------------------------------

#img = cv2.imread("C:/Users/PMN/Desktop/Four_Objects_Noisy.bmp")
#img = cv2.imread("C:\Users\PMN\Desktop\Einstein Noisy.bmp")
img = cv2.imread("C:/Users/ASUS/Desktop/Four_Objects_Noisy_Background-Black.bmp")

imgGray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)

cv2.imshow("Source Image",img)
cv2.imshow("Gray Image",imgGray)

# --- Noisy Image -----------------------------------------------------------------------

noise = np.random.normal(64,32,imgGray.shape).astype(np.uint8)
imgNoisy = cv2.add(imgGray,noise)

cv2.imshow("Noisy Image",imgNoisy)

# --- Linear Lowpass Filter and Binarization by Thresholding ----------------------------

imgBlur = cv2.GaussianBlur(imgNoisy,(9,9),3)
ret, imgBin = cv2.threshold(imgGray,87,250,cv2.THRESH_BINARY+cv2.THRESH_OTSU)

cv2.imshow("Blur Image",imgBlur)
cv2.imshow("Binary Image",imgBin)

# --- Linear Highpass Filter (Canny) ---------------------------------------------------

imgCanny = cv2.Canny(imgGray,100,100)

cv2.imshow("Canny Image",imgCanny)

# --- Nonlinear Filters ----------------------------------------------------------------

imgDilation = cv2.dilate(imgBin,kernel_Dilate,iterations=2)
imgClosing = cv2.erode(imgDilation,kernel_Dilate,iterations=2)

cv2.imshow("Dilation Image",imgDilation)
cv2.imshow("Closing Image", imgClosing)

# --- Wait -------------------------------------------------------------------------------
cv2.waitKey(0)

# See PyCharm help at https://www.jetbrains.com/help/pycharm/