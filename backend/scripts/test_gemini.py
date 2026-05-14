import os
import sys
from dotenv import load_dotenv
import google.generativeai as genai

# Add parent dir to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

load_dotenv()

def test_gemini():
    api_key = os.getenv("GEMINI_API_KEY")
    print(f"Testing Gemini with key: {api_key[:10]}...")
    
    if not api_key:
        print("Error: No API key found in .env")
        return

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-flash-latest")
        response = model.generate_content("Dis bonjour brièvement.")
        print("Success! Gemini response:")
        print(response.text)
    except Exception as e:
        print(f"Error calling Gemini: {e}")

if __name__ == "__main__":
    test_gemini()
