from openai import OpenAI
from tts import generate_speech
import sys
from pydub import AudioSegment
from pydub.playback import _play_with_simpleaudio as play  # Özel çağrı
import re
import time
from typing import List
import os
import threading
import queue

audio_queue = queue.Queue()

def get_api_key(filename):
    with open("api_key.txt", "r") as file:
        api_key = file.read().strip()
    return api_key

def main(filename):
    client = OpenAI(api_key=get_api_key(filename))

    messages = [{
        "role": "user",
        "content": "Sen şu an kaba bir rehin dükkanı sahibisin (biraz kaba davranmaya dikkat et, doğallık için) ve ben seninle birazdan sahip olduğum bir ürünle ilgili pazarlık yapacağım. Benimle selamlaşarak ve ne satmak istediğimi sorarak diyaloğa başla. Satacağım ürünü benden olabildiğince ucuza satın alman gerekiyor ve sana yalan da söyleyebilirim bu ürünün fiyatı hakkında. Bu konularda araştırma yapıp bana yapabileceğin en ucuz teklifi yapman gerekiyor. Rehin dükkanı sahibi olduğunu ve bir ürünü ölücülük yaparak satın alman gerekiyor. Daha sonrasında da bu ürünü benden satın alıp beni ikna etmen gerekiyor. Eğer ürün sana pahalı gelirse satın alma. Ayrıca, bütün sayıları yazıyla yaz, rakamla yazma!"
            }
        ]

    print("💬 Chat with the GPT-4o pawn shop bot. Type 'exit' to quit.\n")

    # Chat loop
    while True:
        # Get response from GPT-4o
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            temperature=1,
            max_tokens=1000,
            top_p=1,
        )

        reply = response.choices[0].message.content
        #print("PawnBot:", reply, "\n")
        
        generate(reply, ref_audio=r"C:\Users\alkan\OneDrive\Masaüstü\Dersler\term6\Foe\oe_f5tts_2.wav")  # Ses üretimi için referans ses dosyası

        messages.append({"role": "assistant", "content": reply})

        user_input = input("You: ")
        #print("\n")
        if user_input.lower() in {"exit", "quit"}:
            print("👋 Goodbye!")
            break
            
        messages.append({"role": "user", "content": user_input})
      # Bu satır, ses tamamen bitene kadar bekler

def audio_player_worker():
    while True:
        filename = audio_queue.get()
        if filename is None:  # Kuyruğa None gelirse thread kapanır
            break
        audio = AudioSegment.from_file(filename, format="wav")
        playback = play(audio)
        playback.wait_done()
        audio_queue.task_done()

# Player thread başlat
player_thread = threading.Thread(target=audio_player_worker, daemon=True)
player_thread.start()


def split_into_batches_smart(text: str, batch_size: int = 20) -> List[str]:
    # Cümlelere ayır
    sentences = re.split(r'(?<=[.!?])\s+', text)
    batches = []
    current_batch = []
    current_word_count = 0

    for sentence in sentences:
        words = sentence.strip().split()
        word_count = len(words)

        # Eğer bu cümle eklendiğinde batch sınırı aşılmıyorsa, ekle
        if current_word_count + word_count <= batch_size:
            current_batch.append(sentence.strip())
            current_word_count += word_count
        else:
            # Eğer cümle tek başına batch'ten büyükse, tek başına batch yap
            if word_count > batch_size:
                if current_batch:
                    batches.append(' '.join(current_batch))
                batches.append(sentence.strip())
                current_batch = []
                current_word_count = 0
            else:
                # Mevcut batch'i kapat, yeni batch başlat
                if current_batch:
                    batches.append(' '.join(current_batch))
                current_batch = [sentence.strip()]
                current_word_count = word_count

    # Son kalan batch'i ekle
    if current_batch:
        batches.append(' '.join(current_batch))

    return batches

def play_audio_threaded(filename: str):
    # Sadece filename'i kuyruğa ekle
    audio_queue.put(filename)

def generate(response: str, ref_audio: str):
    output_dir = "output_wavs"
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)

    batches = split_into_batches_smart(response, batch_size=18)

    for i, batch in enumerate(batches):
        filename = os.path.join(output_dir, f"batch_{i}.wav")
        generate_speech(batch, ref_audio, output_file=filename)
        print(f"[Batch {i+1}] {batch}")
        play_audio_threaded(filename)  # Kuyruğa ekle, thread oynatacak

# Ana program kapanırken player thread’i kapat:
def close_audio_player():
    audio_queue.put(None)  # İşaret gönder (kapanış sinyali)
    player_thread.join()
        # İstersen kaldır – güvenlik boşluğu

if __name__ == "__main__":
    main(sys.argv[0])


