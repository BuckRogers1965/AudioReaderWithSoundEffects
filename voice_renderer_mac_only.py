"""
VML Audio Engine
-----------------
A Python program that reads a text file with Voice Markup Language (VML) commands
and produces a narrated MP3 file with optional background music, sound effects, and
control over voice, rate, volume, and pauses.

Author: [Your Name]
"""

import os
import re
import argparse
import tempfile
import pyttsx3
from pydub import AudioSegment
from math import log10

def db_from_volume(vol):
    return 20 * log10(vol) if vol > 0 else -float('inf')

def synthesize_text(text, voice_name, rate, out_path):
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')
    for voice in voices:
        if voice_name.lower() in voice.name.lower():
            engine.setProperty('voice', voice.id)
            break
    engine.setProperty('rate', rate)
    engine.save_to_file(text, out_path)
    engine.runAndWait()

def process_vml_file(input_path, output_path, fade_duration=2000):
    # Default settings
    voice = "Alex"
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
    current_sfx_end = 0

    with open(input_path, 'r') as f:
        lines = f.readlines()

    for idx, line in enumerate(lines):
        line = line.strip()
        if not line:
            continue

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
                tts_temp = tempfile.NamedTemporaryFile(delete=False, suffix=".aiff")
                synthesize_text(current_text, voice, rate, tts_temp.name)
                tts_audio = AudioSegment.from_file(tts_temp.name) + db_from_volume(voice_vol)
                segments.append({'type': 'voice', 'audio': tts_audio})
                temp_files.append(tts_temp.name)
                current_time += len(tts_audio)
                current_text = ""
            pause_duration = float(m.group(1)) * 1000
            segments.append({'type': 'pause', 'audio': AudioSegment.silent(duration=int(pause_duration))})
            current_time += pause_duration
            continue
        elif m := re.match(r"\[bgm:(.*?)\]", line):
            if current_text:
                tts_temp = tempfile.NamedTemporaryFile(delete=False, suffix=".aiff")
                synthesize_text(current_text, voice, rate, tts_temp.name)
                tts_audio = AudioSegment.from_file(tts_temp.name)
                tts_audio += db_from_volume(voice_vol)
                segments.append({'type': 'voice', 'audio': tts_audio})
                temp_files.append(tts_temp.name)
                current_time += len(tts_audio)
                current_text = ""
            if current_bgm:
                bgm_segments.append((current_bgm, bgm_start_index, len(segments)))
            current_bgm = m.group(1).strip()
            bgm_start_index = len(segments)
            continue
        elif m := re.match(r"\[sfx:(.*?)\]", line):
            if current_text:
                tts_temp = tempfile.NamedTemporaryFile(delete=False, suffix=".aiff")
                synthesize_text(current_text, voice, rate, tts_temp.name)
                tts_audio = AudioSegment.from_file(tts_temp.name)
                tts_audio += db_from_volume(voice_vol)
                segments.append({'type': 'voice', 'audio': tts_audio})
                temp_files.append(tts_temp.name)
                current_time += len(tts_audio)
                current_text = ""

            sfx_file = m.group(1).strip()
            # --- START OF ADDED CODE ---
            try:
                sfx = AudioSegment.from_file(sfx_file)
            except FileNotFoundError:
                print(f"⚠️ Warning: SFX file not found: {sfx_file}. Skipping.")
                continue
            # --- END OF ADDED CODE ---
            sfx += db_from_volume(sfx_vol)

            # Trim the previous SFX if it's still playing
            if sfx_segments:
                prev_sfx, prev_start = sfx_segments[-1]
                trim_duration = max(0, current_time - prev_start)
                sfx_segments[-1] = (prev_sfx[:trim_duration], prev_start)

            sfx_segments.append((sfx, current_time))
            current_sfx_end = current_time + len(sfx)
            continue

        current_text += " " + line

    if current_text:
        tts_temp = tempfile.NamedTemporaryFile(delete=False, suffix=".aiff")
        synthesize_text(current_text, voice, rate, tts_temp.name)
        tts_audio = AudioSegment.from_file(tts_temp.name)
        tts_audio += db_from_volume(voice_vol)
        segments.append({'type': 'voice', 'audio': tts_audio})
        temp_files.append(tts_temp.name)
        current_time += len(tts_audio)

    if current_bgm:
        bgm_segments.append((current_bgm, bgm_start_index, len(segments)))

    voice_track = AudioSegment.silent(duration=0)
    cue_points = [0]

    for seg in segments:
        voice_track += seg['audio']
        cue_points.append(len(voice_track))

    final_mix = voice_track

    for bgm_file, start_idx, end_idx in bgm_segments:
        start_time = cue_points[start_idx]
        end_time = cue_points[end_idx]
        duration = end_time - start_time

        # --- START OF ADDED CODE ---
        try:
            bgm = AudioSegment.from_file(bgm_file).low_pass_filter(5000)
        except FileNotFoundError:
            print(f"⚠️ Warning: BGM file not found: {bgm_file}. Skipping.")
            continue
        # --- END OF ADDED CODE ---
        bgm = bgm * (duration // len(bgm) + 1)
        bgm = bgm[:duration].fade_in(fade_duration).fade_out(fade_duration)
        bgm += db_from_volume(bgm_vol)
        final_mix = final_mix.overlay(bgm, position=start_time)

    for sfx_audio, position in sfx_segments:
        final_mix = final_mix.overlay(sfx_audio, position=int(position))

    final_mix.export(output_path, format="mp3")
    print(f"✅ Output saved to {output_path}")

    for f in temp_files:
        os.remove(f)

def print_help():
    print("""
Voice Markup Language (VML) Commands:

  [voice:Name]         Set voice (e.g., Alex, Samantha)
  [rate:180]           Set voice speed (default: 180)
  [pause:2.5]          Insert 2.5 second pause
  [bgm:track.mp3]      Set background music with smooth fade
  [bgm_volume:0.4]     Set background music volume (0.0–1.0)
  [voice_volume:1.0]   Set voice volume
  [sfx:ding.wav]       Insert sound effect (overlays current audio)
  [sfx_volume:1.0]     Set SFX volume

Usage:
  python vml_audio_engine.py input.vml output.mp3
  python vml_audio_engine.py --help
    """)

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
