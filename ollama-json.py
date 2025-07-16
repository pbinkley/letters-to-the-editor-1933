from ollama import chat
from pydantic import BaseModel
import json
import sys
import os
from pathlib import Path
import time
import re
import subprocess

# based on https://ollama.com/blog/structured-outputs

from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter

job_start = time.localtime()

# Parse command line arguments
parser = ArgumentParser(formatter_class=ArgumentDefaultsHelpFormatter)
parser.add_argument("-s", "--service", default="ollama", help="LLM service")
parser.add_argument("-m", "--model", default="olmo2", help="LLM name")
parser.add_argument("file", help="File name like raw_text/1933-03-01_letters.txt'")
args = vars(parser.parse_args())

# Set up parameters
service = args['service']
model = args['model']
try:
  input_text_file = args['file'] # e.g. raw_text/1933-03-01_letters.txt
except:
  sys.exit("Provide a filename like 'raw_text/1933-03-01_letters.txt'")

def get_short_commit_id_with_date():
    result = subprocess.run(['git', 'log', '-1', '--pretty=format:%h - %ad'], stdout=subprocess.PIPE)
    output = result.stdout.decode().strip()
    return output.split(' - ')[0], output.split(' - ')[1]

short_commit_id, commit_date = get_short_commit_id_with_date()

print(f"Service: {service}; model: {model}; commit: {short_commit_id}; commit date: {commit_date}")

# model = 'olmo2'
# model = 'olmo2:13b-1124-instruct-fp16'
# model = 'deepseek-r1:32b'

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
    model = model,
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
  start = time.localtime()

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
  letter_data['service'] = service
  letter_data['model'] = model
  letter_data['timestamp'] = time.strftime("%Y-%m-%d %H:%M:%S", start)

  print(letter_data['summary'])

  # now do the entities

  # prompt template ends with <OCR text>
  letter_entities_prompt = prompt_entities.replace("<OCR text>", f"\n\"\"\"\n{letter}\n\"\"\"")

  response = get_response(letter_entities_prompt, LetterListEntities)

  letter_data['entities'] = []
  for letter in json.loads(response['message']['content'])['letters']:
    #import pdb; pdb.set_trace()
    for entity in letter['entities']:
      letter_data['entities'].append(entity)
      print(f"  {entity.get('name', '<no name>')}: {entity.get('type', '<no type>')}")

  letters_json.append(letter_data)

  elapsed_seconds = round(time.time() - time.mktime(start), 1)
  print(f"  elapsed time: {elapsed_seconds} seconds; {len(letter_data['entities'])} entities")
  letter_data['elapsed_seconds'] = elapsed_seconds

  counter += 1

  print(f"\n\n")

job_elapsed_seconds = round(time.time() - time.mktime(job_start), 1)
print(f"  elapsed time: {job_elapsed_seconds} seconds")

# Write to json file
print(f"Writing to {filename}.json")
with open(f"output_json/{filename}-{model}-{short_commit_it}.json", "w") as outfile:
  outfile.write(json.dumps(letters_json, indent=2))
