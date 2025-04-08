from ollama import chat
from pydantic import BaseModel
import json
import sys
import os
from pathlib import Path

# based on https://ollama.com/blog/structured-outputs

input_text_file = sys.argv[1] # e.g. raw_text/1933-03-01_letters.txt
if input_text_file == '':
  sys.exit("Provide a filename like 'raw_text/1933-03-01_letters.txt'")

print(f"Opening {input_text_file}")

p = Path(input_text_file)
filename = p.with_suffix('').name # extract filename and strip extension

class Letter(BaseModel):
  Author: str
  Address: str
  Subjects: list[str]
  Summary: str
  Names: list[object]
  DocType: str

class LetterList(BaseModel):
  letters: list[Letter]

with open('prompt_json.txt', 'r') as file:
    prompt = file.read()
with open(input_text_file, 'r') as file:
    ocr_text = file.read()

# loop through letters, 
# which are separated by empty lines

letters_json = []
letters = ocr_text.split("\n\n")
print(f"There are {len(letters)} letters.")
# import pdb; pdb.set_trace()

for letter in letters:

  paragraphs = letter.partition('\n')
  title = paragraphs[0]
  print("Letter: " + title)

  # prompt ends with <OCR text>
  letter_prompt = prompt.replace("<OCR text>", f"\n\"\"\"\n{letter}\n\"\"\"")

  response = chat(
      model='olmo2',
      messages=[
        { 
          'role': 'system', 
          'content': 'You are a helpful assistant. You pay close attention to your instructions and follow them precisely. You do not make up answers.'
        },
        {
          'role': 'user', 
          'content': letter_prompt
        }
      ],
      format=LetterList.model_json_schema(),
  )

  letter = json.loads(response['message']['content'])['letters'][0]
  letter['Text'] = paragraphs
  letter['Title'] = title.title()

  letters_json.append(letter)

#  import pdb; pdb.set_trace()

# Writing to json file
print(f"Writing to {filename}.json")
with open(f"output_json/{filename}.json", "w") as outfile:
  outfile.write(json.dumps(letters_json, indent=2))