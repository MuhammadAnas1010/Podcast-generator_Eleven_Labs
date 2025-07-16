import os
from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs
from elevenlabs import VoiceSettings
from openai import OpenAI
from pydub import AudioSegment
import requests
import argparse


load_dotenv()

ElevenLabs_api_key = os.getenv("Eleven_lab_api_key")
LLM_key=os.getenv("LLM_secret_key")

print(ElevenLabs_api_key)
print(LLM_key)
if not ElevenLabs_api_key or not LLM_key:
    raise ValueError("API key not present")

client=ElevenLabs(api_key=ElevenLabs_api_key)

def validate_audio_type(file):
    if not file.endswith(('.mp3','.wav')):
        raise argparse.ArgumentTypeError("Audio file must end with .mp3 or .wav")
    return file


def CLI_parse():
    parse=argparse.ArgumentParser(description="Podcast Generator CLI")
    parse.add_argument('-topic',required=True,type=str,help="Tell Topic for podcast")
    parse.add_argument('-output_audio_file', type=validate_audio_type, default='my_podcast.mp3',
                        help='(Optional) Name for output audio file (.mp3 or .wav). Default: my_podcast.mp3')
    parse.add_argument('-output_script_file', type=str, default='podcast_script.txt',
                        help='(Optional) Name for output text script file. Default: podcast_script.txt')
    parse.add_argument('-llm_model', type=str, default='mistral-saba-24b',
                         help='(Optional) LLM model to use. Default: mistral-saba-24b can choose llama3-70b-8192')
    parse.add_argument('-host_voice', type=str, default='Xb7hH8MSUJpSbSDYk0k2',
                        help='(Optional) Eleven Labs Voice ID for Host. Default: Xb7hH8MSUJpSbSDYk0k2')
    parse.add_argument('-guest_voice', type=str, default='cgSgspJ2msm6clMCkdW9',
                        help='(Optional) Eleven Labs Voice ID for Guest. Default: cgSgspJ2msm6clMCkdW9')
    
    return parse.parse_args()


def text_to_speech(text:str,index:int):

    print(f"Generating audio for index {index}, speaker: {text.get('speaker')}, text: {text.get('text')}")

    voice_id = args.host_voice if text.get('speaker').lower() == "host" else args.guest_voice
    client = ElevenLabs(api_key=ElevenLabs_api_key)
    response=client.text_to_speech.convert(
        optimize_streaming_latency='0',
        voice_id=voice_id,
        output_format='mp3_44100_128',
        text=text.get("text"),
        voice_settings=VoiceSettings(
            stability=0.75,         
            similarity_boost=0.65,  
            style=0.7,  
            use_speaker_boost=True,
        ),
    
    )
    save_file_path=f"D{index}first_sample.mp3"
    audio_file_names.append(save_file_path)
    with open(save_file_path,"wb") as f:
        for chunk in response:
            if chunk:
                f.write(chunk)
    print(f"New audio file added{save_file_path}")
    return save_file_path




def get_credit_info():
    print(ElevenLabs_api_key)
    url = "https://api.elevenlabs.io/v1/user/subscription"
    headers = {
        "xi-api-key": ElevenLabs_api_key
    }
    try:

        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            data = response.json()
            character_limit = data.get("character_limit")
            character_count = data.get("character_count")
            remaining = character_limit - character_count
            return {"status":"success","Remaining Credit":remaining}
        else:
            print(f"Failed to fetch credit info: {response.text}")
            return {"status":"Failed", "Remaining Credit": 0}
    except Exception as e:
        print(f"Error fetching credit info: {e}")
        return {"status":"Failed", "Remaining Credit": 0}
    
Client = OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=LLM_key,
)
def model_response(prompt):
    try:
        response = Client.chat.completions.create(
            model="mistral-saba-24b",
            extra_body={
                'temperature': 0.5,
                'stream': False
            },
            messages=prompt
        )
        answer = response.choices[0].message.content
        return answer
    except Exception as e:
        return f"Error: {str(e)}"


def combine_audio_files(audio_file_names, output_file):
    combined = AudioSegment.empty()

    try:
        for file_path in audio_file_names:
            audio = AudioSegment.from_file(file_path)
            combined += audio
        combined.export(output_file, format="mp3")
        print(f"Combined audio saved to: {output_file}")
    except Exception as e:
        print(f"Failed to combine audio files: {e}")
args=CLI_parse()

#Todo: Add more voices later
#change 1 2 3
# #change 1 2 3  
text=[{'role':'system','content':'Your are given a topic of a podcast, you simplely have to return EXACT 6 answer 3 from host and 3 from guest,Not even a single more answer.Total quantity should be 6. the format should be like HOST: and Guest: , Nothing else,First line from Host like he is asking then from guset then again from host and then guest and so on. What you complete a reply from host or guest , write | this sign and then next .Make sure the conversation sounds like a natural conversation .Only write amm if you want but dont write any expression like laugh or confuse. these convertions are gonna be load into another voice generating LLM so make them sound as natural as possible '},{'role':'user','content':args.topic}]
answer=model_response(text)

if not answer:
    print("Failed to generate podcast script. Exiting.")
    exit(1)


list1 = []
script_text = ""
for line in answer.split('\n'):
    if ':' not in line:
        continue
    speaker, text = line.split(':', 1)
    speaker = speaker.strip()
    text = text.strip()
    list1.append({'speaker': speaker, 'text': text})
    script_text += f"{speaker}: {text}\n"
speaker=0
for items in list1:
    if speaker<=6 and speaker >=0:
        if items.get("speaker").lower()=="host" or items.get("speaker").lower()=="guest" :
            speaker+=1
    else:
        raise IndexError("Speaker limit exceeded")


with open(args.output_script_file,"w",encoding="UTF-8") as f:
    f.write(script_text)



audio_file_names=[]
credit_info=get_credit_info()
if credit_info.get("status")=="success":
    print(f"Remaining ElevenLabs Credits: {credit_info.get('Remaining Credit')}")
    retur=[text_to_speech(i, index) for index, i in enumerate(list1)]
else:
    print("Not enough credits to generate audio.")
    exit(1)



combine_audio_files(audio_file_names, args.output_audio_file)
