import cv2
import numpy as np
import argparse
import imutils

# Automatic brightness and contrast optimization with optional histogram clipping
def abc(image, clip_hist_percent=0.1):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Calculate grayscale histogram
    hist = cv2.calcHist([gray],[0],None,[256],[0,256])
    hist_size = len(hist)

    # Calculate cumulative distribution from the histogram
    accumulator = []
    accumulator.append(float(hist[0]))
    for index in range(1, hist_size):
        accumulator.append(accumulator[index -1] + float(hist[index]))

    # Locate points to clip
    maximum = accumulator[-1]
    clip_hist_percent *= (maximum/100.0)
    clip_hist_percent /= 2.0

    # Locate left cut
    minimum_gray = 0
    while accumulator[minimum_gray] < clip_hist_percent:
        minimum_gray += 1

    # Locate right cut
    maximum_gray = hist_size -1
    while accumulator[maximum_gray] >= (maximum - clip_hist_percent):
        maximum_gray -= 1

    # Calculate alpha and beta values
    alpha = 255 / (maximum_gray - minimum_gray)
    beta = -minimum_gray * alpha

    auto_result = cv2.convertScaleAbs(image, alpha=alpha, beta=beta)
    return (auto_result, alpha, beta)

if __name__ == '__main__':
    #contruct argument parser
    ap = argparse.ArgumentParser()
    ap.add_argument("-i", "--image", help = "path to the image")
    ap.add_argument("-a", "--abc", default="no", help = "auto brightness and contrast clip histogram, ex. -a 0.1")
    ap.add_argument("-n", "--n_colors", default="2", help = "number of colors(min 2) for k-means, ex. -n 4")
    args = vars(ap.parse_args())

    if int(args["n_colors"]) < 2:
        args["n_colors"] = 2
        print("Error! colors number setting below 2. Defaulted to 2.")

    # load the image
    image = cv2.imread(args["image"])
    image = imutils.resize(image, height = 480, width = 640)
    if args["abc"] != "no":
        image, _, _= abc(image, clip_hist_percent=float(args["abc"]))

    average = image.mean(axis=0).mean(axis=0)

    pixels = np.float32(image.reshape(-1, 3))

    # set how many color to fetch
    nColors = int(args["n_colors"])
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 200, .1)
    flags = cv2.KMEANS_RANDOM_CENTERS

    x, labels, palette = cv2.kmeans(pixels, nColors, None, criteria, 10, flags)
    y, counts = np.unique(labels, return_counts=True)

    dominant = palette[np.argmax(counts)]


    if len(counts) >= 2:
        for i in range(len(palette)):
            tempPal = np.array([palette[i][0], palette[i][1], palette[i][2]])
            palette[i] = tempPal
            print("Color (BGR):", palette[i], "; Counts:", counts[i])
        print("Max:", palette[counts.argmax()], "Counts:", counts[counts.argmax()])
        print("Min:", palette[counts.argmin()], "Counts:", counts[counts.argmin()])
        
        print("Average:", np.array([average[0], average[1], average[2]]))
        print("Total pixel:", pixels.size)
        exit()
    else:
        print("Error! number of detected color below minimum")
        exit()