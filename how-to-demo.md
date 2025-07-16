# How to demo:

pbinkley, 2025-07-14

## Derive OCR text

- currently depends on Gemini (using gemini-ocr.py to process column-level images produced by split-columns.py) - I need to adapt the olmocr process

## Extract JSON metadata from OCR text

```
source venv/bin/activate
python ollama-json.py raw_text/1933-03-11_letters.txt 
```

- this processes one page, with five letters to the editor
- for each letter it outputs the title, the single-paragraph summary, and a list of the entities (with name and type)
- the output goes to output_json/1933-03-11_letters.json
