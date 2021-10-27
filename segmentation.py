import cv2
import numpy as np

def bwareaopen(img, min_size, connectivity=8):
    num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(img, connectivity=connectivity)
    for i in range(num_labels):
        label_size = stats[i, cv2.CC_STAT_AREA]
        if label_size < min_size:
            img[labels == i] = 0

    return img

def kmeans(image):
    # convert to RGB
    #image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    # reshape the image to a 2D array of pixels and 3 color values (RGB)
    pixel_values = image.reshape((-1, 3))
    # convert to float
    pixel_values = np.float32(pixel_values)

    print(pixel_values.shape)

    # define stopping criteria
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 500, 0.6)

    # number of clusters (K)
    k = 2
    _, labels, (centers) = cv2.kmeans(pixel_values, k, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)
    
    # convert back to 8 bit values
    centers = np.uint8(centers)

    # flatten the labels array
    labels = labels.flatten()

    # convert all pixels to the color of the centroids
    segmented_image = centers[labels.flatten()]
    segmented_image = segmented_image.reshape(image.shape)
    # show the image
    cv2.imshow("kmeans segmented_image", segmented_image)

    #improveGreen(segmented_image)

    image_gray = cv2.cvtColor(segmented_image, cv2.COLOR_BGR2GRAY)
    cv2.imshow("image_gray_k_means", image_gray)
    (To, bin_k_means) = cv2.threshold(image_gray, 0, 255, cv2.THRESH_OTSU)
    #cv2.imshow("bin_k_means", bin_k_means)


    if pixel_values.shape[0] - cv2.countNonZero(bin_k_means) > cv2.countNonZero(bin_k_means) :
        bin_k_means = 255 - bin_k_means

    return bin_k_means


def morfTransform(bin_image): 

    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    erodido = cv2.morphologyEx(bin_image, cv2.MORPH_ERODE, kernel, iterations=1)
    #cv2.imshow("erodido", erodido)

    bwarea = bwareaopen(erodido, 50000, 8)
    #cv2.imshow("bwarea", bwarea)

    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (7, 7))
    close = cv2.morphologyEx(bwarea, cv2.MORPH_CLOSE, kernel, iterations=6)
    #cv2.imshow("close", close)

    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (7, 7))
    dilatado = cv2.morphologyEx(close, cv2.MORPH_DILATE, kernel, iterations=2)
    #cv2.imshow("dilatado", dilatado)

    return 255 - dilatado


def getSegmented(img_name): 
    original = cv2.imread("./imagens/" + img_name)
    cv2.imshow("Original", original)

    original_ycrcb = cv2.cvtColor(original, cv2.COLOR_BGR2YCR_CB)
    cv2.imshow("original_ycrcb", original_ycrcb)
    #image = cv2.cvtColor(original_ycrcb, cv2.COLOR_YCrCb2RGB)

    kmeans_result = kmeans(original_ycrcb)

    #image_gray = cv2.cvtColor(original, cv2.COLOR_BGR2GRAY)
    #cv2.imshow("image_gray", image_gray)
    #(To, bin_original) = cv2.threshold(image_gray, 0, 255, cv2.THRESH_OTSU)
    #cv2.imshow("bin_original", bin_original)

    morf_result = morfTransform(kmeans_result)
    cv2.imshow("morf_result", morf_result)

    return morf_result

