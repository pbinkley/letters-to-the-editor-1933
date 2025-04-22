from google import genai
from google.genai import types

import PIL.Image
import os
import sys

# based on https://ai.google.dev/gemini-api/docs/vision?lang=python

with open('prompt_ocr.txt', 'r') as file:
    prompt_ocr = file.read()

input_image = sys.argv[1] # e.g. raw_images/1933-03-01_letters.jpg
if input_image == '':
  sys.exit("Provide a filename like 'raw_images/1933-03-01_letters.jpg'")

image = PIL.Image.open(input_image)

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

response = client.models.generate_content(
    model="gemini-2.0-pro-exp-02-05",
    config=types.GenerateContentConfig(
        system_instruction="You are a skilled reader of old newspaper texts. You are particularly careful in following the layout of newspaper columns. You would never mix the text of two different columns."),
    contents=[prompt_ocr, image])

# import pdb; pdb.set_trace()

print(f"Response:\n\n{response.text}")

output_file = input_image.replace("raw_images", "raw_text").replace(".jpg", ".txt")
overwrite = "Y"
if os.path.exists(output_file):
    overwrite = input("File exists; overwrite? (Y/N)")
if overwrite == 'Y':
    f = open(output_file, "w")
    f.write(response.text)
    f.close()
    print(f"Save to {output_file}")
