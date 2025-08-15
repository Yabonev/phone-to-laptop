# Test: Limited Auto-Detect (English/Bulgarian only)

## Test Case 1: English Voice Message

**Arrange:**
- Set language to "auto" in bot settings
- Prepare English voice message

**Act:**
- Send English voice message saying "Hello, this is a test"

**Assert:**
- Language detected as "en"
- Text transcribed correctly in English
- No translation provided (since it's already English)

## Test Case 2: Bulgarian Voice Message

**Arrange:**
- Set language to "auto" in bot settings
- Prepare Bulgarian voice message

**Act:**
- Send Bulgarian voice message saying "Здравей, това е тест"

**Assert:**
- Language detected as "bg"
- Text transcribed correctly in Bulgarian
- English translation provided

## Test Case 3: Other Language (e.g., Spanish)

**Arrange:**
- Set language to "auto" in bot settings
- Prepare Spanish voice message

**Act:**
- Send Spanish voice message saying "Hola, esto es una prueba"

**Assert:**
- System detects it's not English
- Falls back to Bulgarian transcription
- Will attempt to transcribe as Bulgarian (may be inaccurate)
- Logs show: "Detected es, not English. Forcing Bulgarian transcription."
- English translation will be provided (of the Bulgarian-forced transcription)

## Implementation Details

The auto-detect now works as follows:
1. First attempts auto-detection with Whisper
2. If detected language is "en" (English), uses English transcription
3. If detected language is ANYTHING else, forces Bulgarian transcription
4. This creates a simple binary: English stays English, everything else becomes Bulgarian