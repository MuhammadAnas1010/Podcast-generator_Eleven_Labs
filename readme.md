# 🎙️ Podcast Generator CLI

This is a **CLI tool to generate a podcast** featuring a Host and a Guest discussing any given topic. It leverages:
- **Groq's LLM API (OpenAI-compatible)** to generate the dialogue.
- **ElevenLabs API** for converting text into speech.
- **PyDub** to merge generated audio clips into one final podcast file.
- **dotenv** for managing secret API keys.

---

## 📦 Features
- Generates a **scripted conversation** between Host & Guest on any topic.
- Converts dialogue into **voice audio** using ElevenLabs.
- Merges audio into a **single podcast MP3 file**.
- Saves the **generated script as a text file**.
- Configurable voices, output files, and LLM model.

---

## ⚙️ Setup Instructions

### 1. Clone the Repository
```bash
git clone https://github.com/MuhammadAnas1010/Podcast-generator_Eleven_Labs.git
cd podcast-generator-cli
python -m venv venv
venv\Scripts\activate

pip install -r requirements.txt

Eleven_lab_api_key=your_elevenlabs_api_key
LLM_secret_key=your_groq_api_key

Launch the API server with: uvicorn main_api:app --reload

server will be at: http://127.0.0.1:8000

api docs: http://127.0.0.1:8000/docs

Example api request Using /Docs:
{
    "topic": "The future of electric cars",
    "llm_model": "llama3-70b-8192",
    "llm_provider": "Groq",
    "host_voice": "Xb7hH8MSUJpSbSDYk0k2",
    "guest_voice": "cgSgspJ2msm6clMCkdW9",
    "output_audio_filename": "my_podcast.mp3",
    "output_script_filename": "my_podcast_script.txt"
}

```