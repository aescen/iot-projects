import cv2
import numpy as np

src_img = cv2.imread('test.jpg')

average_color_row = np.average(src_img, axis=0)
b, g, r = np.average(average_color_row, axis=0)
print("BGR:", b, g, r)

d_img = np.ones((312,312,3), dtype=np.uint8)
d_img[:,:] = [b, g, r]

cv2.imshow('Source image',src_img)
cv2.imshow('Average Color',d_img)
cv2.waitKey(0)