# Create a folder for voices
mkdir piper_voices

# Download only the en_US voices (excludes other languages to save space)

```bash
huggingface-cli download rhasspy/piper-voices --include "en/en_US/*" --local-dir piper_voices
```

# Option B: The Manual Way
- Go to the Piper Voices Hugging Face Page.
- Browse to a voice (e.g., en_US/amy/medium/).
- Download BOTH .onnx and .onnx.json.
- Place them in your piper_voices/ directory.

# Configuring the Script
Open voice_renderer.py and update the PIPER_MODELS dictionary to point to your files:

```Python
PIPER_MODELS = {
    "John": "piper_voices/en_US-john-medium.onnx",
    "Amy": "piper_voices/en_US-amy-medium.onnx",
    # ensure the .onnx.json file exists in the same folder!
}
```
