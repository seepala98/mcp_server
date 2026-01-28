import sys
from pypdf import PdfReader
import json
import os

def extract_text_from_pdf(pdf_path):
    try:
        reader = PdfReader(pdf_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text.strip()
    except Exception as e:
        print(f"Error extracting PDF: {e}")
        return None

def main():
    resume_path = "/Users/saisuryapranavi/Github/EAG/course_content/code/Session5/Vardhan_Seepala_Resume_.pdf"
    output_path = "/Users/saisuryapranavi/Github/EAG/course_content/code/Session5/resume_text.txt"
    
    print(f"Extracting text from {resume_path}...")
    text = extract_text_from_pdf(resume_path)
    
    if text:
        with open(output_path, "w") as f:
            f.write(text)
        print(f"Successfully extracted text to {output_path}")
        
        # Basic normalization (Stage 3)
        # In a real scenario, we'd use LLM for this, but for now we'll just save the raw text
        # and let the matching engine handle it.
    else:
        print("Failed to extract text.")

if __name__ == "__main__":
    main()
