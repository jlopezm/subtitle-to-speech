from google.cloud import texttospeech
from google.oauth2 import service_account

def list_filtered_voices(creds_path):
    allowed_languages = {"es-ES", "es-US", "ca-ES", "en-US"}

    credentials = service_account.Credentials.from_service_account_file(creds_path)
    client = texttospeech.TextToSpeechClient(credentials=credentials)

    response = client.list_voices()

    for voice in response.voices:
        languages = voice.language_codes
        if any(lang in allowed_languages for lang in languages):
            languages_str = ", ".join(languages)
            gender = texttospeech.SsmlVoiceGender(voice.ssml_gender).name
            print(f"Name: {voice.name}")
            print(f"Languages: {languages_str}")
            print(f"Gender: {gender}")
            print(f"Sample rate: {voice.natural_sample_rate_hertz} Hz")
            print("-" * 40)

import argparse

def main():
    parser = argparse.ArgumentParser(description="List available voices from Google Cloud Text-to-Speech, filtered by language.")
    parser.add_argument("--creds_path", required=True, help="Path to the Google Cloud service account JSON key file.")
    args = parser.parse_args()
    list_filtered_voices(args.creds_path)

if __name__ == "__main__":
    main()
