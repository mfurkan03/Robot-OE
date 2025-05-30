import os
import sys
import pyaudio
import keyboard
from openai import OpenAI
from google.cloud import speech

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "pazarlik-robotu-04e4fff35c71.json"  # kendi yolun

def recognize_speech_while_pressed():
    RATE = 16000
    CHUNK = int(RATE / 10)

    client = speech.SpeechClient()

    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=RATE,
        language_code="tr-TR"
    )

    streaming_config = speech.StreamingRecognitionConfig(
        config=config,
        interim_results=False
    )

    def generator():
        p = pyaudio.PyAudio()
        stream = p.open(format=pyaudio.paInt16, channels=1, rate=RATE, input=True, frames_per_buffer=CHUNK)
        print("🎙️ SPACE tuşuna basılı tutarak konuşun...")
        while keyboard.is_pressed('space'):
            data = stream.read(CHUNK, exception_on_overflow=False)
            yield speech.StreamingRecognizeRequest(audio_content=data)
        stream.stop_stream()
        stream.close()
        p.terminate()

    requests = generator()
    responses = client.streaming_recognize(config=streaming_config, requests=requests)

    for response in responses:
        for result in response.results:
            if result.is_final:
                return result.alternatives[0].transcript
    return ""