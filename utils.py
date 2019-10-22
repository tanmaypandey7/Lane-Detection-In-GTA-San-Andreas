import numpy as np
import cv2
import time
from directkeys import PressKey, W, A, S, D
import warnings
warnings.filterwarnings("ignore")


def canny(image):
    gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    canny = cv2.Canny(blur, 50, 150)
    return canny


def display_lines(image, lines):
    line_image = np.zeros_like(image)
    if lines is not None:
        for line in lines:
            if line is not None:
                x1, y1, x2, y2 = line.reshape(4)
                try:
                    cv2.line(line_image, (x1, y1), (x2, y2), (255, 0, 0), 10)
                except OverflowError:
                    pass

    return line_image


def roi(image):
    # replace object in np.array(<object>)
    # full res [[(100,900),(1600,700),(700,250)]]
    # windowed [[(200, 420), (900, 400), (500, 30)]]
    # first-person [[(10, 635), (10, 400), (430, 290), (800, 400), (800, 635)]]
    polygons = np.array(
        [[(10, 635), (10, 400), (430, 290), (800, 400), (800, 635)]])
    mask = np.zeros_like(image)
    cv2.fillPoly(mask, polygons, 255)
    masked_image = cv2.bitwise_and(image, mask)
    return masked_image


def make_coordiantes(image, lines):
    try:
        slope, intercept = lines
        y1 = image.shape[0]
        y2 = int(y1 * 3 / 5)
        x1 = int((y1 - intercept) / slope)
        x2 = int((y2 - intercept) / slope)
        return np.array([x1, y1, x2, y2])
    except BaseException:
        pass


def average_slope_intercept(image, lines):
    left_fit = []
    right_fit = []
    try:
        for line in lines:
            x1, y1, x2, y2 = line.reshape(4)
            coordinates = np.polyfit((x1, x2), (y1, y2), 1)
            slope = coordinates[0]
            intercept = coordinates[1]
            if slope > 0:
                right_fit.append((slope, intercept))
            else:
                left_fit.append((slope, intercept))
        left_fit_avg = np.average(left_fit, axis=0)
        right_fit_avg = np.average(right_fit, axis=0)
        left_line = make_coordiantes(image, left_fit_avg)
        right_line = make_coordiantes(image, right_fit_avg)
        try:
            return np.array([left_line, right_line])
        except IndexError:
            pass
    except TypeError:
        pass


def process_img(image):
    try:
        lane_image = np.copy(image)
        canny_image = canny(lane_image)
        cropped_image = roi(canny_image)
        lines = cv2.HoughLinesP(cropped_image, cv2.HOUGH_PROBABILISTIC,
                                np.pi / 180, 100, np.array([]), minLineLength=30, maxLineGap=15)
        average_lines = average_slope_intercept(lane_image, lines)
        line_image = display_lines(lane_image, average_lines)
        combo = cv2.addWeighted(lane_image, 0.7, line_image, 1, 1)
        return combo
    except TypeError:
        pass
