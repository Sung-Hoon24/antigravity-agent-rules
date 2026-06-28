import os
import sys
from dotenv import load_dotenv

try:
    from google import genai
    from google.genai import types
except ImportError:
    print("google-genai not installed")
    sys.exit(1)


def test_lyria():
    load_dotenv(r"c:\1인기업\Apps\유튜브에이전트\.env")
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("No API Key")
        return

    client = genai.Client(api_key=api_key)
    prompt = "Lo-fi hip-hop beat, very short 5 seconds, test audio"
    model_id = "lyria-3-pro-preview"

    print(f"Testing {model_id}...")
    try:
        response = client.models.generate_content(
            model=model_id,
            contents=prompt,
            config=types.GenerateContentConfig(response_modalities=["AUDIO"]),
        )

        if getattr(response, "candidates", None) and len(response.candidates) > 0:
            candidate = response.candidates[0]
            if not candidate.content:
                print(
                    "Candidate content is None. Finish reason:", candidate.finish_reason
                )
                print("Candidate safety ratings:", candidate.safety_ratings)
                return
            for part in candidate.content.parts:
                if hasattr(part, "inline_data") and part.inline_data is not None:
                    mime = getattr(part.inline_data, "mime_type", "")
                    if mime.startswith("audio/"):
                        print("SUCCESS: Audio data received!")
                        return
        print("No audio data in response. Full response:", response)
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    test_lyria()
