#!/usr/bin/python3
import argparse
import json
import cv2
import numpy as np
from pprint import pprint
from colorama import Fore, Style

def main():
    # ========================================================
    # .................INITIALIZATION ........................
    # ========================================================

    # ..............Specify file directory....................

    parser = argparse.ArgumentParser()
    parser.add_argument('-j', '--json', type=str, required=True, help='Full path to json file.')
    args = vars(parser.parse_args())
    color_segment = args['json']

    # .............. Get limits.json .........................

    with open(color_segment, "r") as f:
        ranges = json.load(f)

    print('\nYour imported limits are:\n')

    print(Fore.RED + Style.BRIGHT + 'R: ' + Style.RESET_ALL)
    print(ranges['limits']['r'])

    print(Fore.GREEN + Style.BRIGHT + 'G: ' + Style.RESET_ALL)
    print(ranges['limits']['g'])

    print(Fore.BLUE + Style.BRIGHT + 'B: ' + Style.RESET_ALL)
    print(ranges['limits']['b'])
    print('\n')

    cam = cv2.VideoCapture(0)


    print('Press q to exit')

    while True:
        ret, frame = cam.read()  # get an image from the camera

        cv2.namedWindow('Capture', cv2.WINDOW_AUTOSIZE)

        whiteboard = np.zeros(frame.shape, dtype=np.uint8) # Set whiteboard size as the size of the captured image
        whiteboard.fill(255)  # make every pixel white

        cv2.imshow('Capture', frame)
        cv2.imshow('Whiteboard', whiteboard)

        if cv2.waitKey(10) & 0xFF == ord('q'):
            break
    cam.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    main()
