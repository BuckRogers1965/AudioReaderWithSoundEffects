# VML Persona Extension Specification

## Version 1.0

---

## Overview

The Persona Extension adds character-based voice management to VML (Voice Markup Language). Instead of manually setting voice parameters for each character, personas bundle voice model, rate, volume, and other attributes into reusable character profiles.

## Motivation

Traditional VML requires repetitive parameter setting:

```vml
[voice:Amy]
[rate:140]
[volume:0.9]
The Dark Queen spoke with authority.

[voice:John]
[rate:160]
[volume:1.0]
The hero responded boldly.
```

Personas simplify this to:

```vml
[persona:Dark_Queen]
The Dark Queen spoke with authority.

[persona:Hero]
The hero responded boldly.
```

## Specification

### 1. Persona Definition

Personas are defined in a configuration structure (Python dict, JSON, YAML, etc.) that can contain **any valid VML parameter**.

```python
PERSONAS = {
    "persona_name": {
        "voice": "path/to/voice-model.onnx",  # Required
        "rate": 150,                            # Optional
        "volume": 1.0,                          # Optional
        "pitch": 1.0,                           # Optional - future
        "pan": 0.0,                             # Optional - future  
        "effects": ["reverb", "echo"],          # Optional - future
        # ... any other VML parameter
    }
}
```

**Required Fields:**
- `voice`: Path to the Piper `.onnx` voice model file

**Optional Fields:**
Personas can include **any current or future VML parameter**, including but not limited to:

- `rate`: Speech rate (words per minute). Range: 80-200. Default: 150
- `volume`: Audio volume multiplier. Range: 0.0-2.0. Default: 1.0
- `pitch`: Voice pitch adjustment (when implemented)
- `pan`: Stereo positioning, -1.0 = left, 1.0 = right (when implemented)
- `effects`: Array of audio effects like reverb, echo, etc. (when implemented)
- `pause_after`: Automatic pause duration after each line
- `emphasis`: Default emphasis level for this character
- Any future VML extension parameter

**Design Principle:**
The persona system is **parameter-agnostic**. When new VML tags are added to the engine, they automatically become available in persona definitions without requiring changes to the persona specification.

### 2. Persona Tag Syntax

```vml
[persona:persona_name]
```

**Behavior:**
- Loads all parameters associated with `persona_name`
- Remains active until another `[persona:]` or `[voice:]` tag is encountered
- If persona not found, engine should raise an error with available persona list

### 3. Parameter Override

Individual parameters can be temporarily overridden after setting a persona:

```vml
[persona:Dark_Queen]
The Dark Queen spoke normally.

[rate:100]
But now... she speaks... very... slowly.

[persona:Dark_Queen]
And now she's back to her normal cadence.
```

**Override Rules:**
- Overrides apply immediately after the tag
- Overrides persist until the next `[persona:]` tag
- Setting a new persona resets all parameters to that persona's defaults

### 4. Backward Compatibility

The persona system must coexist with legacy VML tags:

```vml
[persona:Narrator]
The story begins.

[voice:en_US-custom-voice.onnx]
[rate:140]
This uses the old manual method.

[persona:Hero]
And we're back to personas.
```

**Compatibility Rules:**
- `[voice:]` tags continue to work as before
- Switching from persona to manual voice clears persona state
- Switching from manual voice to persona applies full persona configuration

### 5. Error Handling

**Undefined Persona:**
```
Error: Persona 'Villian' not found. Available personas: ['Dark_Queen', 'Hero', 'Narrator']
(Did you mean 'Villain'?)
```

**Missing Voice Model:**
```
Error: Persona 'Hero' references voice model 'hero-voice.onnx' which does not exist at path: /voices/hero-voice.onnx
```

**Invalid Parameters:**
```
Warning: Persona 'Speed_Talker' has rate=350 which exceeds maximum (200). Clamping to 200.
```

## Implementation Guide

### Step 1: Define Your Personas

Create a `personas.py` configuration file:

```python
PERSONAS = {
    "Narrator": {
        "voice": "piper_voices/en_US-libritts-high.onnx",
        "rate": 150,
        "volume": 0.85
    },
    "Dark_Queen": {
        "voice": "piper_voices/en_US-amy-medium.onnx",
        "rate": 140,
        "volume": 0.9,
        "pan": -0.3,           # Slightly left (when implemented)
        "effects": ["reverb"]  # Add echo to her voice (when implemented)
    },
    "Hero": {
        "voice": "piper_voices/en_US-john-medium.onnx",
        "rate": 160,
        "volume": 1.0,
        "pan": 0.3             # Slightly right (when implemented)
    },
    "Old_Wizard": {
        "voice": "piper_voices/en_US-norman-medium.onnx",
        "rate": 130,
        "volume": 0.95,
        "pitch": 0.9,          # Lower pitch (when implemented)
        "pause_after": 0.5     # Dramatic pauses (when implemented)
    },
    "Ghost": {
        "voice": "piper_voices/en_US-amy-medium.onnx",
        "rate": 120,
        "volume": 0.6,
        "effects": ["reverb", "echo"],  # Ethereal sound (when implemented)
        "pan": -1.0            # Far left for spooky effect (when implemented)
    }
}
```

### Step 2: Modify the VML Parser

Add persona handling to your tag parser with **future-proof parameter handling**:

```python
import re
from personas import PERSONAS

def parse_persona_tag(line, current_state):
    """
    Parse [persona:name] tags and update current state.
    
    This function is parameter-agnostic - it applies ALL parameters
    defined in the persona, regardless of what they are. This means
    new VML features automatically work in personas without code changes.
    
    Args:
        line: The VML line to parse
        current_state: Dict containing all current VML parameters
    
    Returns:
        Updated state dict or None if no persona tag found
    """
    match = re.search(r'\[persona:(\w+)\]', line)
    if match:
        persona_name = match.group(1)
        
        if persona_name not in PERSONAS:
            available = ', '.join(PERSONAS.keys())
            raise ValueError(
                f"Persona '{persona_name}' not found. "
                f"Available personas: [{available}]"
            )
        
        persona = PERSONAS[persona_name]
        
        # Apply ALL parameters from the persona definition
        # This works for current parameters AND future extensions
        current_state.update(persona)
        current_state['current_persona'] = persona_name
        
        return current_state
    
    return None
```

**Key Design Feature:**
The `current_state.update(persona)` approach means:
- When you add `[pan:]` support to your engine, personas with `pan` values automatically work
- When you add `[effects:]` support, personas with effects automatically work
- No changes to the persona parser needed for future VML extensions

### Step 3: Integrate into Main Engine

Update your main VML processing loop:

```python
def process_vml_file(input_file, output_file):
    state = {
        'voice': None,
        'rate': 150,
        'volume': 1.0,
        'current_persona': None
    }
    
    with open(input_file, 'r') as f:
        for line in f:
            # Try persona first
            new_state = parse_persona_tag(line, state)
            if new_state:
                state = new_state
                continue
            
            # Fall back to legacy tags
            if '[voice:' in line:
                # Parse voice tag, clear persona
                state['current_persona'] = None
                # ... existing voice parsing logic
            
            # ... rest of your VML processing
```

### Step 4: Create Example VML Script

Create a test file `epic_battle.vml`:

```vml
[bgm:music/epic_battle.mp3]
[bgm_volume:0.3]

[persona:Narrator]
The throne room fell silent as the Dark Queen rose from her seat.

[pause:1]

[persona:Dark_Queen]
You dare challenge me, mortal?

[sfx:sfx/thunder.wav]

[persona:Hero]
[rate:170]
Your reign of terror ends today!

[persona:Dark_Queen]
[rate:120]
Foolish... child.

[sfx:sfx/magic_blast.wav]

[persona:Narrator]
And thus began the final battle that would decide the fate of the realm.
```

### Step 5: Test and Validate

Run your test script:

```bash
python voice_renderer_os.py epic_battle.vml output.mp3
```

Verify:
- ✓ Each persona uses correct voice model
- ✓ Rate and volume are applied correctly
- ✓ Persona switches happen cleanly
- ✓ Parameter overrides work as expected
- ✓ Error messages are helpful

## Benefits

1. **Writer-Friendly**: Think in characters, not parameters
2. **Consistency**: Characters always sound the same across projects
3. **Maintainability**: Change a voice model once, updates everywhere
4. **Readability**: VML scripts are cleaner and more narrative-focused
5. **Scalability**: Easy to add new characters to your voice library

## Example Use Cases

### Audio Drama Production
```vml
[persona:Detective_Morgan]
The evidence doesn't add up, chief.

[persona:Chief_Richards]
Then find me someone who can make it add up.
```

### Interactive Fiction
```python
# Generate dynamic dialogue
persona = "Friendly_NPC" if player_karma > 0 else "Hostile_NPC"
dialogue = f"[persona:{persona}]\n{npc_response_text}"
```

### Educational Content
```vml
[persona:Teacher]
Today we'll learn about photosynthesis.

[persona:Student_Curious]
How do plants make food from sunlight?

[persona:Teacher]
Great question! Let me explain...
```

## Migration from Legacy VML

Existing VML scripts continue to work without modification. To migrate:

1. Identify repeated voice/rate/volume patterns
2. Create persona definitions for each pattern
3. Replace parameter blocks with `[persona:]` tags
4. Test thoroughly

**Before:**
```vml
[voice:Amy][rate:140][volume:0.9]
Text here
[voice:Amy][rate:140][volume:0.9]
More text
```

**After:**
```vml
[persona:Dark_Queen]
Text here
More text
```

## Conclusion

The Persona Extension transforms VML from a technical voice control system into a character performance platform. By bundling parameters into memorable character profiles, content creators can focus on storytelling rather than voice configuration.