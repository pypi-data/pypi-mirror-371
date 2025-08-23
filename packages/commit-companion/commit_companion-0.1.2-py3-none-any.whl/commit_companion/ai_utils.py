# ai_utils.py
import openai
from utils import get_api_key

client = openai.OpenAI(api_key=get_api_key())

def generate_commit_message(diff: str, tone: str = "neutral") -> str:
    prompt = (
        f"Summarize the following Git diff as a conventional commit message.\n"
        f"Tone: {tone}\n\n"
        f"{diff}"
    )

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=60,
        )

        content = response.choices[0].message.content
        if content:
            return content.strip()
        else:
            return "⚠️ No content returned from GPT."

    except Exception as e:
        print(f"❌ GPT API call failed: {e}")
        return "⚠️ Failed to generate commit message."