"""
VML Audio Engine (AI Voice Edition)
-----------------------------------
Reads a text file with Voice Markup Language (VML) commands and produces a
narrated MP3 file with background music, sound effects, pauses, and AI voices.

Uses Piper TTS for offline, open-source, high-quality speech synthesis.

Author: You
"""

import os
import re
import argparse
import tempfile
import subprocess
from pathlib import Path
from pydub import AudioSegment
from math import log10


# ---------------------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------------------

# Map VML [voice:Name] to Piper model files
PIPER_MODELS = {
    "Alex":      "voices/en_US-alex.onnx",
    "Samantha":  "voices/en_US-samantha.onnx",
    "Narrator":  "voices/en_GB-narrator.onnx",
    "Hero":      "voices/en_US-hero.onnx",
    "Villain":   "voices/en_US-villain.onnx",
}

# ---------------------------------------------------------------------
# UTILITIES
# ---------------------------------------------------------------------

def db_from_volume(vol):
    return 20 * log10(vol) if vol > 0 else -float('inf')


# ---------------------------------------------------------------------
# PIPER AI TTS IMPLEMENTATION
# ---------------------------------------------------------------------

def synthesize_text(text, voice_name, rate, out_path):
    """
    TTS using Piper.
    Piper does not natively support rate control, so we generate audio,
    then apply pitch-independent speed adjustment using pydub.
    """

    model = PIPER_MODELS.get(voice_name)
    if not model:
        raise ValueError(f"No Piper model configured for voice '{voice_name}'.")

    # Temporary intermediate WAV
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
        raw_tts_path = tmp.name

    # Run Piper
    subprocess.run(
        [
            "piper",
            "--model", model,
            "--output_file", raw_tts_path
        ],
        input=text.encode("utf8"),
        check=True
    )

    # Load and adjust speed
    audio = AudioSegment.from_wav(raw_tts_path)

    if rate != 180:
        factor = rate / 180
        audio = audio._spawn(audio.raw_data, overrides={
            "frame_rate": int(audio.frame_rate * factor)
        }).set_frame_rate(audio.frame_rate)

    audio.export(out_path, format="wav")
    os.remove(raw_tts_path)


# ---------------------------------------------------------------------
# MAIN VML PROCESSOR
# ---------------------------------------------------------------------

def process_vml_file(input_path, output_path, fade_duration=2000):
    # Default state
    voice = "Narrator"
    rate = 180
    voice_vol = 1.0
    bgm_vol = 0.4
    sfx_vol = 1.0

    segments = []
    temp_files = []
    bgm_segments = []
    sfx_segments = []
    current_bgm = None
    bgm_start_index = 0
    current_time = 0
    current_text = ""

    with open(input_path, 'r') as f:
        lines = f.readlines()

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # -------------------------
        # COMMANDS
        # -------------------------

        if m := re.match(r"\[voice:(.*?)\]", line):
            voice = m.group(1).strip()
            continue

        elif m := re.match(r"\[rate:(\d+)\]", line):
            rate = int(m.group(1))
            continue

        elif m := re.match(r"\[voice_volume:(.*?)\]", line):
            voice_vol = float(m.group(1))
            continue

        elif m := re.match(r"\[bgm_volume:(.*?)\]", line):
            bgm_vol = float(m.group(1))
            continue

        elif m := re.match(r"\[sfx_volume:(.*?)\]", line):
            sfx_vol = float(m.group(1))
            continue

        elif m := re.match(r"\[pause:(.*?)\]", line):
            if current_text:
                tts_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
                synthesize_text(current_text, voice, rate, tts_file.name)
                tts_audio = AudioSegment.from_file(tts_file.name) + db_from_volume(voice_vol)
                segments.append({'type': 'voice', 'audio': tts_audio})
                temp_files.append(tts_file.name)
                current_time += len(tts_audio)
                current_text = ""

            pause_ms = float(m.group(1)) * 1000
            segments.append({'type': 'pause', 'audio': AudioSegment.silent(duration=int(pause_ms))})
            current_time += pause_ms
            continue

        elif m := re.match(r"\[bgm:(.*?)\]", line):
            if current_text:
                tts_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
                synthesize_text(current_text, voice, rate, tts_file.name)
                tts_audio = AudioSegment.from_file(tts_file.name) + db_from_volume(voice_vol)
                segments.append({'type': 'voice', 'audio': tts_audio})
                temp_files.append(tts_file.name)
                current_time += len(tts_audio)
                current_text = ""

            if current_bgm:
                bgm_segments.append((current_bgm, bgm_start_index, len(segments)))

            current_bgm = m.group(1).strip()
            bgm_start_index = len(segments)
            continue

        elif m := re.match(r"\[sfx:(.*?)\]", line):
            if current_text:
                tts_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
                synthesize_text(current_text, voice, rate, tts_file.name)
                tts_audio = AudioSegment.from_file(tts_file.name) + db_from_volume(voice_vol)
                segments.append({'type': 'voice', 'audio': tts_audio})
                temp_files.append(tts_file.name)
                current_time += len(tts_audio)
                current_text = ""

            sfx_name = m.group(1).strip()
            try:
                sfx = AudioSegment.from_file(sfx_name)
            except FileNotFoundError:
                print(f"⚠️ SFX not found: {sfx_name}")
                continue

            sfx += db_from_volume(sfx_vol)
            sfx_segments.append((sfx, current_time))
            continue

        # -------------------------
        # ACCUMULATE TEXT
        # -------------------------

        current_text += " " + line

    # Final flush
    if current_text:
        tts_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
        synthesize_text(current_text, voice, rate, tts_file.name)
        tts_audio = AudioSegment.from_file(tts_file.name) + db_from_volume(voice_vol)
        segments.append({'type': 'voice', 'audio': tts_audio})
        temp_files.append(tts_file.name)
        current_time += len(tts_audio)

    # Close BGM range
    if current_bgm:
        bgm_segments.append((current_bgm, bgm_start_index, len(segments)))

    # --------------------------------------------------------------
    # AUDIO COMPOSITION
    # --------------------------------------------------------------

    voice_track = AudioSegment.silent(duration=0)
    cue_points = [0]

    for seg in segments:
        voice_track += seg['audio']
        cue_points.append(len(voice_track))

    final_mix = voice_track

    for bgm_file, start_idx, end_idx in bgm_segments:
        try:
            bgm = AudioSegment.from_file(bgm_file).low_pass_filter(5000)
        except FileNotFoundError:
            print(f"⚠️ BGM not found: {bgm_file}")
            continue

        start_time = cue_points[start_idx]
        end_time = cue_points[end_idx]
        duration = end_time - start_time

        bgm = bgm * (duration // len(bgm) + 1)
        bgm = bgm[:duration].fade_in(fade_duration).fade_out(fade_duration)
        bgm += db_from_volume(bgm_vol)

        final_mix = final_mix.overlay(bgm, position=start_time)

    for sfx_audio, pos in sfx_segments:
        final_mix = final_mix.overlay(sfx_audio, position=int(pos))

    final_mix.export(output_path, format="mp3")
    print(f"✅ Output saved: {output_path}")

    for f in temp_files:
        os.remove(f)


# ---------------------------------------------------------------------
# HELP SCREEN
# ---------------------------------------------------------------------

def print_help():
    print("""
Voice Markup Language (VML) Commands:

  [voice:Name]         Set voice (must match your Piper model name)
  [rate:180]           Set speech speed
  [pause:2.5]          Insert pause in seconds
  [bgm:track.mp3]      Play background music across sections
  [bgm_volume:0.4]     Set BGM level 0.0–1.0
  [voice_volume:1.0]   Set voice level
  [sfx:ding.wav]       Play a sound effect
  [sfx_volume:1.0]     Set SFX level

Usage:
  python vml_audio_engine.py input.vml output.mp3
    """)


# ---------------------------------------------------------------------
# ENTRY POINT
# ---------------------------------------------------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("input", nargs="?", help="Input VML file")
    parser.add_argument("output", nargs="?", help="Output MP3")
    parser.add_argument("--help", action="store_true")
    args = parser.parse_args()

    if args.help or not args.input or not args.output:
        print_help()
    else:
        process_vml_file(args.input, args.output)

