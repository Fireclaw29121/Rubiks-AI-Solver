### IMPORT ###
import time
import cv2
import numpy as np

### FUNC ###

def guidelines(image:np.array) -> np.array:
    '''
    A function that applies guidelines to a raw image.

    Input:
    image (np.array):               A raw RGB image of a face of a Rubik's Cube.

    Output:
    image_guidelines (np.array):    A copy of image with guidelines over its center portion.

    Guidelines are placed using a cropping algorithm identical to identify_stickers.
    '''
    # Get the dimensions to crop the image to its center plus some bound of error, adjusted dynamically by resolution.
    imgheight, imgwidth, depth = np.shape(image)
    
    image_guidelines = np.copy(image)
    WHITE = [255, 255, 255]

    if imgwidth >= imgheight:
        larger_side = imgwidth
        smaller_side = imgheight

        border_top  = (smaller_side)//8
        border_side = (larger_side)//2-3*border_top
        center_width = 6*border_top

        # Horizontal borders.

        # Top
        image_guidelines[border_top][border_side:border_side+center_width] = WHITE

        # Thirds
        image_guidelines[border_top+center_width//3][border_side:border_side+center_width] = WHITE
        image_guidelines[border_top+2*center_width//3][border_side:border_side+center_width] = WHITE

        # Bottom 
        image_guidelines[border_top+center_width][border_side:border_side+center_width] = WHITE

        # Vertical borders.

        # Left
        image_guidelines[border_top:border_top+center_width,border_side] = WHITE

        # Thirds
        image_guidelines[border_top:border_top+center_width,border_side+center_width//3] = WHITE
        image_guidelines[border_top:border_top+center_width,border_side+2*center_width//3] = WHITE

        # Right
        image_guidelines[border_top:border_top+center_width,border_side+center_width] = WHITE

    elif imgwidth < imgheight:
        larger_side = imgheight
        smaller_side = imgwidth

        border_side  = (smaller_side)//8
        border_top = (larger_side)//2-3*border_side
        center_width = 6*border_side

        # Horizontal borders.

        # Top
        image_guidelines[border_top][border_side:border_side+center_width] = WHITE

        # Thirds
        image_guidelines[border_top+center_width//3][border_side:border_side+center_width] = WHITE
        image_guidelines[border_top+2*center_width//3][border_side:border_side+center_width] = WHITE

        # Bottom 
        image_guidelines[border_top+center_width][border_side:border_side+center_width] = WHITE

        # Vertical borders.

        # Left
        image_guidelines[border_top:border_top+center_width,border_side] = WHITE

        # Thirds
        image_guidelines[border_top:border_top+center_width,border_side+center_width//3] = WHITE
        image_guidelines[border_top:border_top+center_width,border_side+2*center_width//3] = WHITE

        # Right
        image_guidelines[border_top:border_top+center_width,border_side+center_width] = WHITE

    return image_guidelines

def detect_edges(image:np.array) -> np.array:
    '''
    A function that applies Canny Edge Detection to an image.

    Input:
    image (np.array):   An RGB image.

    Output:
    canny (np.array):   A 1-bit color array of the edges in image.

    image is converted to grayscale, and Gaussian Blur is applied in order to reduce noise.
    Canny is then applied to the denoised image.
    '''
    # convert the image to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # apply GaussianBlur to reduce noise
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    
    # apply Canny edge detection
    canny = cv2.Canny(blurred, 50, 150)
    
    return canny

def is_rubik_square(contour:np.array, center_width:int) -> bool:
    '''
    A function that looks at a given contour and determines whether or not it is the acceptable size and type for a Rubik's Cube sticker.

    Inputs:
    contour (np.array):     An array of [x,y] points in some image that define the boundary of a region.
    center_width:           The INTENDED width of the square center region, in pixels. This value is determined from the height of the original raw photo.

    Output:
    bool:                   Evaluates to True if contour has an accaptable area and is closed; otherwise, False.
    '''
    # If the area of contour is within a given margin of error (+/- 1/3 of the expected length)...
    if cv2.contourArea(contour) >= (center_width/3-center_width/9)**2 and cv2.contourArea(contour) <= (center_width/3+center_width/9)**2:
        # Return True if the contour is closed; otherwise, return False.
        return np.allclose(contour[0], contour[-1], 30, 30)
    else:
        return False
    
def identify_stickers(image:np.array) -> tuple[np.array, list]:
    '''
    A function that identifies the stickers on one face of a Rubik's Cube.

    Input:
    image (np.array):           An RGB image that is a raw photo of one face of the Rubik's Cube. 

    Outputs:
    imagee2 (np.array):         image, after dynamic cropping and basic adjustments have been applied to it.
    sticker_contours (list):    A list of the contours; these contours are the boundaries of the stckers.

    image is dynamically cropped to a center square plus one-eighth of the length of the largest side.
    Canny edge detection is applied using detect_edges, and cv2.findContours finds the contours that could correspond to stickers.

    The contours are processed using is_rubik_square, and then they are sorted by size. 
    The nine largest (which will be the Rubik's cube stickers) are returned, along with the cropped version of image
    '''

    # Get the dimensions to crop the image to its center plus some bound of error, adjusted dynamically by resolution.
    imgheight, imgwidth, depth = np.shape(image)

    if imgwidth >= imgheight:
        larger_side = imgwidth
        smaller_side = imgheight

        border_top  = (smaller_side)//8
        border_side = (larger_side)//2-3*border_top
        true_center_width = 4*border_top
        center_width = 6*border_top

    elif imgwidth < imgheight:
        larger_side = imgheight
        smaller_side = imgwidth

        border_side  = (smaller_side)//8
        border_top = (larger_side)//2-3*border_side
        true_center_width = 4*border_side
        center_width = 6*border_side

    # Crop the image to the above dimensions.
    image_cropped = np.copy(image)
    image_cropped = image_cropped[border_top:border_top+center_width, border_side:border_side+center_width]

    # Detect edges in the image.
    edges = detect_edges(image_cropped)
    contours, hierarchy = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

    # Find all valid contours; sort them by size.
    closed_contours = []

    for contour in contours:
        if is_rubik_square(contour, true_center_width):
            closed_contours.append(contour)
        
    sorted_contours = sorted(closed_contours, key=cv2.contourArea, reverse=True)

    # Get the largest nine contours of this list.
    sticker_contours = sorted_contours[:9]

    return image_cropped, sticker_contours

def correct_labels(image_cropped:np.array, sticker_contours:list, display:bool) -> list[tuple[int, int]]:
    '''
    A function that takes cropped of a face of a Rubik's Cube and the locations of its stickers generated by identify_stickers, 
    which labels the stickers to a standard format:

    [0][1][2]
    [3][4][5]
    [6][7][8]

    In this format, 4 is the center, 1 is the top-left corner, etc.

    Inputs:
    image_cropped (np.array):           The RGB image of the Rubik's Cube. It must be cropped to a square by identify_stickers in order for this algorithm to function.
    sticker_contours (list):            A list of the contours that are the stickers of the Rubik's Cube, also generated by identify_stickers.

    Output:
    label_key (list[tuple[int,int]]):   A list containing tuples of the square number and the index in sticker_contours for each contour in sticker_contours.
    
    '''
    # Preparation and coordinate generation for point tests. 
    point_tests = []
    label_key = []
    standard_length = len(image_cropped)
    for y_coord_ind in range(3):
        for x_coord_ind in range(3):
            x_coord = standard_length//4*(x_coord_ind+1)
            y_coord = standard_length//4*(y_coord_ind+1)                
            point_tests.append((x_coord,y_coord))
    
    # Test each point with each contour; one should fit for each.
    for (cntindex, contour) in enumerate(sticker_contours):
        for (ptindex, point) in enumerate(point_tests):
            if cv2.pointPolygonTest(contour, point, False) > 0:
                label_key.append((ptindex, cntindex))

    if display:
        # Display the contours on the image if specified.
        image_cropped_overwrite=np.copy(image_cropped)
        for ptindex, cntindex in label_key:
            moments = cv2.moments(sticker_contours[cntindex])
            contour_x = int(moments['m10']/moments['m00'])
            contour_y = int(moments['m01']/moments['m00'])
            cv2.putText(image_cropped_overwrite, text=str(ptindex+1), org=(contour_x, contour_y), fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=1, color=(255,255,255), thickness=2, lineType=cv2.LINE_AA)
            cv2.drawContours(image_cropped_overwrite, list(sticker_contours[cntindex]), -1, color=(33,237,255))
            cv2.imshow('Labeled', image_cropped_overwrite)

    return label_key

######## MAIN ########
if __name__=="__main__":
    # Initialize the camera object.
    cam = cv2.VideoCapture(1)
    result, image = cam.read()

    # Time delay to allow the shutter to autofocus.
    time.sleep(0.5)

    while result:
        # Capture video frame by frame
        result, image = cam.read()

        # Place guidelines on a copy of the image.
        image_guidelines = guidelines(image)

        # Display the resulting copy.
        cv2.imshow('VIDEO FEED', image_guidelines)
        
        # Use Q to quit.
        if cv2.waitKey(81)  == ord('q'):
            break

        # Use P to capture and process images.
        if cv2.waitKey(80) == ord('p'):

            image_cropped, sticker_contours = identify_stickers(image)

            label_key = correct_labels(image_cropped, sticker_contours, True)

    # After the loop, release the camera object.
    cam.release()

    # Destroy all windows.
    cv2.destroyAllWindows()