# Test: Simple Language Selection (English/Bulgarian only)

## Test Case 1: English Voice Message

**Arrange:**
- Set language to "English" via /language command
- Prepare English voice message

**Act:**
- Send English voice message saying "This is a test in English"

**Assert:**
- Text transcribed in English
- NO translation provided
- Notes file shows only the English text

## Test Case 2: Bulgarian Voice Message with Translation

**Arrange:**
- Set language to "Bulgarian" via /language command
- Prepare Bulgarian voice message

**Act:**
- Send Bulgarian voice message saying "Това е тест на български"

**Assert:**
- Text transcribed in Bulgarian
- English translation provided
- Notes file shows:
  - **Bulgarian:** [transcribed text]
  - **English:** [translation]

## Test Case 3: Default Language (English)

**Arrange:**
- Fresh bot state or invalid language setting

**Act:**
- Send voice message without setting language

**Assert:**
- Defaults to English transcription
- No translation provided

## Implementation Summary

- **No auto-detect**: User must explicitly choose English or Bulgarian
- **Default**: English (when state is fresh or invalid)
- **Translation**: Only happens when Bulgarian is explicitly selected
- **Offline behavior**: Always uses English (as per old bot.py logic)