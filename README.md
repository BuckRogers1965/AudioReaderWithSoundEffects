
# 🎙️ Open VML Audio Engine
### 100% Offline, Free, & Private AI Text-to-Speech Renderer

**Stop paying per-character API fees.** 

The **Open VML (Voice Markup Language) Engine** is a Python-based audio renderer that turns text files into professional-grade audio productions. It uses **Piper**—a fast, neural text-to-speech system—to generate high-quality voices entirely on your local machine.

No OpenAI API keys. No cloud dependency. No data tracking.

## ⚡ Features
*   **Fully Offline:** Runs on your CPU (Raspberry Pi to Gaming PC).
*   **Zero Cost:** Uses open-source neural models.
*   **Multi-Track Mixing:** Automatically mixes background music (`[bgm]`) and sound effects (`[sfx]`) with the voice.
*   **Dynamic Control:** Change voices, speed, and volume mid-script using simple tags.

---

## 🛠️ Installation

### 1. System Requirements
You need **Python 3.9+** and **FFmpeg** installed.

*   **Ubuntu/Debian:** `sudo apt install ffmpeg`
*   **MacOS:** `brew install ffmpeg`
*   **Windows:** Download FFmpeg and add it to your PATH.

### 2. Install the Piper Binary
This script relies on the `piper` command line tool.
1.  Download the appropriate binary for your OS from the [Piper GitHub Releases](https://github.com/rhasspy/piper/releases).
2.  Extract the archive.
3.  Add the `piper` folder to your system `PATH` (so you can type `piper` in any terminal window).

### 3. Install Python Dependencies
```bash
pip install pydub
```

---

## 🗣️ Setting Up Voices (Crucial!)

This is the most important step. Piper requires **two files** for every voice. If you miss the JSON file, the engine will fail.

1.  **The Model:** `voice-name.onnx` (Contains the AI weights)
2.  **The Config:** `voice-name.onnx.json` (Contains the audio settings)

### Where to get voices
We recommend the **Hugging Face** repository.

**Option A: The Easy Way (Download all US English voices)**
Requires `huggingface_hub` installed (`pip install huggingface_hub`).

```bash
# Create a folder for voices
mkdir piper_voices

# Download only the en_US voices (excludes other languages to save space)
huggingface-cli download rhasspy/piper-voices --include "en/en_US/*" --local-dir piper_voices
```

**Option B: The Manual Way**
1.  Go to the [Piper Voices Hugging Face Page](https://huggingface.co/rhasspy/piper-voices/tree/main/en/en_US).
2.  Browse to a voice (e.g., `en_US/amy/medium/`).
3.  **Download BOTH** `.onnx` and `.onnx.json`.
4.  Place them in your `piper_voices/` directory.

### 📝 Configuring the Script
Open `voice_renderer_os.py` and update the `PIPER_MODELS` dictionary to point to your files:

```python
PIPER_MODELS = {
    "John": "piper_voices/en_US-john-medium.onnx",
    "Amy": "piper_voices/en_US-amy-medium.onnx",
    # ensure the .onnx.json file exists in the same folder!
}
```

---

## 🎬 How to Use

### 1. Write your Script (.txt)
Create a text file (e.g., `story.txt`) using VML tags:

```text
[voice:John]
[rate:150]
[bgm:music/epic_soundtrack.mp3]
[bgm_volume:0.3]

The year is 2049. The servers have gone silent.

[pause:1]
[sfx:sfx/power_down.wav]
[voice:Amy]
[rate:160]
System failure imminent. Rerouting power to the neural net.

[voice:John]
We have to move. Now.
```

### 2. Render the Audio
Run the python script pointing to your text file and desired output file.

```bash
python voice_renderer_os.py story.txt output.mp3
```

---

## ⚠️ Troubleshooting

**Error: `FileNotFoundError: ... .onnx.json`**
*   **Cause:** You downloaded the `.onnx` file but forgot the matching `.json` configuration file.
*   **Fix:** Go back to the source and download the JSON file with the exact same name as the voice model.

**Error: `No Piper model configured...`**
*   **Cause:** The voice name in your text file (e.g., `[voice:Chad]`) isn't in your `PIPER_MODELS` dictionary, or the path is wrong.
*   **Fix:** Edit `voice_renderer_os.py` and ensure the path points to the actual `.onnx` file.

**Audio sounds incredibly fast or slow**
*   **Fix:** Piper models are trained at different native speeds. Adjust the `[rate:150]` tag. 150 is standard, 180 is brisk, 120 is slow.
