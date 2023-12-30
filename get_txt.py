import assemblyai as aai

aai.settings.api_key = "5bd662961e754f148a581e0070f09c88" 

transcriber = aai.Transcriber()

audio_url = (
    "https://bat.hedigital.online/file-1703669708657-351786808.mpeg"
)

config = aai.TranscriptionConfig(speaker_labels=True)

transcript = transcriber.transcribe(audio_url, config)

print(transcript.text)

for utterance in transcript.utterances:
    print(f"Speaker {utterance.speaker}: {utterance.text}")