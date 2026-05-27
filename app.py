import gradio as gr
import subprocess, json, os, io, tempfile
from faster_whisper import WhisperModel
from ollama import Client as OllamaClient

# ---- CONFIG ----
LLM_MODEL = "llama3.2:3b"      # or "mistral:7b", "qwen2.5:3b"
WHISPER_SIZE = "small"         # "base", "small", "medium"
USE_SILERO = True              # set False to use Coqui XTTS v2
USE_CONTEXT = False  # <— new: disable conversational memory

import os
USE_REMOTE_OLLAMA = bool(os.getenv("OLLAMA_HOST"))


if not USE_REMOTE_OLLAMA:
    # Transformers fallback for Spaces (CPU-friendly small instruct model)
    from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
    HF_CHAT_MODEL = os.getenv("HF_CHAT_MODEL", "google/gemma-2-2b-it")  # small instruct model that runs on CPU
    HF_TOKEN = os.getenv("HF_TOKEN")
    
    _tok = AutoTokenizer.from_pretrained(HF_CHAT_MODEL, token=HF_TOKEN)
    _mdl = AutoModelForCausalLM.from_pretrained(HF_CHAT_MODEL, token=HF_TOKEN, torch_dtype="auto", device_map="auto")
    gen = pipeline("text-generation", model=_mdl, tokenizer=_tok, max_new_tokens=256)



# ---- STT (faster-whisper) ----
# Run on GPU if available: compute_type="float16", device="cuda"
stt_model = WhisperModel(WHISPER_SIZE, device="cuda" if os.environ.get("CUDA_VISIBLE_DEVICES") else "cpu",
                         compute_type="float16" if os.environ.get("CUDA_VISIBLE_DEVICES") else "int8")

def speech_to_text(audio_path: str) -> str:
    segments, info = stt_model.transcribe(audio_path, beam_size=1, vad_filter=True, language="en")
    text = "".join(seg.text for seg in segments).strip()
    return text

# ---- LLM (Ollama) ----
# ollama = OllamaClient(host="http://127.0.0.1:11434")

SYSTEM_PROMPT = """You are a friendly AI voice assistant.
Reply in one short, natural sentence only.
Sound warm and conversational, never formal.
Avoid multi-sentence or paragraph answers."""

def chat_with_llm(history_messages, user_text):
    if USE_REMOTE_OLLAMA:
        # Only system + current user
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_text},
        ]
        resp = ollama.chat(model=LLM_MODEL, messages=messages)
        return resp["message"]["content"]
    else:
        # Only system + current user
        prompt = f"{SYSTEM_PROMPT}\nUser: {user_text}\nAssistant:"
        out = gen(prompt, return_full_text=False, max_new_tokens=25, temperature=0.8, repetition_penalty=1.1,)[0]["generated_text"].split("\n")[0].strip()
        return out









# near top-level (global singletons)
_SILERO_TTS = None

def tts_silero(text: str) -> str:
    """
    Return path to WAV synthesized by Silero TTS.
    Uses a cached model instance to avoid re-downloading each request.
    """
    import torch, tempfile
    import soundfile as sf

    global _SILERO_TTS
    if _SILERO_TTS is None:
        obj = torch.hub.load(
            repo_or_dir="snakers4/silero-models",
            model="silero_tts",
            language="en",
            speaker="v3_en",
            trust_repo=True,   # avoids interactive trust prompt
        )
        _SILERO_TTS = obj[0] if isinstance(obj, (list, tuple)) else obj

    model = _SILERO_TTS
    sample_rate = 48000
    speaker = "en_0"
    audio = model.apply_tts(text=text, speaker=speaker, sample_rate=sample_rate)

    out_wav = tempfile.mktemp(suffix=".wav")
    sf.write(out_wav, audio, sample_rate)
    return out_wav



def tts_coqui_xtts(text: str) -> str:
    """
    Returns path to a WAV file synthesized by Coqui XTTS v2 (higher quality; GPU-friendly).
    """
    from TTS.api import TTS
    tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2")
    out_wav = tempfile.mktemp(suffix=".wav")
    tts.tts_to_file(text=text, file_path=out_wav, speaker="female-en-5", language="en")
    return out_wav

def text_to_speech(text: str) -> str:
    if USE_SILERO:
        return tts_silero(text)
    else:
        return tts_coqui_xtts(text)

# ---- Gradio pipeline ----
def pipeline(audio, history):
    # audio is (sample_rate, np.array) OR a filepath (depends on Gradio version)
    # Normalize to a temp wav file
    if audio is None:
        return history, None, "Please speak something."

    if isinstance(audio, tuple):
        # (sr, data) -> write wav
        import soundfile as sf, numpy as np, tempfile
        sr, data = audio
        tmp_in = tempfile.mktemp(suffix=".wav")
        sf.write(tmp_in, data.astype("float32"), sr)
        audio_path = tmp_in
    else:
        audio_path = audio  # path already

    user_text = speech_to_text(audio_path)
    if not user_text:
        return history, None, "Didn't catch that—could you repeat?"

    reply = chat_with_llm(history, user_text)

    # Extract the "Reply:" line for TTS; speak only the conversational reply
    speak_text = reply
    for tag in ["Reply:", "Correction:", "Why:"]:
        # Try to find "Reply:" block
        if "Reply:" in reply:
            speak_text = reply.split("Reply:", 1)[1].strip()
            break

    wav_path = text_to_speech(speak_text)
    updated = (history or []) + [
        {"role": "user", "content": user_text},
        {"role": "assistant", "content": reply},
    ]
    return updated, wav_path, ""

with gr.Blocks(title="Voice Coach") as demo:
    gr.Markdown("## 🎙️ Interactive Voice Chat")
    with gr.Row():
        audio_in = gr.Audio(sources=["microphone"], type="filepath", label="Speak")
        audio_out = gr.Audio(label="Assistant (TTS)", autoplay=True)
    chatbox = gr.Chatbot(type="messages", height=300)
    status = gr.Markdown()
    btn = gr.Button("Send")

    # Use continuous recording or press "Send" after recording
    audio_in.change(pipeline, inputs=[audio_in, chatbox], outputs=[chatbox, audio_out, status])
    btn.click(pipeline, inputs=[audio_in, chatbox], outputs=[chatbox, audio_out, status])

if __name__ == "__main__":
    demo.launch()