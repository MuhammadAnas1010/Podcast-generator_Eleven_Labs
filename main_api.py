from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from podcast_generator import (
    get_credit_info, generate_podcast_script_text, parse_script_to_segments,
    generate_and_combine_audio_from_segments, save_script_text
)

app = FastAPI()

class PodcastRequest(BaseModel):
    topic: str
    llm_model: str = "llama3-70b-8192"
    host_voice: str = "Xb7hH8MSUJpSbSDYk0k2"
    guest_voice: str = "cgSgspJ2msm6clMCkdW9"
    output_audio_filename: str = "podcast.mp3"
    output_script_filename: str = "podcast_script.txt"


@app.post("/generate_podcast")
async def generate_podcast(podcast_material: PodcastRequest):
    credit_info = get_credit_info()
    if credit_info["status"] != "success" or credit_info["Remaining Credit"] <= 0:
        raise HTTPException(status_code=402, detail="not enough credit")

    script_text = generate_podcast_script_text(podcast_material.topic, podcast_material.llm_model)
    segments = parse_script_to_segments(script_text)

    if len(segments) > 6 or len(segments)<0:
        raise HTTPException(status_code=500, detail="Expected 6 dialogue segments, but got a different number.")

    save_script_text(script_text, podcast_material.output_script_filename)
    generate_and_combine_audio_from_segments(
        segments,
        podcast_material.host_voice,
        podcast_material.guest_voice,
        podcast_material.output_audio_filename
    )

    return {
        "success": True,
        "script_file": podcast_material.output_script_filename,
        "audio_file": podcast_material.output_audio_filename,
        "message": "Podcast generated successfully."
    }
