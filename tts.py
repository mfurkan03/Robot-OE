import tempfile
from f5_tts.api import F5TTS # f5_tts'in kurulu ve erişilebilir olduğunu varsayıyoruz
from huggingface_hub import hf_hub_download
import os
import time

model = F5TTS(
        ckpt_file=hf_hub_download("hcsolakoglu/Orkhon-TTS", f"orkhon_tts.pt", token=os.getenv("HF_TOKEN")),
        vocab_file=hf_hub_download("hcsolakoglu/Orkhon-TTS", "vocab.txt", token=os.getenv("HF_TOKEN")))

def generate_speech(text, ref_audio,output_file = "last_output.wav"):
    """
    Seçilen F5TTS model varyantını kullanarak metinden konuşma üretir.

    Args:
        text (str): Sentezlenecek giriş metni.
        ref_audio (str): Ses klonlama için referans sesin dosya yolu.
        variant (str): Kullanılacak TTS model varyantı (örn. "orkhon_tts").
        progress (gradio.Progress, optional): Gradio ilerleme izleyicisi. Varsayılan gr.Progress().

    Returns:
        str: Üretilen WAV ses dosyasının dosya yolu.
    """
    # Seçilen varyant için F5TTS API örneğini al

    # Üretilen sesi kaydetmek için geçici bir dosya oluştur
    # delete=False önemlidir çünkü Gradio'nun bu dosyaya fonksiyon döndükten sonra erişmesi gerekir.
    # Gradio geçici dosyaların temizlenmesini halledecektir.
    # TTS çıkarımını gerçekleştir

    model.infer(
        ref_file=ref_audio,    # Referans sesin yolu
        ref_text="",           # Referans metin (ASR kullanılırsa veya model tarafından gerekmiyorsa boş olabilir)
        gen_text=text,         # Konuşma üretilecek metin
        file_wave=output_file,      # Çıktı WAV dosyasını kaydetme yolu
        nfe_step=16            # nfe_step değerini maksimuma (64) ayarla
    )
    
    return "last_output.wav"  # Üretilen ses dosyasının yolu
                                                                                                                                                      