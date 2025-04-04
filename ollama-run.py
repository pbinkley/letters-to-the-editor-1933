from ollama import chat

with open('prompt_csv.txt', 'r') as file:
    prompt = file.read()
with open('sample_ocr.txt', 'r') as file:
    ocr_text = file.read()

# prompt ends with <paste OCR text>
prompt = prompt.replace('<paste OCR text>', ocr_text)

stream = chat(
    model='deepseek-r1',
    messages=[{'role': 'user', 'content': prompt}],
    stream=True,
)

for chunk in stream:
  print(chunk['message']['content'], end='', flush=True)
