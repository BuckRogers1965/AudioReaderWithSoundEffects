
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



Of course. Here is a professionally written section to continue your `README.md` file, covering the project's future potential and its use as an embeddable engine.

---

## 🚀 Project Roadmap & Future Vision

The current engine is a robust foundation for offline audio production. However, its modular design opens the door for powerful new features. The following roadmap outlines planned enhancements and potential avenues for development.

-   [ ] **Custom Voice Training & Fine-Tuning:**
    -   **Description:** Develop a streamlined workflow (potentially using Google Colab notebooks) to allow users to fine-tune Piper models on their own voice data. This enables true voice ownership and character creation.
    -   **Benefit:** Create a unique, consistent narrator for your brand, game, or podcast. The "not-quite-perfect" quality provides an ethical safeguard against deepfake misuse while establishing a distinct audio identity.

-   [ ] **Direct LLM & RAG Integration:**
    -   **Description:** Create a direct pipeline where a Large Language Model can generate a story *and* the VML tags for directing it.
    -   **Benefit:** Enable fully autonomous content creation. Imagine an AI Dungeon Master that not only describes the scene but also performs it with different voices, music, and sound effects, all generated in real-time.

-   [ ] **Immersive Spatial Audio (Panning):**
    -   **Description:** Implement new VML tags like `[pan:left]`, `[pan:right]`, or `[pan:0.7]` to control the stereo position of voices and sound effects.
    -   **Benefit:** Create a true 3D soundstage. A character could whisper in the listener's left ear, a door could slam on the right, and background music could remain centered, dramatically increasing immersion for audio dramas and games.

-   [ ] **Dynamic Sound Effects Engine:**
    -   **Description:** Allow SFX tags to point to directories instead of single files (e.g., `[sfx:sounds/footsteps/]`). The engine would randomly select a file from the directory to avoid repetition. Further enhancements could include slight, random pitch-shifting.
    -   **Benefit:** Drastically improves realism. Ten distinct footstep sounds are far more convincing than one sound played ten times.

-   [ ] **GUI / Web Interface:**
    -   **Description:** Build a simple front-end (using tools like Tkinter, Gradio, or a simple Flask web app) that provides a text editor for the VML script and a "Render" button.
    -   **Benefit:** Make the tool accessible to non-technical users like writers, narrative designers, and educators who want the power of VML without touching the command line.

---

## 📦 Using as an Embeddable Library

This script was designed not just as a standalone tool, but as a powerful **audio rendering backend** that can be imported into your own Python applications. The core logic is encapsulated and ready to be called.

This allows you to integrate dynamic, scripted audio generation into virtually any project.

### How It Works

The primary function, `process_vml_file()`, handles the entire workflow. You provide it with the path to a VML script and the desired output path, and it handles the rest.

### Example: Powering a Discord Bot

Imagine a Discord bot that can narrate user-submitted stories on command. The bot's code would simply generate a temporary VML file from the user's text and call the engine.

```python
import tempfile
import os
import voice_renderer # Assuming your script is named voice_renderer.py

def narrate_story_for_discord(story_text: str, author_voice: str) -> str:
    """
    Generates a narrated MP3 from user text and returns the file path.
    """
    # 1. Create the VML script dynamically
    vml_script = f"""
    [voice:{author_voice}]
    [rate:160]
    [bgm:music/fantasy_theme.mp3]
    [bgm_volume:0.2]
    
    {story_text}
    """

    # 2. Write the script to a temporary file
    with tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix=".txt") as temp_script:
        temp_script.write(vml_script)
        script_path = temp_script.name

    # 3. Define the output path
    output_path = os.path.join(tempfile.gettempdir(), "narration.mp3")

    # 4. Call the engine to render the audio
    try:
        print(f"Rendering audio for script: {script_path}")
        voice_renderer.process_vml_file(script_path, output_path)
        print(f"Audio successfully saved to: {output_path}")
        return output_path
    except Exception as e:
        print(f"An error occurred during rendering: {e}")
        return None
    finally:
        # 5. Clean up the temporary script file
        os.remove(script_path)

# --- Example Usage ---
# user_story = "The dragon swooped down from the mountain, its shadow covering the village."
# mp3_file_path = narrate_story_for_discord(user_story, "John")
# Now the Discord bot can upload and play mp3_file_path in a voice channel.
```

This pattern makes the VML engine the perfect audio backend for:
*   **Game Development (with Python engines like Godot):** Generate dynamic NPC dialogue with atmospheric effects.
*   **Content Creation Tools:** Build a web service that converts blog posts into podcasts.
*   **Accessibility Applications:** Create advanced screen readers that use different voices for quotes, headings, and body text.
