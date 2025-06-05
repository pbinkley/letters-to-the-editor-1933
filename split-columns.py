import cv2
import os
import sys
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import json

# run:  python3 split-columns.py 1933-03-07_letters

def split_columns(image, column_crops):
    print()
    print(f"Image: {image} Date: {issue_date}")
    img = cv2.imread(image, 0)

    image_name = os.path.splitext(os.path.basename(image))[0]

    # import pdb; pdb.set_trace() 

    # split off heading at 175
    heading_height = 175
    height, width = img.shape
    print(f"image height: {height}")
    heading = img[0:heading_height, 0:width]
    print(f"heading: {heading.shape}")
    cv2.imwrite(f"./column_images/{image_name}_column0.jpg", heading)

    # further processing is on the image without the heading, just the three columns
    img = img[heading_height:height, 0:width]
    print(f"body: {img.shape}")

    _, bitonal = cv2.threshold(img, 100, 255, cv2.THRESH_BINARY)
    height, width = bitonal.shape

    # Split the image into one-pixel-wide images along the x-axis

    blackness = []
    max_black = 0
    for x in range(width): # iterate through 1-pixel columns
        black = 0
        for y in range(height):
            # count black pixels in column
            if bitonal[y, x] == 255:
                black += 1
        blackness.append(black)
        if black > max_black: # discover the column with the highest number of black pixels
            max_black = black
        plt.scatter(x, black) # visualization

    print(f"max: {max_black}")
    chop = max_black - 25
    column_count = 0
    while (column_count != 3) and (chop > 0):
        print(f"Checking {chop}")
        gap_start = 0 # set to x when w find a black column
        column_start = -1 # set to gap_start when we find 100 non-black columns
        gaps = [] # store start and end of text columns
        for x in range(width):
            black = blackness[x]
            if black >= chop:
                # print(f"{x}: {black}")
                if column_start >= 0:
                    # we have reached the edge of a text column
                    gaps.append([column_start, x])
                    print(f"column width: {x - column_start}")
                    column_start = -1
                elif x - gap_start > 100:
                    # this is a text column - we have a lot of non-black pixel columns in a row
                    column_start = gap_start
                gap_start = x
        column_count = len(gaps)
        print(f"columns: {column_count}")
        chop = chop - 25

    print(gaps)
    # import pdb; pdb.set_trace() 

    plt.ylabel('black pixels')
    # plt.show() # display visualization

    c = 1
    for gap in gaps:
        # show the areas of text columns as rectangles on visualization
#        column = patches.Rectangle((0,height), gap[1]-gap[0], 30, linewidth=5, edgecolor='r', facecolor='none')
#        plt.add_patch(column)

        print(f"Column {c}: {gap[0]-10},{gap[1]+20}")
        # incorporate column_crops here: 
        # use to set the bottom of each column, instead of height
        if c <= 3:
            h = height if column_crops[c - 1] == 0 else column_crops[c - 1] - heading_height
            # h = h - heading_height # allow for cropped heading
            print(f"column crop {c}: {column_crops[c - 1]}; height: {h}")
            # left and right sides of column
            left_side = gap[0]-10 if gap[0] >= 10 else 0 # can't have negative number
            right_side = gap[1]+20
            column_image = img[0:h, left_side:right_side]
            cv2.imwrite(f"./column_images/{image_name}_column{str(c)}.jpg", column_image)
            c += 1

if not os.path.exists('./column_images'):
    os.makedirs('./column_images')

# Open and read the JSON file
with open('column-cropping-data.json', 'r') as jsonfile:
    column_crops = json.load(jsonfile)

filename = sys.argv[1]
issue_date = filename.split('_')[0]

split_columns(f"raw_images/{filename}.jpg", column_crops[issue_date])
