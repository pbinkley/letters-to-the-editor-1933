from ollama import chat
from pydantic import BaseModel
import json
import sys
import os
from pathlib import Path
import time
import re

# based on https://ollama.com/blog/structured-outputs

class Letter(BaseModel):
  author: str
  address: str
  subjects: list[str]
  summary: str
  doctype: str

class Entities(BaseModel):
  entities: list[object]

class LetterListMetadata(BaseModel):
  letters: list[Letter]

class LetterListEntities(BaseModel):
  letters: list[Entities]

def is_title_line(text):
  # check for two capital letters together, so as not to be fooled
  # by initials in signature of a letter  
  if re.search(r'[A-Z]{2}', text) and not re.search(r'[a-z]', text):
      return True
  else:
      return False

def get_response(prompt, listClass):
  response = chat(
    model='olmo2',
    options = {"num_ctx": 4096},
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

try:
  input_text_file = sys.argv[1] # e.g. raw_text/1933-03-01_letters.txt
except:
  sys.exit("Provide a filename like 'raw_text/1933-03-01_letters.txt'")

print(f"Opening {input_text_file}")

p = Path(input_text_file)
filename = p.with_suffix('').name # extract filename and strip extension

with open('prompt_metadata.txt', 'r') as file:
    prompt_metadata = file.read()
with open('prompt_entities.txt', 'r') as file:
    prompt_entities = file.read()
with open(input_text_file, 'r') as file:
    ocr_text = file.read()

# loop through letters, 
# which are now separated by multiline titles in all caps
# so: when find matching line start new letter, unless 
# the line follows another matching line (i.e. is the second
# line of a title)

letters_json = []
letters = []

previous_title = ""
current_title = ""
current_letter = []
title_open = True

for counter, line in enumerate(ocr_text.splitlines()):
  if counter == 0:
    # put first line in all caps so will be treated as title
    line = line.upper()
  is_title = is_title_line(line) # the line is in all-caps
  # print(f"line {counter} ({is_title}): {line}")
  if (is_title):
    if title_open:
      if current_title != "":
        current_title += " "
      current_title += f"{line}" # append this line to current title
    elif len(current_letter) > 0:
      # close and store letter
      # print(f"Store letter: {current_title} ({len(current_letter)} lines)")
      letters.append([current_title, ''] + current_letter)
      current_letter = []
      # start a new letter
      previous_title = current_title
      current_title = line
      title_open = True
  else: # append text line to current letter
    title_open = False # we're inside the letter text now
    current_letter.append(line)
else:
  # print(f"Store letter: {current_title} ({len(current_letter)} lines)")
  letters.append([current_title, ''] + current_letter)

print(f"There are {len(letters)} letters.")
counter = 1

for letter in letters:
  start = time.time()

  text = ('\n').join(letter)
  paragraphs = text.split('\n\n')
  words = len(text.split())
  title = paragraphs[0]
  print(f"Letter {counter}: {title} ({words} words)")

  # prompt template ends with <OCR text>
  letter_metadata_prompt = prompt_metadata.replace("<OCR text>", f"\n\"\"\"\n{text}\n\"\"\"")

  response = get_response(letter_metadata_prompt, LetterListMetadata)

  letter_data = json.loads(response['message']['content'])['letters'][0]
  letter_data['text'] = ('@@@').join(paragraphs).replace("-\n", '').replace("\n", ' ').replace('@@@', "\n\n")
  letter_data['title'] = title.title()
  letter_data['doctype'] = "letter"
  letter_data['word_count'] = words

  # now do the entities

  # prompt template ends with <OCR text>
  letter_entities_prompt = prompt_entities.replace("<OCR text>", f"\n\"\"\"\n{letter}\n\"\"\"")

  response = get_response(letter_entities_prompt, LetterListEntities)

  letter_data['entities'] = []
  for letter in json.loads(response['message']['content'])['letters']:
    for entity in letter['entities']:
      letter_data['entities'].append(entity)

  letters_json.append(letter_data)

  elapsed_seconds = round(time.time() - start, 1)
  print(f"  elapsed time: {elapsed_seconds} sec")
  letter_data['elapsed_seconds'] = elapsed_seconds

  counter += 1

# Write to json file
print(f"Writing to {filename}.json")
with open(f"output_json/{filename}.json", "w") as outfile:
  outfile.write(json.dumps(letters_json, indent=2))
