import cv2
import numpy as np
import time
from classification import classify
from segmentation import getSegmented

def closeAfterKey():
    cv2.waitKey(0)
    cv2.destroyAllWindows()

def getOrientation(bin_image):
    img_height, img_width = bin_image.shape[:2]
    x_max = 0
    x_min = img_width
    y_max = 0
    y_min = img_height
    #print("img_width: " + str(img_width) + "; img_height: " + str(img_height))

    for x in range(0, img_width-1):
        for y in range(0, img_height-1):
            if(bin_image[y][x] == 255):
                if(x > x_max):
                    x_max = x
                if(x < x_min):
                    x_min = x
                if(y > y_max):
                    y_max = y
                if(y < y_min):
                    y_min = y
    
    #print("x_max, x_min: " + str(x_max) + ", " + str(x_min))
    #print("y_max, y_min: " + str(y_max) + ", " + str(y_min))

    bin_rgb = cv2.cvtColor(bin_image, cv2.COLOR_GRAY2RGB)
    cv2.rectangle(bin_rgb, (x_max, y_max), (x_min, y_min), (0, 0, 255), 2)
    #cv2.imshow("bin_image", bin_rgb)

    hand_width = x_max - x_min
    hand_height = y_max - y_min
    ratio = hand_height/hand_width
    orientation = "VERT" if ratio > 1 else "HORZ"
    #print("ratio: " + str(ratio))
    print(orientation)

    return x_max, y_max, x_min, y_min, orientation

def centroid(bin_image):
    img_height, img_width = bin_image.shape[:2]
    M_00 = M_01 =  M_10 = 0
    for x in range(0, img_width-1):
        for y in range(0, img_height-1):
            M_00 += bin_image[y][x]  
            M_01 += (y)*bin_image[y][x] 
            M_10 += (x)*bin_image[y][x]

    x = int(M_10 / M_00)
    y = int(M_01 / M_00)

    #print("Centroid (x, y): (" + str(x) + ", " + str(y) + ")")
    bin_rgb = cv2.cvtColor(bin_image, cv2.COLOR_GRAY2RGB)
    cv2.circle(bin_rgb, (x, y), 10, (0, 255, 0), 3)
    cv2.imshow("Centroid", bin_rgb)
    return (x, y)


def thumbDetection(bin_image, x_max, y_max, x_min, y_min, img_orientation):
    img_height, img_width = bin_image.shape[:2]
    bin_rgb = cv2.cvtColor(bin_image, cv2.COLOR_GRAY2RGB)
    if(img_orientation == "HORZ"):
        rect_width = int(0.15*img_height)
    else:
        rect_width = int(0.15*img_width)

        cv2.rectangle(bin_rgb, (x_min + rect_width, y_max), (x_min, y_min), (0, 0, 255), 2)
        cv2.rectangle(bin_rgb, (x_max, y_max), (x_max - rect_width, y_min), (255, 0, 0), 2)
        cv2.imshow("thumb_containers", bin_rgb)

        # Left
        percent_left = getPercentInContainer(bin_image, x_min + rect_width, y_max, x_min, y_min)
        # Right
        percent_right = getPercentInContainer(bin_image, x_max, y_max, x_max - rect_width, y_min)
        thumb_threshold = 0.15
        if(percent_left <= thumb_threshold and percent_right > thumb_threshold):
            print("Dedão na esquerda")
            return "LEFT"
        elif(percent_left > thumb_threshold and percent_right <= thumb_threshold):
            print("Dedão na direita")
            return "RIGHT"
        else:
            print("Dedão não identificado")
            return "NONE"

def getPercentInContainer(bin_image, x_max, y_max, x_min, y_min):
    white_pixels = 0
    black_pixels = 0
    for x in range(x_min, x_max):
        for y in range(y_min, y_max):
            if(bin_image[y][x] == 255):
                white_pixels += 1
            else:
                black_pixels += 1

    percent = white_pixels / (white_pixels + black_pixels)
    #print("percent: " + str(percent))
    return percent

def peakDetection(bin_image, img_orientation):
    bin_rgb = cv2.cvtColor(bin_image, cv2.COLOR_GRAY2RGB)
    contours, hierarchy = cv2.findContours(bin_image, mode=cv2.RETR_TREE, method=cv2.CHAIN_APPROX_NONE)
    image_copy = bin_rgb.copy()
    cv2.drawContours(image_copy, contours=contours, contourIdx=-1, color=(0, 255, 0), thickness=2, lineType=cv2.LINE_AA)
    cv2.imshow("Contorno da imagem", image_copy)

    if(len(contours) != 1): 
        raise Exception("Quantidade de contornos diferente de 1")

    subindo = True
    descendo = False
    picos_maxima = []
    picos_minima = []

    contour = contours[0]
    #contours[0][point_num][0][x=0 or y=1]
    length = len(contour)
    for i in range(0, length-2):
        if contour[i][0][1] < contour[i+1][0][1]:

            if subindo == True:
                picos_maxima.append(contour[i][0])
                cv2.circle(bin_rgb, (contour[i][0][0], contour[i][0][1]), 5, (0, 0, 255), 3)
            
            descendo = True
            subindo = False
        elif contour[i][0][1] > contour[i+1][0][1]:

            if descendo == True:
                picos_minima.append(contour[i][0])
                cv2.circle(bin_rgb, (contour[i][0][0], contour[i][0][1]), 5, (255, 0, 0), 3)
            
            subindo = True
            descendo = False
        

    cv2.imshow("Picos", bin_rgb)
    return picos_maxima


def Proj(img_name):
    start = time.time()

    segmented = getSegmented(img_name)
    x_max, y_max, x_min, y_min, orientation = getOrientation(segmented)
    thumb = thumbDetection(segmented, x_max, y_max, x_min, y_min, orientation)
    x_cent, y_cent = centroid(segmented)
    max_peaks = peakDetection(segmented, orientation)

    letra = classify(orientation, x_cent, y_cent, max_peaks, thumb)
    
    end = time.time()
    print("\nExecution time (s): " + str(end - start))

    closeAfterKey()
    cv2.destroyAllWindows()
    return letra

frase = " "

frase += Proj("imagem6.jpeg") # I
frase += " "
frase += Proj("imagem2.jpeg") # L
frase += Proj("imagem1.jpeg") # O
frase += Proj("imagem10.jpeg") # V
frase += Proj("imagem5.jpeg") # E
frase += " "
frase += Proj("imagem7.jpeg") # U

print(frase)

#Proj("imagem3.jpeg") # U
#Proj("imagem4.jpeg") # P
#Proj("imagem8.jpeg") # H
#Proj("imagem9.jpeg") # I
