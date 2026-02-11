from dotenv import load_dotenv
import os
from anthropic import Anthropic

load_dotenv()

client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

msg = client.messages.create(
    model="claude-3-5-sonnet-latest",
    max_tokens=200,
    messages=[
        {"role": "user", "content": "Say hi and summarize what an accounting AI agent does in 2 bullets."}
    ],
)

print(msg.content[0].text)