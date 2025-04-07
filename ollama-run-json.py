from ollama import chat
from pydantic import BaseModel
import json

# based on https://ollama.com/blog/structured-outputs

class Letter(BaseModel):
  Author: str
  Location: str
  Subjects: list[str]
  Summary: str
  Persons: list[str]
  Places: list[str]
  Organizations: list[str]

class LetterList(BaseModel):
  letters: list[Letter]

with open('prompt_csv.txt', 'r') as file:
    prompt = file.read()
with open('sample_ocr.txt', 'r') as file:
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

  # prompt ends with <paste OCR text>
  letter_prompt = 'Return as JSON. ' + prompt.replace("<paste OCR text>", f"\n\"\"\"\n{letter}\n\"\"\"")

  response = chat(
      model='olmo2',
      messages=[
        { 
          'role': 'system', 
          'content': 'You are a helpful assistant. You pay close attention to your instructions and follow them precisely.'
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
  print(f"{letter['Title']}\nPersons: {letter['Persons']}\nPlaces: {letter['Places']}\nOrganisations: {letter['Organizations']}\n\n")

  letters_json.append(letter)

#  import pdb; pdb.set_trace()

# Writing to sample.json
print("Writing to sample.json")
with open("output_json/sample.json", "w") as outfile:
  outfile.write(json.dumps(letters_json, indent=2))