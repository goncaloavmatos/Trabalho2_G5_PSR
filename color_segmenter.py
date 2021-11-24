#!/usr/bin/python3

import argparse
import cv2
import numpy as np
import json
from colorama import Fore, Back, Style

# ............... Global Variables ................................

minBH = 0
maxBH = 255
minGS = 0
maxGS = 255
minRV = 0
maxRV = 255


# .................. Trackbar callback functions ....................
# These functions change each limit according to changes in their respective trackbars

def onTrackbarMinBH(val):
    global minBH
    minBH = val


def onTrackbarMaxBH(val):
    global maxBH
    maxBH = val


def onTrackbarMinGS(val):
    global minGS
    minGS = val


def onTrackbarMaxGS(val):
    global maxGS
    maxGS = val


def onTrackbarMinRV(val):
    global minRV
    minRV = val


def onTrackbarMaxRV(val):
    global maxRV
    maxRV = val

# ..................................... MAIN FUNCTION ......................................

def main():

    # ............. Initialization ...........................
    window_original = 'Original'
    window_segment = 'Color segmenter'
    global image
    # ................ Presentation .........................

    print(Fore.LIGHTBLUE_EX + Style.BRIGHT + '\n            COLOR SEGMENTER' + Style.RESET_ALL)
    print('___________________________________________________\n')
    print('Use the trackbars to change the limits\n\n'
          'Press:\n'
          'q - quit the programme;\n'
          'w - save the limits in a file (limits.json) and quit the programme.\n')

    # ............... Input arguments .........................

    parser = argparse.ArgumentParser()
    parser.add_argument('-hsv', action='store_true', help='To use HSV image. Default is RGB.')  # To use HSV instead of rgb
    args = vars(parser.parse_args())

    # .............. Processing input image .....................

    cap = cv2.VideoCapture(0)  # Load live image
    cv2.namedWindow(window_original, cv2.WINDOW_AUTOSIZE)
    cv2.moveWindow(window_original, 40, 30)
    cv2.namedWindow(window_segment, cv2.WINDOW_AUTOSIZE)
    cv2.moveWindow(window_segment, 700, 30)


    # ................Create Trackbars...............................................

    if args['hsv']:

        cv2.createTrackbar('Min H', window_segment, 0, 100, onTrackbarMinBH)
        cv2.createTrackbar('Max H', window_segment, 100, 100, onTrackbarMaxBH)
        cv2.createTrackbar('Min S', window_segment, 0, 100, onTrackbarMinGS)
        cv2.createTrackbar('Max S', window_segment, 100, 100, onTrackbarMaxGS)
        cv2.createTrackbar('Min V', window_segment, 0, 100, onTrackbarMinRV)
        cv2.createTrackbar('Max V', window_segment, 100, 100, onTrackbarMaxRV)

    else:

        cv2.createTrackbar('Min B', window_segment, 0, 255, onTrackbarMinBH)
        cv2.createTrackbar('Max B', window_segment, 255, 255, onTrackbarMaxBH)
        cv2.createTrackbar('Min G', window_segment, 0, 255, onTrackbarMinGS)
        cv2.createTrackbar('Max G', window_segment, 255, 255, onTrackbarMaxGS)
        cv2.createTrackbar('Min R', window_segment, 0, 255, onTrackbarMinRV)
        cv2.createTrackbar('Max R', window_segment, 255, 255, onTrackbarMaxRV)

    # .............Assigning limits selected with the trackbars.......................

    while True:
        _, image = cap.read()
        image = cv2.flip(image, 1)  # To make the image work like a mirror
        cv2.imshow(window_original, image)

        if args['hsv']:  # To change from BGR to HSV, if requested
            image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

        if not args['hsv']:
            ranges = {'limits': {'b': {'min': minBH, 'max': maxBH},
                                 'g': {'min': minGS, 'max': maxGS},
                                 'r': {'min': minRV, 'max': maxRV}}}

            # Process image
            mins = np.array([ranges['limits']['b']['min'], ranges['limits']['g']['min'], ranges['limits']['r']['min']])
            maxs = np.array([ranges['limits']['b']['max'], ranges['limits']['g']['max'], ranges['limits']['r']['max']])
            Mask = cv2.inRange(image, mins, maxs)
            cv2.imshow(window_segment, Mask)

        else:
            ranges = {'limits': {'h': {'min': minBH, 'max': maxBH},
                                 's': {'min': minGS, 'max': maxGS},
                                 'v': {'min': minRV, 'max': maxRV}}}

            # Process image
            mins = np.array([ranges['limits']['h']['min'], ranges['limits']['s']['min'], ranges['limits']['v']['min']])
            maxs = np.array([ranges['limits']['h']['max'], ranges['limits']['s']['max'], ranges['limits']['v']['max']])
            Mask = cv2.inRange(image, mins, maxs)
            cv2.imshow(window_segment, Mask)


        pressed_key = cv2.waitKey(1)

        # ............... termination routine ..............

        if pressed_key == ord('q'):
            print('Pressed q to terminate.')
            break

            # ............. printing limits .....................

        if pressed_key == ord('w'):
            file_name = 'limits.json'
            with open(file_name, 'w') as file_handle:
                print('\n\nSaving dictionary with the current limits...')
                json.dump(ranges,  file_handle)
                print('\n\nLimits saved in file: ' + Fore.LIGHTBLUE_EX + 'limits.json\n\n' + Style.RESET_ALL)
            break

if __name__ == '__main__':
    main()