---
title: Interactive AI Voice Chat
emoji: 🚀
colorFrom: pink
colorTo: red
sdk: gradio
sdk_version: 6.15.0
app_file: app.py
pinned: false
license: mit
short_description: Real-time AI voice assistant through natural speech
---

## 🚀 Overview

Interactive AI Voice Chat is a real-time voice-driven assistant deployed on Hugging Face Spaces.  
It allows users to speak naturally through their microphone and receive intelligent AI responses, both in text and audio format. The system leverages modern speech-to-text, large language models, and text-to-speech technologies to deliver a seamless conversational experience.

This project demonstrates a complete workflow from local development to live deployment on the Hugging Face platform.

---

## ✨ Key Features

- 🎤 Real-time voice input processing  
- 🤖 AI-powered responses using `google/gemma-2-2b-it`  
- 🔊 Text-to-Speech audio replies  
- 🌐 Publicly accessible live demo  
- ⚡ Optimized for CPU Basic hardware  
- 🧩 Secure token-based model access

---

## 🖥️ How It Works

1. User speaks into the microphone.
2. Speech is converted to text using STT engine.
3. The text is processed by the AI model.
4. AI generates a response.
5. Response is converted back into audio and played to the user.

---

## 📁 Project Structure

ai-voice-chat-test/
- │
- ├── app.py # Main application logic
- ├── README.md # Documentation
- ├── requirements.txt # Python dependencies
- ├── runtime.txt # Python version
- ├── apt.txt # System dependencies (ffmpeg)
- ├── .gitattributes # Git LFS configuration
- ├── .gitignore # Ignored files and folders
- └── assets/ # Optional media resources

---

## ⚙️ Installation (Local Setup - Optional)

To run this project locally:

```bash
git clone https://huggingface.co/spaces/bdstar/ai-voice-chat-test
cd ai-voice-chat-test
pip install -r requirements.txt
Set your Hugging Face token:
export HF_TOKEN="your_token_here"
Run the application:
python app.py
Open your browser and visit:
http://localhost:7860
```
---
## 📦 Python Environment
- Python Version: 3.11
- Gradio Version: 5.49.1
- Optimized for: CPU Basic

---

## ⚠️ Notes & Limitations
- Running on CPU may result in slower response times.
- Initial model loading may take few seconds.
- For production use, GPU-backed hardware is recommended.
- This project is intended for demonstration and learning purposes.

---

## 📌 Deployment Steps Summary
1.  Prepare project structure
2.	Configure requirements.txt and runtime.txt
3.	Add HF_TOKEN as secret
4.	Push source code to Hugging Face Space
5.	Monitor build logs
6.	Access live demo

---

## 🙏 Credits
- Model: google/gemma-2-2b-it
- Platform: Hugging Face Spaces
- UI Framework: Gradio
- Speech Engine: Faster Whisper
- TTS System: PyDub + Soundfile

---

## 📣 Feedback & Contributions
Feel free to fork this Space, suggest improvements, or contribute new features.
Your feedback is highly appreciated!

---

## ⭐ If you like this project, don't forget to star the repository!

If you'd like:
- 📷 Screenshots section  
- 🎥 Video tutorial link area  
- 🏷 Badges (Deploy, Python, Gradio)  
- 👨‍💻 Author profile section  

Just tell me — I can enhance the README further 👍
