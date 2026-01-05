import os

print("SPOONACULAR_API_KEY:", "OK" if os.getenv("SPOONACULAR_API_KEY") else "MISSING")
print("GEMINI_API_KEY:", "OK" if os.getenv("GEMINI_API_KEY") else "MISSING")
