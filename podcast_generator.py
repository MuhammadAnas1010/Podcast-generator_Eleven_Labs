import os
from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs
from elevenlabs import VoiceSettings
from openai import OpenAI
from pydub import AudioSegment
import requests

load_dotenv()

ElevenLabs_api_key = os.getenv("Eleven_lab_api_key")
LLM_key = os.getenv("LLM_secret_key")

client = ElevenLabs(api_key=ElevenLabs_api_key)
openai_client = OpenAI(base_url="https://api.groq.com/openai/v1", api_key=LLM_key)


def get_credit_info():
    url = "https://api.elevenlabs.io/v1/user/subscription"
    headers = {"xi-api-key": ElevenLabs_api_key}

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        remaining = data.get("character_limit") - data.get("character_count")
        return {"status": "success", "Remaining Credit": remaining}
    else:
        return {"status": "Failed", "Remaining Credit": 0}


def generate_podcast_script_text(topic: str, llm_model: str) -> str:
    prompt = [
        {'role': 'system', 'content': 'Your are given a topic of a podcast, you simplely have to return EXACT 6 answer 3 from host and 3 from guest,Not even a single more answer.Total quantity should be 6. the format should be like HOST: and Guest: , Nothing else,First line from Host like he is asking then from guset then again from host and then guest and so on. What you complete a reply from host or guest , write | this sign and then next .Make sure the conversation sounds like a natural conversation .Only write amm if you want but dont write any expression like laugh or confuse. these convertions are gonna be load into another voice generating LLM so make them sound as natural as possible'},
        {'role': 'user', 'content': topic}
    ]

    response = openai_client.chat.completions.create(
        model=llm_model,
        extra_body={'temperature': 0.5, 
                    'stream': False},
        messages=prompt
    )
    return response.choices[0].message.content


def parse_script_to_segments(script_text: str) -> list:
    segments = []
    for part in script_text.split('|'):
        if ':' not in part:
            continue
        speaker, text = part.split(':', 1)
        segments.append({'speaker': speaker.strip(), 
                         'text': text.strip()})
    return segments


def text_to_speech(text_segment: dict, index: int, host_voice: str, guest_voice: str) -> str:
    voice_id = host_voice if text_segment['speaker'].lower() == "host" else guest_voice
    response = client.text_to_speech.convert(
        optimize_streaming_latency='0',
        voice_id=voice_id,
        output_format='mp3_44100_128',
        text=text_segment['text'],
        voice_settings=VoiceSettings(stability=0.75,
            similarity_boost=0.65, 
            style=0.7, 
            use_speaker_boost=True)
    )

    file_name = f"segment_{index}.mp3"
    with open(file_name, 'wb') as f:
        for chunk in response:
            if chunk:
                f.write(chunk)
    return file_name


def generate_and_combine_audio_from_segments(segments: list, host_voice: str, guest_voice: str, output_audio_path: str) -> None:
    audio_files = []
    for idx, segment in enumerate(segments):
        audio_file = text_to_speech(segment, idx, host_voice, guest_voice)
        audio_files.append(audio_file)

    combined = AudioSegment.empty()
    for file in audio_files:
        audio = AudioSegment.from_file(file)
        combined += audio

    combined.export(output_audio_path, format="mp3")


def save_script_text(script_text: str, output_script_filename: str) -> None:
    with open(output_script_filename, "w", encoding="utf-8") as f:
        f.write(script_text)
