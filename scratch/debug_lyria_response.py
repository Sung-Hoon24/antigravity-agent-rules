# -*- coding: utf-8 -*-
import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv(r"c:\1인기업\Apps\유튜브에이전트\.env")
api_key_env = os.getenv("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEYS")
api_key = api_key_env.split(",")[0].strip()
client = genai.Client(api_key=api_key)

prompt = "Lo-fi hip-hop study beat, 70 BPM. Warm Rhodes electric piano chords, soft dusty vinyl crackles. No vocals. Short test duration. 30 seconds long."
model_id = "lyria-3-pro-preview"

print("📡 API 호출 시작...")
response = client.models.generate_content(
    model=model_id,
    contents=prompt,
    config=types.GenerateContentConfig(response_modalities=["AUDIO"]),
)

print("\n=== API 응답 객체 구조 ===")
print(response)

if getattr(response, "candidates", None) and len(response.candidates) > 0:
    candidate = response.candidates[0]
    print("\n--- Candidate 0 ---")
    print(f"Finish Reason: {candidate.finish_reason}")
    print(
        f"Safety Ratings: {candidate.safety_ratings if hasattr(candidate, 'safety_ratings') else 'None'}"
    )
    if candidate.content:
        print(f"Content parts count: {len(candidate.content.parts)}")
        for idx, part in enumerate(candidate.content.parts):
            print(f"Part {idx} type: {type(part)}")
            print(f"Part {idx} keys/attributes: {dir(part)}")
            if hasattr(part, "inline_data") and part.inline_data is not None:
                print(f"Part {idx} mime_type: {part.inline_data.mime_type}")
                print(
                    f"Part {idx} data length: {len(part.inline_data.data) if part.inline_data.data else 0}"
                )
            else:
                print(
                    f"Part {idx} has no inline_data. Text preview: {getattr(part, 'text', 'No text')}"
                )
else:
    print("No candidates found.")
