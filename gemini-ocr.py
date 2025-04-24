from google import genai
from google.genai import types

from PIL import Image
import os
import sys

# based on https://note.nkmk.me/en/python-pillow-concat-images/

def get_concat_v_resize(im1, im2, resample=Image.BICUBIC, resize_big_image=True):
    _im1 = im1.resize((im2.width, int(im1.height * im2.width / im1.width)), resample=resample)
    _im2 = im2
    dst = Image.new('L', (_im1.width, _im1.height + _im2.height))
    dst.paste(_im1, (0, 0))
    dst.paste(_im2, (0, _im1.height))
    return dst

# based on https://ai.google.dev/gemini-api/docs/vision?lang=python

with open('prompt_ocr.txt', 'r') as file:
    prompt_ocr = file.read()

date = sys.argv[1] # e.g. 1933-03-01
if date == '':
  sys.exit("Provide a date like '1933-03-01'")

text_blocks = 3
text = ''

for column_num in range(1, text_blocks+1):
    print(f"Column {column_num}")
    input_image = f"column_images/{date}_letters_column{column_num}.jpg"
    image = Image.open(input_image)

    if column_num == 1:
        # add the three-column-wide headline (column0) to the top, resized
        headline_image = f"column_images/{date}_letters_column0.jpg"
        image = get_concat_v_resize(Image.open(headline_image), image)

    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

    response = client.models.generate_content(
        # model="gemini-2.0-pro-exp-02-05",
        model="gemini-2.0-flash",
        config=types.GenerateContentConfig(
            system_instruction="You are a skilled reader of old newspaper texts. You never invent, generate or hallucinate text that is not found in the image you are processing."),
        contents=[prompt_ocr, image])

    # import pdb; pdb.set_trace()

    print(f"Response:\n\n{response.text}")
    text += response.text # TODO handle +++

text = text.replace("+++", "")

output_file = f"raw_text/{date}_letters.txt"
overwrite = "Y"
if os.path.exists(output_file):
    overwrite = input("File exists; overwrite? (Y/N)")
if overwrite == 'Y':
    f = open(output_file, "w")
    f.write(text)
    f.close()
    print(f"Saved to {output_file}")
