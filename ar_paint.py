#!/usr/bin/python3
import argparse
import json
import copy
import cv2
import numpy as np


def main():
    # ............. Initialization ...........................

    # Specify file directory

    parser = argparse.ArgumentParser()
    parser.add_argument('-j', '--json', type=str, required=True, help='Full path to json file.')
    args = vars(parser.parse_args())


    global image
    capture = cv2.VideoCapture(0)
    window_name = 'Capture'
    cv2.namedWindow(window_name, cv2.WINDOW_AUTOSIZE)


    print(image)
    white_scr = np.zeros([512, 512, 1], dtype=np.uint8)
    white_scr.fill(255)

    cv2.imshow('White Screen', white_scr)
    print("image shape: ", white_scr.shape)

    # Get limits.json
    with open("limits.json", "r") as f:
        ranges = json.load(f)
    # print(ranges)



    while True:
        _, image = capture.read()  # get an image from the camera

        cv2.imshow(window_name, image)

        cv2.waitKey(0)


if __name__ == '__main__':
    main()
