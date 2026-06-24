import os
import urllib.request
import json
from dotenv import load_dotenv

load_dotenv()
api_key = os.environ.get("GEMINI_API_KEY")
if api_key:
    url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
            for model in data.get("models", []):
                if "gemini" in model["name"] and "generateContent" in model.get("supportedGenerationMethods", []):
                    print(model["name"])
    except Exception as e:
        print(f"Error: {e}")
else:
    print("No key")
