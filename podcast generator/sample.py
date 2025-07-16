from elevenlabs.client import ElevenLabs
import os
from dotenv import load_dotenv
import requests

load_dotenv()

api_key=os.getenv("Eleven_lab_api_key")

  # or hardcode if testing

def get_credit_info():
    url = "https://api.elevenlabs.io/v1/user/subscription"
    headers = {
        "xi-api-key": api_key
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        character_limit = data.get("character_limit")
        character_count = data.get("character_count")
        remaining = character_limit - character_count
        print(f"Total Monthly Characters: {character_limit}")
        print(f"Characters Used: {character_count}")
        print(f"Characters Remaining: {remaining}")
    else:
        print(f"Failed to retrieve credits info: {response.status_code}, {response.text}")

get_credit_info()
# # from groq import Groq
# # import os
# # from dotenv import load_dotenv

# # load_dotenv()  # Load your .env file

# # groq_api_key = os.getenv("GROQ_API_KEY")


# # client = Groq(api_key='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')

# # completion = client.chat.completions.create(
# #     model="deepseek-r1-distill-llama-70b",
# #     messages=[
# #       {
# #         "role": "user",
# #         "content": "Tell me about quantum computing."
# #       }
# #     ],
# #     temperature=0.6,
# #     max_completion_tokens=4096,
# #     top_p=0.95,
# #     stream=False,
# #     stop=None,
# # )

# # for status_code, chunk in completion:
# #     print(chunk['choices'][0]['delta'].get('content', ''), end="")
