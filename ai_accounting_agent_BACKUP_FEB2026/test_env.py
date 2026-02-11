from dotenv import load_dotenv
import os

load_dotenv()

print("OpenAI Key:", os.getenv("OPENAI_API_KEY"))
print("Claude Key:", os.getenv("ANTHROPIC_API_KEY"))