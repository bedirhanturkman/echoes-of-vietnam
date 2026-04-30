"""
Quick test script to check Lyria 3 API access.
Tests both lyria-3-clip-preview (short) and lyria-3-pro-preview (full song).
"""

import os
import sys
from dotenv import load_dotenv

load_dotenv()

from google import genai
from google.genai import types

API_KEY = os.getenv("GEMINI_API_KEY", "")
if not API_KEY:
    print("[FAIL] No GEMINI_API_KEY found in .env")
    sys.exit(1)

print(f"[OK] API key found: {API_KEY[:10]}...")

client = genai.Client(api_key=API_KEY)

# --- Test 1: List available models to check Lyria access ---
print("\n--- Test 1: Checking available Lyria models ---")
try:
    models = client.models.list()
    lyria_models = []
    for model in models:
        name = model.name if hasattr(model, 'name') else str(model)
        if 'lyria' in name.lower():
            lyria_models.append(name)
    
    if lyria_models:
        print(f"[OK] Found Lyria models: {lyria_models}")
    else:
        print("[WARN] No Lyria models found in model list. They may still be accessible.")
except Exception as e:
    print(f"[WARN] Could not list models: {e}")

# --- Test 2: Try generating a short clip with lyria-3-clip-preview ---
print("\n--- Test 2: Testing lyria-3-clip-preview (30-sec clip) ---")
try:
    response = client.models.generate_content(
        model="lyria-3-clip-preview",
        contents="Create a 10-second soft acoustic guitar melody, peaceful and melancholic, instrumental only.",
        config=types.GenerateContentConfig(
            response_modalities=["AUDIO"],
        ),
    )
    
    # Check response for audio data
    audio_saved = False
    for part in response.candidates[0].content.parts:
        if hasattr(part, 'inline_data') and part.inline_data:
            mime = part.inline_data.mime_type
            data_size = len(part.inline_data.data)
            print(f"[OK] Got audio response! MIME: {mime}, Size: {data_size} bytes")
            
            # Save test file
            ext = "mp3" if "mp3" in mime else "wav" if "wav" in mime else "audio"
            test_path = f"output/test_lyria_clip.{ext}"
            os.makedirs("output", exist_ok=True)
            with open(test_path, "wb") as f:
                f.write(part.inline_data.data)
            print(f"[OK] Test audio saved: {test_path}")
            audio_saved = True
        elif hasattr(part, 'text') and part.text:
            print(f"[INFO] Text response: {part.text[:200]}")
    
    if not audio_saved:
        print("[WARN] No audio data in response")

except Exception as e:
    print(f"[FAIL] lyria-3-clip-preview error: {e}")
    print(f"       Error type: {type(e).__name__}")

# --- Test 3: Try lyria-3-pro-preview with vocals ---
print("\n--- Test 3: Testing lyria-3-pro-preview (full song with vocals) ---")
try:
    response = client.models.generate_content(
        model="lyria-3-pro-preview",
        contents="""Create a short folk song with gravelly male vocals.
Genre: Acoustic folk, protest song style.
Tempo: 72 BPM

[Verse]
The rivers run with memories untold,
Of soldiers young who never grew old.

[Chorus]
How many roads must a man walk down,
Before the guns fall silent in this town.""",
        config=types.GenerateContentConfig(
            response_modalities=["AUDIO", "TEXT"],
        ),
    )
    
    audio_saved = False
    for part in response.candidates[0].content.parts:
        if hasattr(part, 'inline_data') and part.inline_data:
            mime = part.inline_data.mime_type
            data_size = len(part.inline_data.data)
            print(f"[OK] Got audio with vocals! MIME: {mime}, Size: {data_size} bytes")
            
            ext = "mp3" if "mp3" in mime else "wav" if "wav" in mime else "audio"
            test_path = f"output/test_lyria_vocals.{ext}"
            with open(test_path, "wb") as f:
                f.write(part.inline_data.data)
            print(f"[OK] Vocal test saved: {test_path}")
            audio_saved = True
        elif hasattr(part, 'text') and part.text:
            print(f"[INFO] Text/lyrics: {part.text[:300]}")
    
    if not audio_saved:
        print("[WARN] No audio data in response")

except Exception as e:
    print(f"[FAIL] lyria-3-pro-preview error: {e}")
    print(f"       Error type: {type(e).__name__}")

print("\n--- Tests complete ---")
