import tensorflow as tf
from tf_bodypix.api import download_model, load_model, BodyPixModelPaths
import cv2
from matplotlib import pyplot as plt
import numpy as np
import urllib.request
import sys
import os
import time
import json

# -------------------input url to return image-------------------#
def url_to_image(url):
    resp = urllib.request.urlopen(url)
    image = np.asarray(bytearray(resp.read()), dtype="uint8")
    image = cv2.imdecode(image, cv2.IMREAD_COLOR)
    return image


path = "\public\images"
finalpath = os.getcwd() + path
os.chdir(finalpath)
img = url_to_image(sys.argv[1])

# -------------------import tensorflow library-------------------#
bodypix_model = load_model(
    download_model(BodyPixModelPaths.MOBILENET_FLOAT_50_STRIDE_16)
)

# -------------------resize-------------------#
scale = img.shape[0] / 500
width = int(img.shape[1] / scale)
height = 500
dim = (width, height)
resized = cv2.resize(img, dim, interpolation=cv2.INTER_AREA)

# -------------------mask-------------------#
result = bodypix_model.predict_single(resized)
mask = result.get_mask(threshold=0.1).numpy().astype(np.uint8)
mask[mask > 0] = cv2.GC_PR_FGD
mask[mask == 0] = cv2.GC_BGD

# -------------------define bg fg array---------------------#
fgModel = np.zeros((1, 65), dtype="float")
bgModel = np.zeros((1, 65), dtype="float")

# -------------------run grabCut---------------------#
start = time.time()

(mask, bgModel, fgModel) = cv2.grabCut(
    resized, mask, None, bgModel, fgModel, iterCount=5, mode=cv2.GC_INIT_WITH_MASK
)

end = time.time()

# -------------------post-process mask---------------------#
outputMask = np.where((mask == cv2.GC_BGD) | (mask == cv2.GC_PR_BGD), 0, 1)
outputMask = (outputMask * 255).astype("uint8")

cv2.imwrite("testimage.jpg", outputMask)

# -------------------measurements---------------------#
newimage = cv2.imread("testimage.jpg")
lineimage = cv2.imread("testimage.jpg")

# -------------------input different height---------------------#
width = newimage.shape[1]


def findMeasurements(height):
    leftboundary = [0]
    rightboundary = [0]
    widths = []
    blackwidths = []
    measurements = []
    j = 0
    k = 0
    continued = True

    while continued:
        # find left boundary
        for i in range(rightboundary[j], width):
            if (newimage[height, i][0] == 255) & continued:
                leftboundary.append(i)
                k += 1
                break

            if i == width - 1:
                continued = False

        # find right boundary
        for i in range(leftboundary[k], width):
            if (newimage[height, i][0] == 0) & continued:
                rightboundary.append(i)
                j += 1
                break

            if i == width - 1:
                continued = False

    for i in range(1, len(rightboundary)):
        widths.append(rightboundary[i] - leftboundary[i])

    for i in range(1, len(leftboundary)):
        blackwidths.append(leftboundary[i] - rightboundary[i - 1])
    blackwidths.append(width - rightboundary[-1])

    for i in range(1, len(leftboundary)):
        cv2.line(
            lineimage,
            (leftboundary[i], height),
            (rightboundary[i], height),
            (255, 0, 0),
            5,
        )

    measurements.append(widths)
    measurements.append(blackwidths)
    measurements.append(leftboundary)
    measurements.append(rightboundary)
    return measurements


def findMax(width):
    max = [0, 0]
    max[0] = width[0]
    for i in range(0, len(width)):
        if width[i] > max[0]:
            max[0] = width[1]
            max[1] = i
    return max


levels = [int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])]

# create 2d arrays of measurements
smeasure = findMeasurements(levels[0])
wmeasure = findMeasurements(levels[1])
hmeasure = findMeasurements(levels[2])

# include max values to measurement array
smeasure.append(findMax(smeasure[0]))
wmeasure.append(findMax(wmeasure[0]))
hmeasure.append(findMax(hmeasure[0]))

# cv2.imwrite("newimage.jpg", newimage)
cv2.imwrite("lineimage.jpg", lineimage)

# -------------------check accuracy---------------------#
swthres = 0.55
shthres = 0.80
hwthres = 0.55


def checkAccuracy(smeasure, wmeasure, hmeasure):
    # 0 represents accurate, 1 represents inaccurate
    accuracy = [0, 0, 0]
    max = [smeasure[4][0], wmeasure[4][0], hmeasure[4][0]]

    for i in range(0, 3):
        # check if the value is equal zero
        if max[i] == 0:
            accuracy[i] = 1

    # compare left and right boundaries of assumed swh,
    # i assume that the smaller(left) or larger(right) measurement is the correct one
    if max[0] / max[1] < swthres or max[0] / max[2] < shthres:
        accuracy[0] = 1

    if max[1] / max[0] < swthres or max[1] / max[2] < hwthres:
        accuracy[1] = 1

    if max[2] / max[0] < shthres or max[2] / max[1] < hwthres:
        accuracy[2] = 1

    return accuracy


accuracy = checkAccuracy(smeasure, wmeasure, hmeasure)

# -------------------make corrections---------------------#


def makeCorrections(accuracy, measure, width):
    corrected = measure
    newmax = measure[4]
    newwidths = []

    if accuracy == 1:
        white = measure[0]
        black = measure[1]
        maxI = newmax[1]

        wrongBlack = [0, 0]

        left = [black[maxI], maxI]
        right = [black[maxI + 1], maxI + 1]

        if left[1] == 0:
            wrongBlack = right
        elif right[1] == len(black) - 1:
            wrongBlack = left

        # check if left or right black has a larger value
        else:
            if left[0] < right[0]:
                wrongBlack = left
            else:
                wrongBlack = right

        # corrections to max val and corrected array
        if wrongBlack == left:
            # corrections to max val
            newmax[0] = newmax[0] + left[0] + white[maxI - 1]
            newmax[1] = maxI - 1

            # corrections to blackwidths
            corrected[1].pop(left[1])

            # corrections to left/right boundary
            corrected[2].pop(maxI + 1)
            corrected[3].pop(maxI)

        else:
            newmax[0] = newmax[0] + right[0] + white[maxI + 1]
            newmax[1] = maxI

            corrected[1].pop(right[1])

            corrected[2].pop(maxI + 2)
            corrected[3].pop(maxI + 1)

        # corrections to widths
        for i in range(1, len(corrected[3])):
            newwidths.append(corrected[3][i] - corrected[2][i])

        # make final changes to corrected array
        corrected[0] = newwidths
        corrected[4] = newmax

    return corrected


# -----loop accuracy and corrections-----#

while accuracy != [0, 0, 0]:
    smeasure = makeCorrections(accuracy[0], smeasure, width)
    wmeasure = makeCorrections(accuracy[1], wmeasure, width)
    hmeasure = makeCorrections(accuracy[2], hmeasure, width)
    accuracy = checkAccuracy(smeasure, wmeasure, hmeasure)

# create a corrected array for bodyshape calculator
corrected = [smeasure[4], wmeasure[4], hmeasure[4]]

swratio = corrected[0][0] / corrected[1][0]
whratio = corrected[1][0] / corrected[2][0]

# -------------------calc body shapes---------------------#


def bodyShape(corrected, gender):
    shoulder = corrected[0][0]
    waist = corrected[1][0]
    hip = corrected[2][0]

    swratio = shoulder / waist
    whratio = waist / hip
    shratio = shoulder / hip

    # used for rectangle comparison (within 5% of each other)
    # find largest values
    rmax = findMax(corrected)[0]
    # include other vals
    rvals = []
    for i in corrected:
        if i != max:
            rvals.append(i)

    # used for hourglass comparison (hips and shoulders within 5% of each other)
    if shoulder > hip:
        hgval = [shoulder, hip]
    else:
        hgval = [hip, shoulder]

    # determine body shape
    if gender:

        if shratio <= 0.96:
            # male-oval
            if whratio > 0.9:
                shape = 4
            # male-triangle
            else:
                shape = 1

        # male-inverted-triangle
        elif swratio > 1.6:
            shape = 0

        # male-trapezoid
        elif swratio > 1.5:
            shape = 3

        # rectangle
        else:
            shape = 2

    else:
        # female-inverted-triangle
        if shoulder / hip > 1.05:
            shape = 0

        # female-pear
        elif hip / shoulder >= 1.05:
            shape = 1

        # female-rectangle
        elif swratio < 1.33 and rvals[0] > 0.95 * rmax and rvals[1] > 0.95 * rmax:
            shape = 2

        # female-hourglass
        elif swratio >= 1.33 and whratio <= 0.75 and hgval[1] >= 0.95 * hgval[0]:
            shape = 3

        # female-apple
        else:
            shape = 4

    return shape


def capitalise(string):
    if string == "true":
        return True
    return False


x = {
    "bodyshape": bodyShape(corrected, capitalise(sys.argv[5])),
    "shoulder": corrected[0][0],
    "waist": corrected[1][0],
    "hips": corrected[2][0],
    "swratio": round(float(swratio), 2),
    "whratio": round(float(whratio), 2),
}
y = json.dumps(x)
print(y)
