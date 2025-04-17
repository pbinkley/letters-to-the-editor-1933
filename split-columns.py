import cv2

def split_columns(image):
    img = cv2.imread(image, 0)
    bitonal = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY)

    # Split the image into one-pixel-wide images along the x-axis

    for x in range(len(bitonal)):
        black = 0
        import pdb; pdb.set_trace()
        for y in range(img.rows):
            pixel = x[y][0]
            import pdb; pdb.set_trace() 


    # Iterate over the contours and extract each column
    i = 1
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        
        print(f"{i}: {x}, {y}, {w}, {h}")

        # Extract the columns from the source image
        col1 = img[y:y+h, 0:x]
        col2 = img[y:y+h, x:x+w]
        col3 = img[y:y+h, x+w:]
        
        # Save each column as a separate image file
        cv2.imwrite(f"column1_{i}.jpg", col1)
        cv2.imwrite(f"column2_{i}.jpg", col2)
        cv2.imwrite(f"column3_{i}.jpg", col3)
        i += 1
        
    return None

split_columns("raw_images/1933-03-04_letters.jpg")
