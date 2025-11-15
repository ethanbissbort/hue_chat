# Hue Chat Project Documentation

## Project Overview

**Hue Chat** is a Python CLI application that enables natural language control of Philips Hue smart lights using ChatGPT. Users can issue commands like "turn on the lights" or "make one light blue and the other red" and the application interprets them through ChatGPT to generate the appropriate JSON configurations for the Hue lights.

## Architecture & Key Components

### Core Modules

1. **main.py** (Entry Point)
   - Initializes the ChatBot and Hue bridge connection
   - Implements the main input loop: prompts user → gets ChatGPT response → applies to lights
   - Handles `JSONDecodeError` exceptions gracefully
   - Defines the system prompt (HEADER) that instructs ChatGPT on the exact JSON format required

2. **chat_bot.py** (ChatBot Class)
   - Manages OpenAI API communication
   - Maintains conversation history for context
   - Includes `trim()` function to extract JSON from ChatGPT responses (handles markdown code blocks)
   - Responsible for parsing structured responses from the API

3. **hue.py** (Hue Bridge)
   - Discovers Hue bridge on the local network using the `discoverhue` library
   - Handles initial bridge authentication (user must press button on bridge)
   - Returns a bridge object for controlling lights

4. **tests.py**
   - Unit tests for the `trim()` function
   - Validates that JSON extraction works correctly with various response formats

## System Flow

```
User Input
    ↓
ChatBot (sends to OpenAI with HEADER context)
    ↓
Parse JSON Response (trim function extracts from markdown)
    ↓
Apply to Hue Lights (iterate through commands, set color properties)
```

## Important Technical Details

### ChatGPT System Prompt (HEADER)

The system prompt defines:
- **Hue Scale**: 0-65535 (0=red, 7281=orange, 14563=yellow, 23665=green, 43690=blue, 50971=purple, 54612=pink)
- **Saturation**: 0-254 (color intensity)
- **Brightness**: 0-254 (light intensity)
- **Light IDs**: 0 and 1 (two lights controlled by this system)

### Expected JSON Format

ChatGPT must respond with a list of exactly two JSON objects:

```json
[
  {
    "light_id": 0,
    "color": {
      "hue": 43690,
      "saturation": 254,
      "brightness": 254
    }
  },
  {
    "light_id": 1,
    "color": {
      "hue": 43690,
      "saturation": 254,
      "brightness": 254
    }
  }
]
```

### Hue Light Control

Once JSON is parsed, the application:
1. Iterates through each command in the response list
2. Extracts `light_id` and `color` (dict with hue, saturation, brightness)
3. Gets the light object from the bridge: `bridge.lights[light_id]`
4. Sets attributes dynamically: `setattr(light, key, value)` for each color property

## Dependencies

- **openai** (v2.8.0) - Modern OpenAI API client library with improved async support and type hints
- **phue2** (v0.0.3) - Modernized fork of phue with type annotations and improved error handling
- **discoverhue** (v1.0.2) - Library for discovering Hue bridges on the network

## Setup & Running

### Prerequisites
- Python 3.x
- Hue bridge on the same WiFi network
- OpenAI API key (set as `OPENAI_API_KEY` environment variable)

### Installation
```bash
pip install -r requirements.txt
export OPENAI_API_KEY={your_api_key}
```

### First Run
On first execution, you must press the button on your Hue bridge to authorize the script.

### Running the Application
```bash
./main.py
```

Then enter commands at the prompt: "What should I do with the lights?"

## Recent Refactoring (API Updates)

### OpenAI API Upgrade (0.26.5 → 2.8.0)

The codebase was updated from the legacy OpenAI API to the modern 2.8.0 version:

**Changes Made:**
- Replaced `openai.ChatCompletion.create()` with `client.chat.completions.create()`
- Changed from module-level API key setting to client-based initialization
- Implemented lazy client initialization to support testing without API key
- Improved error handling with explicit `ValueError` when API key is missing

**Code Example - Before:**
```python
import openai
openai.api_key = os.environ["OPENAI_API_KEY"]
result = openai.ChatCompletion.create(model=model, messages=messages)
```

**Code Example - After:**
```python
from openai import OpenAI
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))  # Lazy init
result = client.chat.completions.create(model=model, messages=messages)
```

### Phue Library Upgrade (1.1 → phue2 0.0.3)

Upgraded from the legacy `phue` library to the modernized `phue2` fork to resolve setuptools compatibility issues with Python 3.11+:

**Benefits:**
- Type annotations for better IDE support
- Modern Python packaging
- Improved error handling
- API remains backward compatible with original phue

**Usage:** Imported as `import phue2 as phue` for seamless compatibility

## Development Guidelines

### Code Style
- Flat file structure (all modules in root directory)
- Python conventions and naming
- Error handling for JSON parsing failures
- Lazy initialization pattern for API clients

### Testing
- Run tests with: `python tests.py`
- Focus on the `trim()` function which is critical for response parsing
- Test cases cover various JSON response formats from ChatGPT

### Key Considerations for Modifications

1. **JSON Parsing**: The `trim()` function must reliably extract JSON from ChatGPT responses, which may include markdown code blocks or extra text
2. **API Rate Limits**: Be aware of OpenAI API rate limits when testing
3. **Light Control**: The system supports exactly 2 lights with IDs 0 and 1
4. **Hue Values**: Use the predefined color mappings in HEADER to ensure consistent color naming

## Error Handling

The main loop catches `JSONDecodeError` exceptions when ChatGPT responses cannot be parsed as valid JSON. When this occurs, the user is prompted to try again.

## Future Enhancement Areas

- Support for more than 2 lights (make light_id dynamic)
- Additional color presets or custom color specification
- Scene management (save/recall light configurations)
- More robust error messages to guide users when commands fail
- Extended command types (brightness, saturation only, etc.)
