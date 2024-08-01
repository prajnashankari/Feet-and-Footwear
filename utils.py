from sklearn.cluster import KMeans
import random as rng
import cv2
import imutils
import argparse
from skimage.io import imread
import numpy as np
import matplotlib.pyplot as plt



def preprocess(img):

    img = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)

    img = cv2.GaussianBlur(img, (9, 9), 0)
    img = img/255

    return img

def plotImage(img):
    
    plt.imshow(img)
    #plt.title('Clustered Image')
    plt.show()

def cropOrig(bRect, oimg):
    # x (Horizontal), y (Vertical Downwards) are start coordinates
    # img.shape[0] = height of image
    # img.shape[1] = width of image

    x,y,w,h = bRect

    print(x,y,w,h)
    pcropedImg = oimg[y:y+h,x:x+w]

    x1, y1, w1, h1 = 0, 0, pcropedImg.shape[1], pcropedImg.shape[0]

    y2 = int(h1/10)

    x2 = int(w1/10)

    crop1 = pcropedImg[y1+y2:h1-y2,x1+x2:w1-x2]

    #cv2_imshow(crop1)

    ix, iy, iw, ih = x+x2, y+y2, crop1.shape[1], crop1.shape[0]

    croppedImg = oimg[iy:iy+ih,ix:ix+iw]

    return croppedImg, pcropedImg



def overlayImage(croppedImg, pcropedImg):


    x1, y1, w1, h1 = 0, 0, pcropedImg.shape[1], pcropedImg.shape[0]

    y2 = int(h1/10)

    x2 = int(w1/10)

    new_image = np.zeros((pcropedImg.shape[0], pcropedImg.shape[1], 3), np.uint8)
    new_image[:, 0:pcropedImg.shape[1]] = (255, 0, 0) # (B, G, R)

    new_image[ y1+y2:y1+y2+croppedImg.shape[0], x1+x2:x1+x2+croppedImg.shape[1]] = croppedImg

    return new_image



def kMeans_cluster(img):

    # For clustering the image using k-means, we first need to convert it into a 2-dimensional array
    # (H*W, N) N is channel = 3
    image_2D = img.reshape(img.shape[0]*img.shape[1], img.shape[2])

    # tweak the cluster size and see what happens to the Output
    kmeans = KMeans(n_clusters=2, random_state=0).fit(image_2D)
    clustOut = kmeans.cluster_centers_[kmeans.labels_]

    # Reshape back the image from 2D to 3D image
    clustered_3D = clustOut.reshape(img.shape[0], img.shape[1], img.shape[2])

    clusteredImg = np.uint8(clustered_3D*255)

    return clusteredImg


def edgeDetection(clusteredImage):
  #gray = cv2.cvtColor(hsvImage, cv2.COLOR_BGR2GRAY)
  edged1 = cv2.Canny(clusteredImage, 0, 255)
  edged = cv2.dilate(edged1, None, iterations=1)
  edged = cv2.erode(edged, None, iterations=1)
  return edged

def getBoundingBox(img):
    contours, _ = cv2.findContours(img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    contours = sorted(contours, key=lambda x: cv2.contourArea(x), reverse=True)
    
    contours_poly = [None] * len(contours)
    boundRect = [None] * len(contours)
    for i, c in enumerate(contours):
        contours_poly[i] = cv2.approxPolyDP(c, 3, True)
        boundRect[i] = cv2.boundingRect(contours_poly[i])
    
    return boundRect, contours, contours_poly, img


def drawCnt(bRect, contours, cntPoly, img):

    drawing = np.zeros((img.shape[0], img.shape[1], 3), dtype=np.uint8)   


    paperbb = bRect

    for i in range(len(contours)):
      color = (rng.randint(0,256), rng.randint(0,256), rng.randint(0,256))
      cv2.drawContours(drawing, cntPoly, i, color)
      #cv2.rectangle(drawing, (int(boundRect[i][0]), int(boundRect[i][1])), \
              #(int(boundRect[i][0]+boundRect[i][2]), int(boundRect[i][1]+boundRect[i][3])), color, 2)
    cv2.rectangle(drawing, (int(paperbb[0]), int(paperbb[1])), \
              (int(paperbb[0]+paperbb[2]), int(paperbb[1]+paperbb[3])), color, 2)
    
    return drawing


# def calcFeetSize(pcropedImg, fboundRect):
#   x1, y1, w1, h1 = 0, 0, pcropedImg.shape[1], pcropedImg.shape[0]

#   y2 = int(h1/10)

#   x2 = int(w1/10)

#   fh = y2 + fboundRect[2][3]
#   fw = x2 + fboundRect[2][2]
#   ph = pcropedImg.shape[0]
#   pw = pcropedImg.shape[1]

#   opw = 210
#   oph = 297

#   ofs = 0.0

#   if fw>fh:
#     ofs = (opw/pw)*fw
#   else :
#     ofs = (oph/ph)*fh

#   return ofs








# def calcFeetSize(pcropedImg, fboundRect):
#     x1, y1, w1, h1 = 0, 0, pcropedImg.shape[1], pcropedImg.shape[0]

#     y2 = int(h1 / 10)
#     x2 = int(w1 / 10)

#     fh = y2 + fboundRect[2][3]
#     fw = x2 + fboundRect[2][2]
#     ph = pcropedImg.shape[0]
#     pw = pcropedImg.shape[1]

#     opw = 210
#     oph = 297

#     ofs = 0.0

#     if fw > fh:
#         ofs = (opw / pw) * fw
#     else:
#         ofs = (oph / ph) * fh

#     # Calculate breadth at ball and bridge
#     ball_breadth = fboundRect[1][2]  # Assuming fboundRect[1] is the bounding rectangle at the "ball" part
#     bridge_breadth = fboundRect[0][2]  # Assuming fboundRect[0] is the bounding rectangle at the "bridge" part

#     return ofs, ball_breadth, bridge_breadth




# def calcFeetSize(pcropedImg, fboundRect):
#     x1, y1, w1, h1 = 0, 0, pcropedImg.shape[1], pcropedImg.shape[0]

#     y2 = int(h1 / 10)
#     x2 = int(w1 / 10)

#     fh = y2 + fboundRect[2][3]
#     fw = x2 + fboundRect[2][2]
#     ph = pcropedImg.shape[0]
#     pw = pcropedImg.shape[1]

    # opw = 210
    # oph = 297

    # ofs = 0.0

    # if fw > fh:
    #     ofs = (opw / pw) * fw
    # else:
    #     ofs = (oph / ph) * fh

    # # Calculate breadth at ball and bridge
    # ball_breadth = fboundRect[1][2]  # Assuming fboundRect[1] is the bounding rectangle at the "ball" part
    # bridge_breadth = fboundRect[0][2]  # Assuming fboundRect[0] is the bounding rectangle at the "bridge" part

    # # Rough estimation of height based on width
    # estimated_height = 0.75 * ball_breadth  # Example assumption based on typical proportions

    # return ofs, ball_breadth, bridge_breadth, estimated_height



def calcFeetGirth(pcropedImg, fboundRect):
    # Dimensions of A4 paper in centimeters
    a4_width_cm = 21.0
    a4_height_cm = 29.7

    # Extract dimensions from the bounding rectangles
    foot_length_px = fboundRect[1][3]  # Height of the foot in pixels
    scale_y = a4_height_cm / pcropedImg.shape[0]  # Scale for height

    # Calculate foot dimensions in centimeters
    foot_length_cm = foot_length_px * scale_y

    return foot_length_cm

def calcMeasurements(foot_length_cm):
    # Example proportions, adjust as per empirical data
    ball_breadth_cm = foot_length_cm * 0.38
    bridge_breadth_cm = foot_length_cm * 0.31

    ball_girth_cm = foot_length_cm+1
    instep_girth_cm = foot_length_cm

    return ball_breadth_cm, bridge_breadth_cm, ball_girth_cm, instep_girth_cm