import csv
from pathlib import PureWindowsPath, PurePosixPath

# copy page blocks from Zotero storage into the project directory

with open('ClevelandPressLetters_zotero.csv', newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        image_path = str(PurePosixPath(PureWindowsPath(row['File Attachments'])))
        image_path = image_path.replace("C:\\/Users/pbinkley", "/home/pbinkley/C")
        output_file = f"{row['Date']}_letters.jpg"
        print(f"cp '{image_path}' ./raw_images/{output_file}")
