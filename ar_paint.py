#!/usr/bin/python3
import argparse
import json
import cv2
import numpy as np
from colorama import Fore, Style

# ========================================================
# ...... Function: ISOLATE LARGEST OBJECT IN A MASK ......
# ========================================================


def remove_small_objects(mask):
    # find all your connected components (white blobs in your image)
    nb_components, output, stats, centroids = cv2.connectedComponentsWithStats(mask, connectivity=8)
    # connectedComponentswithStats yields every seperated component with information on each of them, such as size
    # the following part is just taking out the background which is also considered a component, but most of the time
    # we don't want that.
    sizes = stats[1:, -1]  # extracting size from cv2.connectedComponentsWithStats
    nb_components = nb_components - 1

    # your answer image
    mask_largest = mask
    # for every component in the image, you keep it if it's size is equal to the largest in sizes
    for i in range(0, nb_components):
        if sizes[i] != max(sizes) or sizes[i] < 200:  # I added the second condition because when no large object is
            # being detected, sometimes there are little objects that can be considered the largest ones,
            # even if they are very small. To prevent that,the mask with the largest objects will only show objects
            # with size bigger than 200
            mask_largest[output == i + 1] = 0

    return mask_largest

# ========================================================
# .... Function: GET LARGEST OBJECT CENTROID COORDINATES...
# ========================================================

def get_centroid_largest(mask_largest):
    # find all your connected components (white blobs in your image)
    nb_components, output, stats, centroids = cv2.connectedComponentsWithStats(mask_largest, connectivity=8)
    # connectedComponentswithStats yields every seperated component with information on each of them, such as size
    # the following part is just taking out the background which is also considered a component, but most of the time
    # we don't want that.
    # extracting size from cv2.connectedComponentsWithStats

    if len(centroids) == 1:
        centroid = (0, 0)
    else:
        centroid = centroids[1]

    return centroid[0], centroid[1]


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

    with open(color_segment, "r") as f:  # opens and reads the json file
        ranges = json.load(f)  # saves the dictionary as ranges

    #  Print the imported dictionary
    print('\nYour imported limits are:\n')

    print(Fore.RED + Style.BRIGHT + 'R: ' + Style.RESET_ALL)
    print(ranges['limits']['r'])

    print(Fore.GREEN + Style.BRIGHT + 'G: ' + Style.RESET_ALL)
    print(ranges['limits']['g'])

    print(Fore.BLUE + Style.BRIGHT + 'B: ' + Style.RESET_ALL)
    print(ranges['limits']['b'])
    print('\n')

    # Extracting minimums and maximums from ranges and saving as separate arrays
    mins = np.array([ranges['limits']['b']['min'], ranges['limits']['g']['min'], ranges['limits']['r']['min']])
    maxs = np.array([ranges['limits']['b']['max'], ranges['limits']['g']['max'], ranges['limits']['r']['max']])

    # ========================================================
    # .................PROCESSING IMAGE ......................
    # ========================================================
    cam = cv2.VideoCapture(0)

    print('Press q to exit')

    while True:

        # ........... initializing images and windows ..............................

        ret, frame = cam.read()  # get an image from the camera
        frame = cv2.flip(frame, 1) # To make the image work like a mirror

        cv2.namedWindow('Capture', cv2.WINDOW_AUTOSIZE)
        cv2.namedWindow('Whiteboard', cv2.WINDOW_AUTOSIZE)
        cv2.namedWindow('Mask', cv2.WINDOW_AUTOSIZE)

        # .............. Creating whiteboard with same size as shape ................

        whiteboard = np.zeros(frame.shape, dtype=np.uint8) # Set whiteboard size as the size of the captured image
        whiteboard.fill(255)  # make every pixel white

        #cv2.imshow('Capture', frame)
        #cv2.imshow('Whiteboard', whiteboard)

        # ............Applying segmentation limits to create a mask ......................

        segmented_mask = cv2.inRange(frame, mins, maxs)
        cv2.imshow('Mask', segmented_mask)

        # ......................... Isolating Largest object ............................

        mask_largest = remove_small_objects(segmented_mask)
        cv2.imshow('Largest', mask_largest)

        # .......... Setting up the point that will draw in the whiteboard ...............

        # Getting the largest object's centroid coordinates
        x_c, y_c = get_centroid_largest(mask_largest)
        centroid = (int(round(x_c)), int(round(y_c)))

        # Showing marker in the original image
        frame = cv2.circle(frame, centroid, 5, (255, 0, 0), -1)

        # Showing images
        cv2.imshow('Capture', frame)
        cv2.imshow('Whiteboard', whiteboard)


        # To terminate
        if cv2.waitKey(10) & 0xFF == ord('q'):
            break
    cam.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    main()
