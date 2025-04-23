import cv2
import os
import sys
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# run:  python3 split-columns.py 1933-03-07_letters

def split_columns(image):
    print()
    print(f"Image: {image}")
    img = cv2.imread(image, 0)

    image_name = os.path.splitext(os.path.basename(image))[0]

    # import pdb; pdb.set_trace() 

    _, bitonal = cv2.threshold(img, 100, 255, cv2.THRESH_BINARY)
    # cv2.imwrite('bitonal.jpg', bitonal)
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
    chop = max_black - 100
    column_count = 0
    while column_count < 3:
        print(f"Checking {chop}")
        gap_start = 0 # set to x when w find a black column
        column_start = -1 # set to gap_start when we find 300 non-black columns
        gaps = [] # store start and end of text columns
        for x in range(width):
            black = blackness[x]
            if black >= chop:
                # print(f"{x}: {black}")
                if column_start >= 0:
                    # we have reached the end of a text column
                    gaps.append([column_start, x])
                    print(f"column width: {x - column_start}")
                    column_start = -1
                elif x - gap_start > 100:
                    # this is a text column - we have a lot of non-black pixel columns in a row
                    column_start = gap_start
                gap_start = x
        column_count = len(gaps)
        print(f"columns: {column_count}")
        chop = chop - 100

    print(gaps)
    # import pdb; pdb.set_trace() 

    plt.ylabel('black pixels')
    # plt.show() # display visualization

    c = 1
    for gap in gaps:
        # show the areas of text columns as rectangles on visualization
#        column = patches.Rectangle((0,height), gap[1]-gap[0], 30, linewidth=5, edgecolor='r', facecolor='none')
#        plt.add_patch(column)

        print(f"{gap[0]-10},{gap[1]+20}")
        left_side = gap[0]-10 if gap[0] >= 10 else 0
        right_side = gap[1]+20
        column_image = img[0:height, left_side:right_side]
        cv2.imwrite(f"./column_images/{image_name}_column{str(c)}.jpg", column_image)
        c += 1


if not os.path.exists('./column_images'):
    os.makedirs('./column_images')
split_columns(f"raw_images/{sys.argv[1]}.jpg")
