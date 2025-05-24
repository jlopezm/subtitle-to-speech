import os
import argparse
from google.cloud import texttospeech
from google.oauth2 import service_account

def ssml_to_audio(ssml_path, output_audio_path, creds_path, voice_name="en-GB-Neural2-B"):
    with open(ssml_path, "r", encoding="utf-8") as f:
        ssml = f.read()

    credentials = service_account.Credentials.from_service_account_file(creds_path)
    client = texttospeech.TextToSpeechClient(credentials=credentials)

    synthesis_input = texttospeech.SynthesisInput(ssml=ssml)

    voice = texttospeech.VoiceSelectionParams(
        language_code=voice_name[:5],  # "es-ES" extracted from "es-ES-Neural2-B"
        name=voice_name
    )

    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3
    )

    response = client.synthesize_speech(
        input=synthesis_input,
        voice=voice,
        audio_config=audio_config
    )

    with open(output_audio_path, "wb") as out:
        out.write(response.audio_content)
    
    print(f"✅ Audio generated at: {output_audio_path}")

def main():
    parser = argparse.ArgumentParser(description="Generate audio from SSML files using Google Cloud Text-to-Speech.")
    parser.add_argument("--creds_path", type=str, required=True, help="Path to the Google Cloud credentials JSON file.")
    args = parser.parse_args()

    # Define the base path (current folder)
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Delete all old mp3 files in the folder
    for file in os.listdir(base_dir):
        if file.endswith(".mp3"):
            file_path = os.path.join(base_dir, file)
            os.remove(file_path)
            print(f"❌ Deleted old file: {file_path}")

    # Iterate through all .ssml files in the folder and generate their corresponding mp3
    for file in os.listdir(base_dir):
        if file.endswith(".ssml"):
            ssml_path = os.path.join(base_dir, file)
            base_name, _ = os.path.splitext(file)
            output_audio_path = os.path.join(base_dir, f"{base_name}.mp3")
            ssml_to_audio(ssml_path, output_audio_path, args.creds_path)

if __name__ == "__main__":
    main()
