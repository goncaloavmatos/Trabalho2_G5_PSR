#!/usr/bin/python3
import argparse
import json
import copy
import cv2
import numpy as np
from colorama import Fore, Style, Back
import math
import time


# ========================================================
# ........... Function: DISTANCE BETWEEN POINTS ..........
# ========================================================

# distance between 2 points
def calculate_distance(point1, point2):
    x1, y1 = point1[0], point1[1]
    x2, y2 = point2[0], point2[1]
    dist = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
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

    return centroid, reality  # reality is just for debugging


# ========================================================
# .................. Function: PAINTING...................
# ========================================================
# Receives inputs and draws

def draw_on_whiteboard(img, marker_coord, val, painting_true, brush_size):
    global previous_point  # The last point before the marker
    dist = calculate_distance(previous_point, marker_coord)

    # If we are painting and the distance between the 2 points isn't too big
    # And val is True (for debugging)

    # ............. Shake prevention ..........................
    # Only paints if the distance between points is small
    if usp:
        if painting_true and dist < 50 and val:

            # paints circle where the centroid is detected
            # divide brush size by to permit a radius of 1
            img = cv2.circle(img, marker_coord, int(brush_size / 2), colour, -1)

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
def centroids_paint(contour_paint, number):
    for c in contour_paint:
        # Calculate moments for each contour
        M = cv2.moments(c)
        # Calculate x,y coordinate of center
        cX = int(M["m10"] / M["m00"])
        cY = int(M["m01"] / M["m00"])
        # Add number in the center position of each contour
        cv2.putText(whiteboard, str(number), (cX, cY), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)


def numbered_paint():
    dim = (frame.shape[1], frame.shape[0])  # Get video size from webcam
    img_nump_path = '/home/goncalo/catkin_ws/src/Trabalho2_G5_PSR/teste.png'  # Get image path
    img_nump = cv2.resize(cv2.imread(img_nump_path, cv2.IMREAD_COLOR), dim)  # Resize image
    img_nump_b, img_nump_g, img_nump_r = cv2.split(img_nump)  # Split image in blue, green and red
    # Binarize each color in the image
    global img_nump_b_tresh
    _, img_nump_b_tresh = cv2.threshold(img_nump_b, 0, 255, 0)
    global img_nump_g_tresh
    _, img_nump_g_tresh = cv2.threshold(img_nump_g, 0, 255, 0)
    global img_nump_r_tresh
    _, img_nump_r_tresh = cv2.threshold(img_nump_r, 0, 255, 0)
    # Find contours for blue
    contours_nump_b, hierarchy = cv2.findContours(img_nump_b_tresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    centroids_paint(contours_nump_b, 1)
    # Find contours for green
    contours_nump_g, hierarchy = cv2.findContours(img_nump_g_tresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    centroids_paint(contours_nump_g, 2)
    # Find contours for red
    contours_nump_r, hierarchy = cv2.findContours(img_nump_r_tresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    centroids_paint(contours_nump_r, 3)
    # Merge all contours
    global contours_2
    contours_2 = np.append(np.append(contours_nump_b, contours_nump_g), contours_nump_r)


def paint_pontuation(paint, paint_region):
    # pixels_total = np.count_nonzero(frame)  # Get the number of all the pixels in the image
    pixels_region = np.count_nonzero(paint_region)  # Get the number of pixels in the regions with a specific color
    pixels_right = np.count_nonzero(cv2.bitwise_and(paint, paint_region))  # Get the number of pixels in the right spot
    pixels_wrong = np.count_nonzero(cv2.bitwise_and(paint, cv2.bitwise_not(paint_region)))  # Get the number of
    # pixels in the wrong spot
    pixels_painted = pixels_right + pixels_wrong  # Amount of pixels painted with a specific color
    percentage_region_painted = round((pixels_right / pixels_region) * 100, 2)  # Percentage of a region painted with the right
    # color
    if pixels_painted != 0:
        percentage_accuracy = round((pixels_right / pixels_painted) * 100, 2)  # Accuracy
    else:
        percentage_accuracy = None
    return percentage_region_painted, percentage_accuracy

# ========================================================
# ............... FUNCTION: DRAW SHAPES ....................
# ========================================================


def draw_shape(coord, shape_param, img, img_temp, colour, thickness):

    if coord['mouse'] != (0, 0) and coord['p1'] != (0, 0):

        # If s is pressed, starts rectangle drawing sequence
        if shape_param['figure'] == 's':  # If s is pressed, starts rectangle drawing sequence

            # If only first press has been made
            if shape_param['p1'] and not shape_param['p2']:
                # first point: first press
                # second: variable centroid
                img_temp = cv2.rectangle(img_temp, coord['p1'], coord['mouse'], colour, thickness)

            # If there is a second press
            if shape_param['p1'] and shape_param['p2']:
                # first point: first press
                # second: second press
                img = cv2.rectangle(img, coord['p1'], coord['p2'], colour, thickness)

                # puts variables back to false, so that next press ir perceived as a first
                shape_param['p1'] = False
                shape_param['p2'] = False

        # If o is pressed, starts circle drawing sequence
        if shape_param['figure'] == 'o':

            # If only first press has been made
            if shape_param['p1'] and not shape_param['p2']:
                dist = int(calculate_distance(coord['p1'], coord['mouse']))
                img_temp = cv2.circle(img_temp, coord['p1'], dist, colour, thickness)
            # If there is a second press
            if shape_param['p1'] and shape_param['p2']:
                dist = int(calculate_distance(coord['p1'], coord['p2']))
                img = cv2.circle(img, coord['p1'], dist, colour, thickness)
                shape_param['p1'] = False
                shape_param['p2'] = False


    return img, img_temp, shape_param


# ========================================================
# ................ FUNCTION: COLORMASK ...................
# ========================================================


def colormask(img):
    mask_R = cv2.inRange(img, (0, 0, 0), (0, 0, 255))
    mask_G = cv2.inRange(img, (0, 0, 0), (0, 255, 0))
    mask_B = cv2.inRange(img, (0, 0, 0), (255, 0, 0))

    mask = cv2.bitwise_or(mask_R, mask_G)
    mask = cv2.bitwise_or(mask, mask_B)

    return mask


# =================================================================================================
# ............................................. MAIN FUNCTION .....................................
# =================================================================================================


def main():
    # ========================================================
    # .................INITIALIZATION ........................
    # ========================================================

    global colour
    global previous_point
    p1 = (320, 240)
    # ..............Arguments....................

    parser = argparse.ArgumentParser()
    parser.add_argument('-j', '--json', type=str, required=True, help='Full path to json file.')
    parser.add_argument('-usp', '--use_shake_prevention', action='store_true',
                        help='Prevents brush from drifting with big variations of the centroid.')
    parser.add_argument('-nump', '--numbered_paint', action='store_true',
                        help='Enables the numbered paint mode. Full path to the image')
    parser.add_argument('-fb', '--use_frame_as_board', action='store_true',
                        help='To draw on the capture frame image instead of the whiteboard.')
    args = vars(parser.parse_args())
    color_segment = args['json']

    global switch_board
    switch_board = args['use_frame_as_board']
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
          + Fore.RED + '"r"' + Style.RESET_ALL + ' -> Change color to '+Fore.RED+'red\n'+ Style.RESET_ALL +
          Fore.GREEN +'"g"' + Style.RESET_ALL + ' -> Change color to '+ Fore.GREEN +'green\n' + Style.RESET_ALL +
          Fore.BLUE +'"b"' + Style.RESET_ALL + ' -> Change color to '+ Fore.BLUE +'blue\n' + Style.RESET_ALL +
          '"spacebar" -> '+ Fore.LIGHTMAGENTA_EX +'Eraser\n\n' + Style.RESET_ALL +
          'Edit brush size\n'
          '"+" -> make bigger\n'
          '"-" -> make smaller\n\n'
          'GEOMETRIC SHAPES\n'
          '"s" -> start square, again to stop\n'
          '"o" -> circle center, again to stop')

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
        print('\nNUMBERED PAINT\n'
              'Paint the regions with the number ' + Fore.BLUE + '1 with blue\n' + Style.RESET_ALL +
              'Paint the regions with the number ' + Fore.GREEN + '2 with green\n' + Style.RESET_ALL +
               'Paint the regions with the number ' + Fore.RED + '3 with red\n' + Style.RESET_ALL)

        global whiteboard
        whiteboard = np.zeros(frame.shape, dtype=np.uint8)
        whiteboard.fill(255)
        numbered_paint()
        cv2.drawContours(whiteboard, contours_2, -1, (0, 0, 0), 3)
    else:
        # .............. Creating whiteboard with same size as shape ................
        whiteboard = np.zeros(frame.shape, dtype=np.uint8)  # Set whiteboard size as the size of the captured image
        whiteboard.fill(255)  # make every pixel white

    cv2.imshow('Whiteboard', whiteboard)
    # ..................... Starting values ...................................
    # Specifying that at the start the user is not painting
    painting = False
    brush_size = 5
    previous_point = (0, 0)
    colour = (255, 0, 0)  # To start with blue by default

    shape_coord = {'p1': None, 'p2': None, 'p3': None, 'mouse': None}

    square_param = {'p1': False, 'p2': False, 'figure': 's'}
    circle_param = {'p1': False, 'p2': False, 'figure': 'o'}
    #  elipse_param = {'p1': False, 'p2': False, 'p3': False, 'figure': 'e'}

    drawing_square = False
    drawing_circle = False
    #  drawing_elipse = False

    # =======================================================================================
    # .................................. CICLO WHILE .......................................
    # =======================================================================================

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

        whiteboard_temp = copy.deepcopy(whiteboard)

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
            # frame = cv2.circle(frame, centroid, 5, colour, -1)
            frame = cv2.putText(frame, 'x', (centroid[0] - 10, centroid[1] + 8), cv2.FONT_HERSHEY_PLAIN, 2, colour, 2)
        # ..................................................................


        # To clear the board
        if pressed & 0xFF == ord('c'):
            if nump:
                whiteboard = np.zeros(frame.shape, dtype=np.uint8)
                whiteboard.fill(255)
                numbered_paint()
            else:
                whiteboard = np.zeros(frame.shape, dtype=np.uint8)
                whiteboard.fill(255)  # or img[:] = 255
            print('\nCLEARED THE WHITEBOARD')

        # To start and stop painting
        if pressed & 0xFF == ord('p'):
            drawing_circle = False
            drawing_square = False
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
                print(
                    Fore.YELLOW + Style.BRIGHT + Back.RED + '\n' + ' Brush size is already at the MAXIMUM' + Style.RESET_ALL)

            else:
                brush_size += 2

        if pressed & 0xFF == ord('-'):
            if brush_size == 1:  # To prevent brush size from getting below the minimum of 1
                brush_size = 1
                print(
                    Fore.RED + Style.BRIGHT + Back.YELLOW + '\n' + ' Brush size is already at the minimum' + Style.RESET_ALL)
            else:
                brush_size -= 2

                # ========================================================
                # .........................SHAPES ........................
                # ========================================================

                # .......................... Shape selection ..............................

        if centroid != (0, 0):
            shape_coord['mouse'] = centroid

            if pressed & 0xFF == ord('s'):

                if not square_param['p1'] and val:  # start drawing square
                    shape_coord['p1'] = centroid  # save first point
                    square_param['p1'] = True
                    #elipse_param['p1'] = False
                    circle_param['p1'] = False

                elif square_param['p1'] and not square_param['p2'] and val:

                    shape_coord['p2'] = centroid
                    square_param['p2'] = True
                    print('\nYou drew a rectangle')

            if pressed & 0xFF == ord('o'):

                if not circle_param['p1'] and val:  # start drawing square

                    shape_coord['p1'] = centroid  # save first point
                    square_param['p1'] = False
                    #elipse_param['p1'] = False
                    circle_param['p1'] = True

                elif circle_param['p1'] and not circle_param['p2'] and val:

                    shape_coord['p2'] = centroid
                    circle_param['p2'] = True
                    print('\nYou drew a circle')

            # ................ Detecting if a shape is being painted ................

            if square_param['p1']:
                drawing_square = True

            if circle_param['p1']:
                drawing_circle = True

            #if (elipse_param['p1'] and not elipse_param['p2']) or (elipse_param['p1'] and elipse_param['p2'] and not elipse_param['p3']):
                drawing_elipse = True

            # ................Calling the function that paints the whiteboard ................
            if drawing_square:
                painting = False
                whiteboard, whiteboard_temp, square_param = draw_shape(shape_coord, square_param, whiteboard, whiteboard_temp, colour, brush_size)


                if switch_board:

                    mask_switch = colormask(whiteboard_temp)
                    frame[mask_switch > 0] = whiteboard_temp[mask_switch > 0]
                    cv2.imshow('Capture', frame)

                else:
                    cv2.imshow('Whiteboard', whiteboard_temp)

            if drawing_circle:
                painting = False
                whiteboard, whiteboard_temp, circle_param = draw_shape(shape_coord, circle_param, whiteboard, whiteboard_temp, colour, brush_size)


                if switch_board:

                    mask_switch = colormask(whiteboard_temp)
                    frame[mask_switch > 0] = whiteboard_temp[mask_switch > 0]
                    cv2.imshow('Capture', frame)

                else:
                    cv2.imshow('Whiteboard', whiteboard_temp)

            if not drawing_square and not drawing_circle:

                whiteboard = draw_on_whiteboard(whiteboard, centroid, val, painting, brush_size)

                if switch_board:

                    mask_switch = colormask(whiteboard)
                    frame[mask_switch > 0] = whiteboard[mask_switch > 0]
                    cv2.imshow('Capture', frame)

                else:
                    whiteboard = draw_on_whiteboard(whiteboard, centroid, val, painting, brush_size)

                    cv2.imshow('Whiteboard', whiteboard)

        if switch_board:

            mask_switch = colormask(whiteboard)
            frame[mask_switch > 0] = whiteboard[mask_switch > 0]

        # Showing images
        cv2.imshow('Capture', frame)

        # To save image EX: drawing_Tue_Sep_15_10:36:39_2020.png
        if pressed & 0xFF == ord('w'):
            save_string = "/home/goncalo/catkin_ws/src/Trabalho2_G5_PSR/drawing_" + current_date() + ".png"
            cv2.imwrite(save_string, whiteboard)

            print('\nSaved image in: ' + Style.BRIGHT + Fore.LIGHTBLUE_EX + save_string + Style.RESET_ALL)

    cam.release()
    cv2.destroyAllWindows()

    # ------ Paint rating ------
    if nump:
        while True:
            try:
                rate_question = str(input('Do you want to rate your painting? (y or n) \n'))
            except ValueError:
                continue

            if str(rate_question) != 'y' and str(rate_question) != 'n':
                print('Wrong input! You typed ' + str(rate_question) + ' and you must type y or n')
                print(rate_question)
                continue
            else:
                break
        if rate_question == 'y':
            whiteboard[np.where((whiteboard == [255, 255, 255]).all(axis=2))] = [0, 0, 0]
            paint_b, paint_g, paint_r = cv2.split(whiteboard)
            if paint_pontuation(paint_b, img_nump_b_tresh)[1] == None:
                print('You did not paint in blue')
            else:
                print('You painted ' + str(paint_pontuation(paint_b, img_nump_b_tresh)[0]) + '% of the blue region with ' +
                      str(paint_pontuation(paint_b, img_nump_b_tresh)[1]) + '% of accuracy')
            if paint_pontuation(paint_g, img_nump_g_tresh)[1] == None:
                print('You did not paint in green')
            else:
                print('You painted ' + str(paint_pontuation(paint_g, img_nump_g_tresh)[0]) + '% of the green region with ' +
                      str(paint_pontuation(paint_g, img_nump_g_tresh)[1]) + '% of accuracy')
            if paint_pontuation(paint_r, img_nump_r_tresh)[1] == None:
                print('You did not paint in red')
            else:
                print('You painted ' + str(paint_pontuation(paint_r, img_nump_r_tresh)[0]) + '% of the red region with ' +
                      str(paint_pontuation(paint_r, img_nump_r_tresh)[1]) + '% of accuracy')


if __name__ == '__main__':
    main()