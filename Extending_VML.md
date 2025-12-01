# How To Add New VML Expansion Tags

**Extend the Voice Markup Language with your own commands**

VML is intentionally simple:
**each tag is just a function call embedded in angled brackets** inside the script text.

This guide shows exactly how to implement new tags, wire them into the parser, and make them affect audio generation.

---

## 1. Anatomy of a VML Tag

A VML tag looks like:

```
<COMMAND arg1="value" arg2="value">
```

The parser extracts:

• the command name
• the arguments (as strings)
• the position in the script

Each tag is routed to a handler function in Python.

Example built-in tag:

```
<VOICE name="amy">
```

gets routed to:

```python
handle_voice(args)
```

---

## 2. Where Tags Are Defined

In your current engine, there is a central **dispatcher**, usually something like:

```python
TAG_HANDLERS = {
    "VOICE": handle_voice,
    "MUSIC": handle_music,
    "SFX": handle_sfx,
    "WAIT": handle_wait,
}
```

To add a new VML command:

1. Write a new handler function
2. Add an entry to `TAG_HANDLERS`
3. Update the documentation

That’s all.

---

## 3. Step-by-Step: Adding a New Tag

Let’s walk through adding a new tag called `<PITCH shift="1.2">`.

### Step 1: Define the handler

Handler functions receive `args` and the engine context:

```python
def handle_pitch(engine, args):
    shift = float(args.get("shift", "1.0"))
    engine.set_pitch(shift)
```

If your engine doesn’t support pitch yet, you’d implement:

```python
class EngineState:
    def __init__(self):
        self.pitch = 1.0

    def set_pitch(self, value):
        self.pitch = value
```

Later, when TTS audio is rendered, this value modifies processing:

```python
audio = apply_pitch_shift(audio, self.pitch)
```

---

## 4. Wiring the Tag Into the Dispatcher

Add it to `TAG_HANDLERS`:

```python
TAG_HANDLERS = {
    "VOICE": handle_voice,
    "MUSIC": handle_music,
    "SFX": handle_sfx,
    "WAIT": handle_wait,
    "PITCH": handle_pitch,   # NEW
}
```

The parser immediately gains the ability to recognize `<PITCH>` tags.

---

## 5. Syntax Rules: Keeping VML Predictable

VML tags should follow these guidelines:

1. **Uppercase tag name**
2. **Arguments are always key="value"**
3. **No nested tags**
4. **Everything not inside `< >` is treated as text that should be spoken**
5. **Tags modify engine state or trigger an immediate action**

So:

```
<PITCH shift="0.8"> The monster growled…
```

Reader flow:

• engine pitch shifts
• TTS reads the next text segment at the new pitch
• pitch persists until changed or reset

---

## 6. Example: Adding a Fade Command

Let’s add:

```
<FADE music="5.0">
```

Meaning fade background music over 5 seconds.

### Handler:

```python
def handle_fade(engine, args):
    duration = float(args.get("music", "1.0"))
    engine.fade_music(duration)
```

### Dispatcher:

```python
TAG_HANDLERS["FADE"] = handle_fade
```

### Engine implementation:

```python
def fade_music(self, duration):
    # Queue a fade-out event
    self.timeline.append(("fade_music", duration))
```

---

## 7. Example: Adding a Choice System

Say you want the script to branch:

```
<CHOICE id="path" option="forest">
```

Handler:

```python
def handle_choice(engine, args):
    cid = args.get("id")
    option = args.get("option")
    engine.record_choice(cid, option)
```

Engine:

```python
choices = {}

def record_choice(self, cid, option):
    self.choices[cid] = option
```

---

## 8. Example: Add a TIMECODE Tag

```
<TIMECODE mark="battle_start">
```

Handler:

```python
def handle_timecode(engine, args):
    mark = args.get("mark")
    engine.add_marker(mark)
```

Engine:

```python
def add_marker(self, name):
    timestamp = self.timeline_duration()
    self.markers[name] = timestamp
```

---

## 9. Testing New Tags

Every new tag should have:

1. **A unit test** verifying event insertion
2. **A sample invocation**
3. **An audio test** to verify the effect is applied

Example test snippet:

```python
engine = Engine()
handle_pitch(engine, {"shift": "0.5"})
assert engine.pitch == 0.5
```

---

## 10. Updating the Documentation

Always update:

• README.md
• VML.md (schema)
• EXAMPLES.md

Describe:

• tag name
• arguments
• usage
• effect

Example doc block:

```
### <PITCH>

Adjusts synthesized speech pitch.

Attributes:
- shift: float multiplier (1.0 = normal)

Usage:
<PITCH shift="0.7"> The shadow whispered…
```

---

# Summary: Adding New Tags in 20 Seconds

1. Write a handler function
2. Add an entry in the dispatcher
3. Update the engine state or queue an action
4. Document the tag
5. Test it

VML remains simple, deterministic, and composable.


