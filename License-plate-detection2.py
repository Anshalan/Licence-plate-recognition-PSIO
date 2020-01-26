import cv2 as cv
import imutils
import pytesseract
import string
import numpy as np
from PIL import Image
#import math as m

pytesseract.pytesseract.tesseract_cmd = "C:\\Program Files\\Python38\\TesseractOCR\\tesseract.exe"

### Reading Image -> Resiziing it -> copying original image to variable 'image'
fileDIR = '2m\\1'
image = cv.imread(fileDIR+'.jpg')
image = imutils.resize(image, width=1000)

# Changing color scale to gray
gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
# cv.imshow('1 - Grayscale version', gray)
# cv.waitKey(0)

# Blur
gray = cv.bilateralFilter(gray,  40, 25, 25)
# cv.imshow("2 - Bilateral version", gray)
# cv.waitKey(0)

# Drawing Contours with Canny algorythm
edged = cv.Canny(gray, 170,200)
# cv.imshow("3 - Canny",edged)
# cv.waitKey(0)

# Find Countours
cnts, new = cv.findContours(edged.copy(), cv.RETR_LIST, cv.CHAIN_APPROX_SIMPLE)

# Draw Contours
img1 = image.copy()
cv.drawContours(img1, cnts,-1,(0,255), 3)
# cv.imshow("4 - Canny All contours",img1)
# cv.waitKey(0)

# Find rectangular shape with adjusted side to side ratio
findings = 0
method = 0

for c in cnts:
    peri =cv.arcLength(c,True)
    approx= cv.approxPolyDP(c, 0.02* peri, True)
    if len(approx) == 4:
        NumberPlatCnt = approx
        x, y, w, h, =cv.boundingRect(c)
        diagonalpow2 = pow(w,2)+pow(h,2)

        if w > 165 and h > 36 and w > (3 * h) and w < (5 * h) and w < 300 and h < 50: #Jednorzędowe tablice dla samochodów oraz przyczep	520 x 114 mm =>4:1
            new_img=image[y:y+h, x:x+w]
            print(w, h)
            findings = findings + 1
            method = 1
            name = 'Found plate ' + str(findings)
            print(name)
            # cv.imshow(name, new_img)
            # cv.waitKey(0)
            cv.imwrite(fileDIR+'_byShape_plate.jpg', new_img)
            break
#
# for 1 meter distance  -  if w>300 and h>60 and w > (3* h)and w < (5 * h) and diagonalpow2 < (pow(h,2) + pow(w, 2) + 20) and diagonalpow2 > (pow(h,2) + pow(w, 2) - 20):
# for 2 meter distance  -  if w>165 and h>36 and w > (3* h)and w < (5 * h) and diagonalpow2 < (pow(h,2) + pow(w, 2) + 20) and diagonalpow2 > (pow(h,2) + pow(w, 2) - 20):

#print("Znaleziono ",findings, " elementow za pomoca detekcji ksztaltu")
findings_color = 0

# if the plates weren't found by shape detection, we try using color detection based on blue color on the left side of the plates
if findings == 0:
    ## Formating by color blue (BLUE,110-255 GREEN,20-160 RED 0-60)
    # Creating a color mask to check the image for specified color, the mask was calculated for MIN and MAX value check for 10 images
    upperColor = (255, 160, 80)
    lowerColor = (110, 20, 0)
    upper = np.array(upperColor, dtype='uint8')
    lower = np.array(lowerColor, dtype='uint8')

    colorMask = cv.inRange(image, lower, upper)

    # Now the do an AND operation using our colorMask
    output = cv.bitwise_and(image, image, mask = colorMask)

    # cv.imshow('Color Image', output)
    # cv.waitKey(0)

    # Shifting the blue areas do gray scale
    grayBlueField = cv.cvtColor(output, cv.COLOR_BGR2GRAY)

    # Finding contours, basiclly we are checkin where the blue areas were
    cnts, new = cv.findContours(grayBlueField, cv.RETR_LIST, cv.CHAIN_APPROX_NONE)

    # for every contouer we try to creat a Rectanglur object, if we succesed that will give us the location of the plate than we create a new image base on that location. We create 2 image because we don't know the distance beetwen the car and camera
    for c in cnts:
        findings_color = findings_color + 1
        method = 2
        x, y, w, h, = cv.boundingRect(c)
        temp = image[y:y+ h+20, x:x + w + 20]
        plates_1m = image[y-60:y + 40, x-15:x + 400]
        plates_2m = image[y-25:y + 15, x-5:x + 195]
        cv.imwrite(fileDIR + '_byColor_1m_plate.jpg', plates_1m)
        cv.imwrite(fileDIR + '_byColor_2m_plate.jpg', plates_2m)
        # cv.imshow('Plates for 1m distance', plates_1m)
        # cv.waitKey(0)
        # cv.imshow('Plates for 2m distance', plates_2m)
        # cv.waitKey(0)
        break

# OCR

if method == 0:
    print("Nie znaleziono tablicy")
else:
    print("Znaleziono ", findings, " elementow za pomoca detekcji kształtu, ", findings_color, " za pomoca dektencji koloru")
    if method == 1:
        processedImgDIR = fileDIR + '_byShape_plate.jpg'
        image = cv.imread(processedImgDIR)
        result_a = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
        result_a = cv.bilateralFilter(result_a, 40, 25, 25)
        reta, result_a = cv.threshold(result_a, 120, 255, cv.THRESH_BINARY)
        cv.imshow("End image in gray 1", result_a)
        cv.waitKey(0)
        a = pytesseract.image_to_string(result_a)
        print('Tablica za pomocą detekcji ksztaltu: ', a)
    elif method == 2:
        processedImgDIR = fileDIR + '_byColor_1m_plate.jpg'
        image = cv.imread(processedImgDIR)
        result_a = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
        result_a = cv.bilateralFilter(result_a, 40, 25, 25)
        reta, result_a = cv.threshold(result_a, 120, 255, cv.THRESH_BINARY)
        cv.imshow("End image in gray 1", result_a)
        cv.waitKey(0)
        a = pytesseract.image_to_string(result_a)
        processedImgDIR = fileDIR + '_byColor_2m_plate.jpg'
        image = cv.imread(processedImgDIR)
        result_b = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
        result_b = cv.bilateralFilter(result_b, 40, 25, 25)
        retb, result_b = cv.threshold(result_b, 120, 255, cv.THRESH_BINARY)
        cv.imshow("End image in gray 2", result_b)
        cv.waitKey(0)
        b = pytesseract.image_to_string(result_b)
        if len(a) >= len(b):
            print('Tablica za pomoca detekcji koloru: ', a)
        else:
            print('Tablica za pomoca detekcji koloru: ', b)