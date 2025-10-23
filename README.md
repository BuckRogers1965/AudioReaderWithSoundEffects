# AudioReaderWithSoundEffects
This takes a simply formatted text file and reads the text following embedded commands to include background sound track and sound effects.

> A Python tool to render narrated audio from a markup script.

Sorry I cannot incude the audio files for the test.vml file.  Copyright being what it is, you can find similar files on the Internet.

The VML Audio Engine reads a text file written in Voice Markup Language (VML) and produces a final, mixed MP3 file. It provides script-based control over voice selection, speech rate, volume levels, pauses, background music, and sound effects.

**This script is currently designed for and tested on macOS only.** To make it work on Windows or Linux, you must modify the source code as described in the **"Modifying the Code for Cross-Platform Compatibility"** section below.  I plan to do this at some point in the future, but for me now, this script does what I need it to do.

## Design Philosophy

The engine's behavior is intentional:

*   **State-Based Settings:** Commands like `[bgm_volume:0.5]` set a state. This volume level is applied to all subsequent `[bgm]` tracks until a new volume command is issued. The volume is not tied to the audio file it precedes in the script; it is a global state that you modify.
*   **Interruptible Sound Effects:** The `[sfx]` command is designed for short, sharp audio cues. When a new `[sfx]` command is processed, it immediately terminates any sound effect from a previous `[sfx]` command that is still playing. This prevents overlapping sound effects and allows for rapid sequences. For long-running, uninterruptible audio, use the `[bgm]` command.

## Requirements

*   Python 3.x
*   **FFmpeg**
*   Python packages: `pyttsx3`, `pydub`

## Installation

1.  **Clone the repository:** `git clone https://github.com/your-username/vml-audio-engine.git`
2.  **Install packages:** `pip install pyttsx3 pydub`
3.  **Install FFmpeg:** Use a package manager like Homebrew (`brew install ffmpeg`), Chocolatey (`choco install ffmpeg`), or apt (`sudo apt-get install ffmpeg`).

## Usage

```bash
python voice_renderer.py <input_vml_file> <output_mp3_file>
```

To see the command list: `python voice_renderer.py --help`

## VML Command Guide

| Command                 | Description                                                                  |
| ----------------------- | ---------------------------------------------------------------------------- |
| `[voice:Name]`          | Sets the TTS voice.                                                          |
| `[rate:180]`            | Sets the voice speed in words per minute.                                    |
| `[voice_volume:1.0]`    | Sets the global state for voice volume.                                      |
| `[bgm_volume:0.4]`      | Sets the global state for background music volume.                           |
| `[sfx_volume:1.0]`      | Sets the global state for sound effect volume.                               |
| `[pause:2.5]`           | Inserts a silent pause for the specified number of seconds.                  |
| `[bgm:path/track.mp3]`  | Starts a background music track using the current `bgm_volume` state.        |
| `[sfx:path/ding.wav]`   | Plays a sound effect, interrupting any previous SFX still playing.           |


---

## Modifying the Code for Cross-Platform Compatibility

To make `voice_renderer.py` work on Windows and Linux, two parts of the code must be changed.

### 1. Fix the Hardcoded Temporary File Format

The script saves temporary TTS audio as `.aiff` files, a format that is not standard outside of the Apple ecosystem. This must be changed to the universal `.wav` format.

**Action:**
Open `voice_renderer.py` and locate the `process_vml_file` function. Find the two lines that create a `NamedTemporaryFile` and change the suffix.

**Change this:**
```python
tts_temp = tempfile.NamedTemporaryFile(delete=False, suffix=".aiff")
```
**To this:**
```python
tts_temp = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
```
*This change must be made in **two places** within the function.*

### 2. Fix the Reliance on macOS Voices

The VML script relies on voice names like "Alex" and "Samantha," which only exist on macOS. A cross-platform script needs a way for the user to discover and use the voices available on their own system.

**Action:**
Add a command-line argument (`--list-voices`) that prints all available TTS voices and then exits.

**In `voice_renderer.py`, modify the `if __name__ == "__main__":` block at the end of the file:**

**Replace this existing block:**
```python
if __name__ == "__main__":
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("input", nargs="?", help="Input VML script file")
    parser.add_argument("output", nargs="?", help="Output MP3 file")
    parser.add_argument("--help", action="store_true")
    args = parser.parse_args()

    if args.help or not args.input or not args.output:
        print_help()
    else:
        process_vml_file(args.input, args.output)
```
**With this new block:**
```python
def list_voices():
    """Prints all available TTS voices."""
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')
    print("Available voices on this system:")
    for voice in voices:
        print(f"- {voice.name}")
    engine.stop()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("input", nargs="?", help="Input VML script file")
    parser.add_argument("output", nargs="?", help="Output MP3 file")
    parser.add_argument("--help", action="store_true", help="Show this help message and command list")
    parser.add_argument("--list-voices", action="store_true", help="List all available TTS voices and exit")
    args = parser.parse_args()

    if args.list_voices:
        list_voices()
    elif args.help or not args.input or not args.output:
        print_help()
    else:
        process_vml_file(args.input, args.output)
```

After making these two code changes, the script will be cross-platform. Users on Windows and Linux can run `python voice_renderer.py --list-voices` to see which voice names to use in their VML files.