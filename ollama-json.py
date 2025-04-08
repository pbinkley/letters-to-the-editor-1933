from ollama import chat
from pydantic import BaseModel
import json
import sys
import os
from pathlib import Path
import time

# based on https://ollama.com/blog/structured-outputs

class Letter(BaseModel):
  Author: str
  Address: str
  Subjects: list[str]
  Summary: str
  DocType: str

class Names(BaseModel):
  Names: list[object]

class LetterListMeta(BaseModel):
  letters: list[Letter]

class LetterListNames(BaseModel):
  letters: list[Names]

def get_response(prompt, listClass):
  response = chat(
    model='olmo2',
    # options = {"num_ctx": 5120},
    messages=[
      { 
        'role': 'system', 
        'content': 'You are a helpful assistant. You pay close attention to your instructions and follow them precisely. You do not make up answers.'
      },
      {
        'role': 'user', 
        'content': prompt
      }
    ],
    format=listClass.model_json_schema(),
  )
  return response

input_text_file = sys.argv[1] # e.g. raw_text/1933-03-01_letters.txt
if input_text_file == '':
  sys.exit("Provide a filename like 'raw_text/1933-03-01_letters.txt'")

print(f"Opening {input_text_file}")

p = Path(input_text_file)
filename = p.with_suffix('').name # extract filename and strip extension

with open('prompt_meta.txt', 'r') as file:
    prompt_meta = file.read()
with open('prompt_names.txt', 'r') as file:
    prompt_names = file.read()
with open(input_text_file, 'r') as file:
    ocr_text = file.read()

# loop through letters, 
# which are separated by empty lines

letters_json = []
letters = ocr_text.split("\n\n")
print(f"There are {len(letters)} letters.")

for letter in letters:

  start = time.time()

  paragraphs = letter.partition('\n')
  words = len(letter.split())
  title = paragraphs[0]
  print(f"Letter: {title} ({words} words)")

  # prompt template ends with <OCR text>
  letter_meta_prompt = prompt_meta.replace("<OCR text>", f"\n\"\"\"\n{letter}\n\"\"\"")

  response = get_response(letter_meta_prompt, LetterListMeta)

  letter_data = json.loads(response['message']['content'])['letters'][0]
  letter_data['Text'] = paragraphs
  letter_data['Title'] = title.title()

  # now do the names

  # prompt template ends with <OCR text>
  letter_names_prompt = prompt_names.replace("<OCR text>", f"\n\"\"\"\n{letter}\n\"\"\"")

  response = get_response(letter_names_prompt, LetterListNames)

  letter_data['Names'] = []
  for letter in json.loads(response['message']['content'])['letters']:
    for name in letter['Names']:
      letter_data['Names'].append(name)

#  import pdb; pdb.set_trace()


  letters_json.append(letter_data)

  elapsed = time.time() - start
  print(f"  elapsed time: {round(elapsed, 1)} sec")

#  import pdb; pdb.set_trace()

# Writing to json file
print(f"Writing to {filename}.json")
with open(f"output_json/{filename}.json", "w") as outfile:
  outfile.write(json.dumps(letters_json, indent=2))