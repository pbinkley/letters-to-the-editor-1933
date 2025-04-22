import cv2
import os
import sys

def split_columns(image):
    img = cv2.imread(image, 0)

    image_name = os.path.splitext(os.path.basename(image))[0]

    # import pdb; pdb.set_trace() 

    _, bitonal = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY)
    cv2.imwrite('bitonal.jpg', bitonal)
    height, width = bitonal.shape

    # Split the image into one-pixel-wide images along the x-axis

    gap_start = 0 # set to x when w find a black column
    column_start = -1 # set to gap_start when we find 300 non-black columns
    gaps = [] # store start and end of text columns

    for x in range(width):
        black = 0
        for y in range(height):
            if bitonal[y, x] == 255:
                black += 1
        if black >= 2700:
            # print(f"{x}: {black}")
            if column_start >= 0:
                # we have reached the end of a column
                gaps.append([column_start, x])
                column_start = -1
            elif x - gap_start > 100:
                # this is a text column
                column_start = gap_start
            gap_start = x
    print(gaps)
    # import pdb; pdb.set_trace() 

    c = 1
    for gap in gaps:
        column_image = img[0:height, gap[0]-10:gap[1]+20]
        cv2.imwrite(f"./column_images/{image_name}_column{str(c)}.jpg", column_image)
        c += 1

if not os.path.exists('./column_images'):
    os.makedirs('./column_images')
split_columns(f"raw_images/{sys.argv[1]}.jpg")
