#!/usr/bin/python3
import argparse
import json
import cv2
import numpy as np
from colorama import Fore, Style, Back
import math
import time

# ========================================================
# ........... Function: DISTANCE BETWEEN POINTS ..........
# ========================================================

# To help with Funcionalidade Avançada 1


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
# ...Function: GET LARGEST OBJECT'S CENTROID COORDINATES...
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

    return centroid, reality   # reality is just for debugging

# ========================================================
# .................. Function: PAINTING...................
# ========================================================
# Receives inputs and draws

def draw_on_whiteboard(img, marker_coord, val, painting_true, brush_size):
    global previous_point # The last point before the marker
    dist = calculate_distance(previous_point, marker_coord)

    # If we are painting and the distance between the 2 points isn't too big
    # And val is True (for debugging)

    # ............. Shake prevention ..........................
    # Only paints if the distance between points is small
    if usp:
        if painting_true and dist < 35 and val:

            # paints circle where the centroid is detected
            # divide brush size by to permit a radius of 1
            img = cv2.circle(img, marker_coord, int(brush_size/2), colour, -1)

            img = cv2.line(img, previous_point, marker_coord, colour, brush_size)  # unites close circles with line

            previous_point = marker_coord  # saves the current point to be the previous point in the next iteration

        else:
            # doesn't paint but saves the current point to be the previous point in the next iteration
            previous_point = marker_coord

    # ............. Without shake prevention ..........................
    # Paints with no regards of the distance between points
    else:

        if painting_true and val:

            # paints circle where the centroid is detected
            # divide brush size by to permit a radius of 1
            img = cv2.circle(img, marker_coord, int(brush_size / 2), colour, -1)

            img = cv2.line(img, previous_point, marker_coord, colour, brush_size)  # unites close circles with line

            previous_point = marker_coord  # saves the current point to be the previous point in the next iteration

        else:
            # doesn't paint but saves the current point to be the previous point in the next iteration
            previous_point = marker_coord

    return img

# ========================================================
# .......... Function: CURRENT DATE STRING................
# ========================================================
# To save image EX: drawing_Tue_Sep_15_10:36:39_2020.png

def current_date():
    named_tuple = time.localtime()  # get struct_time
    time_string = time.strftime("%a_%b_%d_%H:%M:%S_%Y", named_tuple)

    return time_string

# ========================================================
# .......... Advanced function 4................
# ========================================================

def numbered_paint():
    #For advanced function 4
    # img_contour = cv2.drawContours(img_nump, contours_nump_b, -1,(0,0,0), 3)
    dim = (frame.shape[1], frame.shape[0])
    img_nump_path = './teste.png'
    img_nump = cv2.resize(cv2.imread(img_nump_path, cv2.IMREAD_COLOR),dim)
    img_nump_b, img_nump_g, img_nump_r = cv2.split(img_nump)
    _,img_nump_b_tresh = cv2.threshold(img_nump_b,0,255,0)
    _,img_nump_g_tresh = cv2.threshold(img_nump_g,0,255,0)
    _,img_nump_r_tresh = cv2.threshold(img_nump_r,0,255,0)
    #Find contours for blue
    contours_nump_b, hierarchy = cv2.findContours(img_nump_b_tresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    for c in contours_nump_b:
        # calculate moments for each contour
        M = cv2.moments(c)
        # calculate x,y coordinate of center
        cX = int(M["m10"] / M["m00"])
        cY = int(M["m01"] / M["m00"])
        # add number 1 in the center position of each contour
        cv2.putText(whiteboard, "1", (cX, cY), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)
    contours_nump_g, hierarchy = cv2.findContours(img_nump_g_tresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    for c in contours_nump_g:
        # calculate moments for each contour
        M = cv2.moments(c)
        # calculate x,y coordinate of center
        cX = int(M["m10"] / M["m00"])
        cY = int(M["m01"] / M["m00"])
        # add number 1 in the center position of each contour
        cv2.putText(whiteboard, "1", (cX, cY), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)
    contours_nump_r, hierarchy = cv2.findContours(img_nump_r_tresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    for c in contours_nump_r:
        # calculate moments for each contour
        M = cv2.moments(c)
        # calculate x,y coordinate of center
        cX = int(M["m10"] / M["m00"])
        cY = int(M["m01"] / M["m00"])
        # add number 1 in the center position of each contour
        cv2.putText(whiteboard, "1", (cX, cY), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)
    global contours_2
    contours_2=np.append(np.append(contours_nump_b,contours_nump_g),contours_nump_r)
    pass




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
    parser.add_argument('-usp', '--use_shake_prevention', action='store_true', help='Prevents brush from drifting with big variations of the centroid.')
    parser.add_argument('-nump', '--numbered_paint', action='store_true', help='Enables the numbered paint mode')
    args = vars(parser.parse_args())
    color_segment = args['json']

    global usp
    usp = args['use_shake_prevention']
    global nump
    nump = args['numbered_paint']


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

    # ................ Instructions ............................
    print(Style.BRIGHT + '\nINSTRUCTIONS:\n' + Style.RESET_ALL)
    print('"p" -> Start/stop painting\n'
          '"q" -> Quit\n\n'
          'Colours\n'
          '"r" -> Change color to red\n'
          '"g" -> Change color to green\n'
          '"b" -> Change color to blue (Default)\n'
          '"spacebar" -> Eraser\n\n'
          'Edit brush size\n'
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
    global frame
    ret, frame = cam.read()  # get an image from the camera

    if nump:
        global whiteboard
        whiteboard = np.zeros(frame.shape, dtype=np.uint8)
        whiteboard.fill(255)
        numbered_paint()
        cv2.drawContours(whiteboard, contours_2, -1,(0,0,0), 3)
    else:
        # .............. Creating whiteboard with same size as shape ................
        whiteboard = np.zeros(frame.shape, dtype=np.uint8)  # Set whiteboard size as the size of the captured image
        whiteboard.fill(255)  # make every pixel white


    # ..................... Starting values ...................................
    # Specifying that at the start the user is not painting
    painting = False
    brush_size = 5
    previous_point = (0, 0)
    colour = (255, 0, 0) # To start with blue by default

    while True:

        # ........... initializing images and windows ..............................

        ret, frame = cam.read()  # get an image from the camera
        frame = cv2.flip(frame, 1)  # To make the image work like a mirror

        cv2.namedWindow('Capture', cv2.WINDOW_AUTOSIZE)
        cv2.moveWindow('Capture', 40, 30)
        cv2.namedWindow('Whiteboard', cv2.WINDOW_AUTOSIZE)
        cv2.moveWindow('Whiteboard', 720, 30)
        cv2.namedWindow('Mask', cv2.WINDOW_AUTOSIZE)
        cv2.moveWindow('Mask', 40, 600)
        cv2.namedWindow('Largest', cv2.WINDOW_AUTOSIZE)
        cv2.moveWindow('Largest', 720, 600)

        # ............Applying segmentation limits to create a mask ......................

        segmented_mask = cv2.inRange(frame, mins, maxs)
        cv2.imshow('Mask', segmented_mask)

        # ......................... Isolating Largest object ............................

        mask_largest = remove_small_objects(segmented_mask)
        cv2.imshow('Largest', mask_largest)

        # add a greenish shine on the original image where the object that paints is
        cv2.add(frame, (-10, 50, -10, 0), dst=frame, mask=mask_largest)

        # .......... Setting up the point that will draw in the whiteboard ...............

        # Getting the largest object's centroid coordinates
        centroid, val = get_centroid_largest(mask_largest)

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

        if centroid != (0, 0):
            # Showing marker in the original image
            #frame = cv2.circle(frame, centroid, 5, colour, -1)
            frame = cv2.putText(frame, 'x', (centroid[0]-10, centroid[1]+8), cv2.FONT_HERSHEY_PLAIN, 2, colour, 2)
        # ..................................................................

        # To clear the board
        if pressed & 0xFF == ord('c'):
            if nump:
                whiteboard = np.zeros(frame.shape, dtype=np.uint8)
                whiteboard.fill(100)
                numbered_paint()
            else:
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
            if brush_size == 55:  # To prevent brush size from getting above the maximum of 55
                brush_size = 55
                print(Fore.YELLOW + Style.BRIGHT + Back.RED + '\n'+' Brush size is already at the MAXIMUM' + Style.RESET_ALL)

            else:
                brush_size += 2

        if pressed & 0xFF == ord('-'):
            if brush_size == 1:  # To prevent brush size from getting below the minimum of 1
                brush_size = 1
                print(Fore.RED + Style.BRIGHT + Back.YELLOW + '\n'+' Brush size is already at the minimum' + Style.RESET_ALL)
            else:
                brush_size -= 2

        # ................Calling the function that paints the whiteboard ................
        whiteboard = draw_on_whiteboard(whiteboard, centroid, val, painting, brush_size)

        # Showing images
        cv2.imshow('Capture', frame)
        cv2.imshow('Whiteboard', whiteboard)


        # To save image EX: drawing_Tue_Sep_15_10:36:39_2020.png
        if pressed & 0xFF == ord('w'):

            save_string = "drawing_" + current_date() + ".png"
            cv2.imwrite(save_string, whiteboard)

            print('\nSaved image as: ' + Style.BRIGHT + Fore.LIGHTBLUE_EX + save_string + Style.RESET_ALL)

    cam.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    main()
