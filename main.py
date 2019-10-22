from utils import process_img
import cv2
import numpy as np
from PIL import ImageGrab


def main():
    while True:
        screen = np.array(ImageGrab.grab(bbox=(40, 16, 750, 550)))
        try:
            new_screen = process_img(screen)
            cv2.imshow('window', new_screen)
            if cv2.waitKey(25) & 0xFF == ord('q'):
                cv2.destroyAllWindows()
                break
        except TypeError:
            pass

main()
