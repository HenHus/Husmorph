import cv2
import numpy as np
import os
import csv

'''
This script processes images in a specified folder, detects lines using Hough Transform, and draws the LONGEST LINE FOUND in each image.

It batch processes images in a folder, calculates the pixel-to-mm ratio based on a known length of a scale bar, and saves the results in a CSV file.

If no line is found, it uses the last known valid line.
'''


# Using euclidean distance to calculate the angle
def calculate_angle(x1, y1, x2, y2):
    return np.arctan2(y2 - y1, x2 - x1) * 180 / np.pi

# Processing function
def process_image(file_path, last_valid_line):
    image = cv2.imread(file_path)

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    '''
    These values will depend on the image characteristics.
    You may need to adjust them for your specific images and scale bar, because I cannot predict how different scale bars will look like.
    
    The GaussianBlur kernel size (5, 5) is used to reduce noise and improve edge detection.
    The Canny edge detection thresholds (100, 200) are set to detect strong edges.
    The dilation kernel size (3, 3) is used to close gaps in the edges.
    The Hough Transform parameters are set to detect lines with a minimum length of 500 pixels and a maximum gap of 200 pixels.
    The threshold is set to 1000, but this would need to be changed depending on your setup and the scale bar.

    The other values are set to detect lines that are not too steep (between -30 and 30 degrees), 
    and to ignore lines that are too long (greater than 1000 pixels).
    '''
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blurred, 100, 200, apertureSize=3)
    kernel = np.ones((3, 3), np.uint8)
    dilated_edges = cv2.dilate(edges, kernel, iterations=4)
    lines = cv2.HoughLinesP(dilated_edges, 1, np.pi/180, threshold=1000, minLineLength=500, maxLineGap=200)

    longest_line = None
    max_length = 0

    if lines is not None:
        lines = np.squeeze(lines, axis=1)
        for line in lines:
            x1, y1, x2, y2 = line
            length = np.sqrt((x2 - x1)**2 + (y2 - y1)**2)
            angle = calculate_angle(x1, y1, x2, y2)
            # Checking if the line is within the  angle range
            if -30 <= angle <= 30 and length > max_length:
                max_length = length

    # Use valid current line if length is within limits, else use last valid
    if 0 < max_length <= 1000:
        return max_length / known_length_mm, max_length 
    elif last_valid_length is not None:
        return last_valid_length / known_length_mm, last_valid_length
    else:
        return "NA", None

# Add your folder path here
folder_path = 'path_to_your_folder_here'

# CSV file to store results
csv_file = "calibration_to_mm.csv"

known_length_mm = 30  # Known length in mm


last_valid_length = None

with open(csv_file, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['Filename', 'px/mm'])

    for filename in sorted(os.listdir(folder_path)):
        file_path = os.path.join(folder_path, filename)
        if os.path.isfile(file_path) and filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tif', '.tiff')):
            base_filename = os.path.splitext(filename)[0]
            px_per_mm, new_valid_length = process_image(file_path, last_valid_length)
            if new_valid_length is not None:
                last_valid_length = new_valid_length
            writer.writerow([base_filename, px_per_mm])

cv2.destroyAllWindows()