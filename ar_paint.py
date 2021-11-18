#!/usr/bin/python3
import argparse
import json
import cv2
import numpy as np


def main():
    # ............. Initialization ...........................

    # Specify file directory

    parser = argparse.ArgumentParser()
    parser.add_argument('-j', '--json', type=str, required=True, help='Full path to json file.')
    args = vars(parser.parse_args())

    # Get limits.json
    with open("limits.json", "r") as f:
        ranges = json.load(f)

    white_scr = np.zeros([600, 600, 1], dtype=np.uint8)
    white_scr.fill(255)

    cv2.imshow('White Screen', white_scr)
    print("image shape: ", white_scr.shape)

    cam = cv2.VideoCapture(0)

    print('Press q to exit')

    while True:
        ret, frame = cam.read()  # get an image from the camera

        cv2.namedWindow('Capture', cv2.WINDOW_AUTOSIZE)
        resized = cv2.resize(frame, (600, 600), interpolation=cv2.INTER_AREA)
        print("capture size: ", resized.shape)
        cv2.imshow('Capture', resized)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cam.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    main()
