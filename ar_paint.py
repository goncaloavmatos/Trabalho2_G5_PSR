#!/usr/bin/python3
import argparse
import json
import cv2
import numpy as np
from colorama import Fore, Style, Back
import math

# ========================================================
# ........... Function: DISTANCE BETWEEN POINTS ..........
# ========================================================


def calculate_distance(point1, point2):
    x1, y1 = point1[0], point1[1]
    x2, y2 = point2[0], point2[1]
    dist = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
    return dist

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

    if len(centroids) == 1:  # If no object is detected, put marker on the origin
        centroid = (0, 0)
        reality = False
    else:
        centroid = centroids[1]  # Save the largest object's centroid as a tuple
        reality = True
    centroid = (int(round(centroid[0])), int(round(centroid[1])))

    return centroid, reality

# ========================================================
# .................. Function: PAINTING...................
# ========================================================


def draw_on_whiteboard(img, marker_coord, val, painting_true, brush_size):
    global previous_point
    dist = calculate_distance(previous_point, marker_coord)

    if painting_true and dist < 25 and val:

        img = cv2.circle(img, marker_coord, brush_size, colour, -1)
        img = cv2.line(img, previous_point, marker_coord, colour, brush_size+5)
        previous_point = marker_coord

    else:

        previous_point = marker_coord


    return img

colour = (255, 0, 0)


# =================================================================================================
# ............................................. MAIN FUNCTION .....................................
# =================================================================================================


def main():

    # ========================================================
    # .................INITIALIZATION ........................
    # ========================================================

    global colour
    global previous_point
    # ..............Specify file directory....................

    parser = argparse.ArgumentParser()
    parser.add_argument('-j', '--json', type=str, required=True, help='Full path to json file.')
    args = vars(parser.parse_args())
    color_segment = args['json']

    # ................ Presentation .........................

    print(Fore.LIGHTBLUE_EX + Style.BRIGHT + '\n            AUGMENTED REALITY PAINT' + Style.RESET_ALL)
    print('___________________________________________________')


    # .............. Get limits.json .........................

    with open(color_segment, "r") as f:  # opens and reads the json file
        ranges = json.load(f)  # saves the dictionary as ranges

    #  Print the imported dictionary
    print('\nUse an object within the color limits you segmented as a marker.\nYour imported limits are:\n')

    print(Fore.RED + Style.BRIGHT + 'R: ' + Style.RESET_ALL)
    print(ranges['limits']['r'])

    print(Fore.GREEN + Style.BRIGHT + 'G: ' + Style.RESET_ALL)
    print(ranges['limits']['g'])

    print(Fore.BLUE + Style.BRIGHT + 'B: ' + Style.RESET_ALL)
    print(ranges['limits']['b'])
    print('\n')

    # ................ Instruction ............................
    print(Style.BRIGHT + '\nINSTRUCTIONS:\n' + Style.RESET_ALL)
    print('"p" -> Start/stop painting\n\n'
          'Colours\n'
          '"r" -> Change color to red\n'
          '"g" -> Change color to green\n'
          '"b" -> Change color to blue\n'
          '"spacebar" -> Eraser\n\n'
          'Edit marker\n'
          '"+" -> make bigger\n'
          '"-" -> make smaller')

    print('\n\n\n Press "p" to start painting. Press it again to stop.\n\n')

    # Extracting minimums and maximums from ranges and saving as separate arrays
    mins = np.array([ranges['limits']['b']['min'], ranges['limits']['g']['min'], ranges['limits']['r']['min']])
    maxs = np.array([ranges['limits']['b']['max'], ranges['limits']['g']['max'], ranges['limits']['r']['max']])

    # ========================================================
    # .................PROCESSING IMAGE ......................
    # ========================================================
    cam = cv2.VideoCapture(0)
    ret, frame = cam.read()  # get an image from the camera

    # .............. Creating whiteboard with same size as shape ................

    whiteboard = np.zeros(frame.shape, dtype=np.uint8)  # Set whiteboard size as the size of the captured image
    whiteboard.fill(255)  # make every pixel white

    print('Press q to exit')

    # Specifying that at the start the user is not painting
    painting = False
    brush_size = 5
    previous_point = (0, 0)


    while True:

        # ........... initializing images and windows ..............................

        ret, frame = cam.read()  # get an image from the camera
        frame = cv2.flip(frame, 1)  # To make the image work like a mirror

        cv2.namedWindow('Capture', cv2.WINDOW_AUTOSIZE)
        cv2.namedWindow('Whiteboard', cv2.WINDOW_AUTOSIZE)
        cv2.namedWindow('Mask', cv2.WINDOW_AUTOSIZE)

        # ............Applying segmentation limits to create a mask ......................

        segmented_mask = cv2.inRange(frame, mins, maxs)
        cv2.imshow('Mask', segmented_mask)

        # ......................... Isolating Largest object ............................

        mask_largest = remove_small_objects(segmented_mask)
        cv2.imshow('Largest', mask_largest)

        # .......... Setting up the point that will draw in the whiteboard ...............

        # Getting the largest object's centroid coordinates
        centroid, val = get_centroid_largest(mask_largest)

        if centroid != (0, 0):
            # Showing marker in the original image
            frame = cv2.circle(frame, centroid, 5, (255, 0, 0), -1)

        pressed = cv2.waitKey(50)

        # To terminate
        if pressed & 0xFF == ord('q'):
            print('\n\nYou pressed "q" to quit, the program terminated.\n\n')
            break

        # ...................... Change colours .........................
        if pressed & 0xFF == ord('r'):
            colour = (0, 0, 255)
            print('\nCurrent colour: ' + Fore.RED + 'RED' + Style.RESET_ALL)

        if pressed & 0xFF == ord('g'):
            colour = (0, 255, 0)
            print('\nCurrent colour: ' + Fore.GREEN + 'GREEN' + Style.RESET_ALL)

        if pressed & 0xFF == ord('b'):
            colour = (255, 0, 0)
            print('\nCurrent colour: ' + Fore.BLUE + 'BLUE' + Style.RESET_ALL)

        if pressed & 0xFF == ord(' '):
            colour = (255, 255, 255)
            print('\nYou selected the ' + Fore.LIGHTMAGENTA_EX + 'ERASER' + Style.RESET_ALL)

        # ..................................................................

        # To clear the board
        if pressed & 0xFF == ord('c'):
            whiteboard = np.zeros(frame.shape, dtype=np.uint8)
            whiteboard.fill(255)  # or img[:] = 255
            print('\nCLEARED THE WHITEBOARD')

        # To start and stop painting
        if pressed & 0xFF == ord('p'):
            previous_point = centroid
            if painting is False:
                painting = True
                print('\nPAINTING...\n')
            else:
                painting = False
                print('\nNOT PAINTING.\n')

        # ....................... Changing brush size ......................

        if pressed & 0xFF == ord('+'):
            if brush_size == 45:  # To prevent brush size from getting above the maximum of 45
                brush_size = 45
                print(Fore.YELLOW + Style.BRIGHT + Back.RED + '\n'+' Brush size is already at the MAXIMUM' + Style.RESET_ALL)

            else:
                brush_size += 2

        if pressed & 0xFF == ord('-'):
            if brush_size == 1:  # To prevent brush size from getting below the minimum of 1
                brush_size = 1
                print(Fore.YELLOW + Style.BRIGHT + Back.RED + '\n'+' Brush size is already at the minimum' + Style.RESET_ALL)
            else:
                brush_size -= 2

        # ................Calling the function tha paints the whiteboard ................
        whiteboard = draw_on_whiteboard(whiteboard, centroid, val, painting, brush_size)

        # Showing images
        cv2.imshow('Capture', frame)
        cv2.imshow('Whiteboard', whiteboard)

    cam.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    main()
