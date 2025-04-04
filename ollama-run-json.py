from ollama import chat
from pydantic import BaseModel

# based on https://ollama.com/blog/structured-outputs

with open('prompt_csv.txt', 'r') as file:
    prompt = file.read()
with open('sample_ocr.txt', 'r') as file:
    ocr_text = file.read()

# prompt ends with <paste OCR text>
prompt = 'Return as JSON. ' + prompt.replace('<paste OCR text>', ocr_text)

class Letter(BaseModel):
  Title: str
  Author: str
  Location: int
  Subjects: list[str]
  Summary: str
  LetterText: str

class LetterList(BaseModel):
  letters: list[Letter]

response = chat(
    model='llama3.1',
    messages=[
      {
        'role': 'user', 
        'content': prompt
      }
    ],
    format=LetterList.model_json_schema(),
)

print(response)

letters = LetterList.model_validate_json(response.messages.content)
print(letters)
