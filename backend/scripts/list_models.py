import os
import sys
from dotenv import load_dotenv
import google.generativeai as genai

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
for m in genai.list_models():
    if 'generateContent' in m.supported_generation_methods:
        print(m.name)
