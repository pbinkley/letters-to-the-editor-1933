from ollama import chat
from pydantic import BaseModel

# based on https://ollama.com/blog/structured-outputs

class Letter(BaseModel):
  Author: str
  Location: str
  Subjects: list[str]
  Summary: str

class LetterList(BaseModel):
  letters: list[Letter]

with open('prompt_csv.txt', 'r') as file:
    prompt = file.read()
with open('sample_ocr.txt', 'r') as file:
    ocr_text = file.read()

# loop through letters, 
# which are separated by empty lines

letters = ocr_text.split("\n\n")
print(f"There are {len(letters)} letters.")
# import pdb; pdb.set_trace()

for letter in letters:

  paragraphs = letter.partition('\n')
  title = paragraphs[0]
  print("Letter: " + title)

  # prompt ends with <paste OCR text>
  letter_prompt = 'Return as JSON. ' + prompt.replace('<paste OCR text>', letter)

  response = chat(
      model='llama3.1',
      messages=[
        {
          'role': 'user', 
          'content': letter_prompt
        }
      ],
      format=LetterList.model_json_schema(),
  )

  print(response)
  import pdb; pdb.set_trace()

# letters = LetterList.model_validate_json(response.messages.content)
# print(letters)
