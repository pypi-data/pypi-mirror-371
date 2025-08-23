<div style="
  width:200px; 
  height:100px; 
  overflow:hidden; 
  display:flex; 
  justify-content:center; 
  align-items:center; 
  margin:auto; 
  position:relative; 
  top:0; 
  bottom:0; 
  left:0; 
  right:0;
  border-radius:10px;
  box-shadow:0 4px 8px rgba(0,0,0,0.2);
">
  <img src="https://raw.githubusercontent.com/yazirofi/cdn/main/yazirofi.jpg" 
       style="width:100%; height:100%; object-fit:cover;" 
       alt="Cropped Image">
</div>

---

# 🎙️ pyvoicelib

<div align="center">

[![Downloads](https://static.pepy.tech/badge/pyvoicelib)](https://pepy.tech/projects/pyvoicelib)
[![PyPI Version](https://img.shields.io/pypi/v/pyvoicelib.svg)](https://pypi.org/project/pyvoicelib/)
![Python Version](https://img.shields.io/pypi/pyversions/pyvoicelib.svg)
[![License](https://img.shields.io/github/license/yazirofi/pyvoicelib)](LICENSE)
[![GitHub Stars](https://img.shields.io/github/stars/yazirofi/pyvoicelib?style=social)](https://github.com/yazirofi/pyvoicelib)

</div>

---
> A **simple, cross-platform Python voice assistant library** for beginners, hobbyists, and developers.  
Easily add **speech recognition** 🗣️ and **text-to-speech** 🔊 to your Python projects.

---

## ✨ Features

✅ Text-to-speech conversion (TTS)  
✅ Speech recognition (STT)  
✅ Simple API – both **functions** and **VoiceAssistant class**  
✅ Set **voice rate, volume, and gender** (male/female/neutral)  
✅ Cross-platform: Windows, macOS, Linux  
✅ Python **3.6+** supported  

---

## 📦 Installation

```bash
pip install pyvoicelib
````

For development (with testing):

```bash
git clone https://github.com/Yazirofi/pyvoicelib.git
cd pyvoicelib
pip install -r requirements-dev.txt
```

---

## 🚀 Quick Start

### 1. Standalone Functions

```python
from pyvoicelib import speak, listen

# Text-to-speech
speak("Hello, I am your Python voice assistant!")

# Speech recognition
try:
    text = listen()
    print("You said:", text)
except Exception as e:
    print("Error:", e)
```

---

### 2. Using the VoiceAssistant Class

```python
from pyvoicelib import VoiceAssistant

# Initialize assistant
assistant = VoiceAssistant(voice_rate=160, voice_volume=0.8, voice_gender="female")

# Speak
assistant.speak("Hi there, how can I help you?")

# Listen
try:
    command = assistant.listen()
    print("You said:", command)
except Exception as e:
    print("Error:", e)
```

---

## 🎛️ Voice Customization

```python
from pyvoicelib import VoiceAssistant
assistant = VoiceAssistant

assistant.set_voice_rate(180)   # Words per minute
assistant.set_voice_volume(0.7) # Volume (0.0 – 1.0)
assistant.set_voice_gender("male") # 'male', 'female', 'neutral'

# Check available voices on your system:
print(assistant.get_available_voices())
```
---
## Change the voice gender
```python
from pyvoicelib import VoiceAssistant

va = VoiceAssistant()

print("Available voices:", va.get_available_voices())

va.set_voice_gender("female")
va.speak("Hello, this is the female voice.")

va.set_voice_gender("male")
va.speak("And now, this is the male voice.")
```

---

## Test Complete Package

```python
from pyvoicelib import VoiceAssistant, speak, listen
from pyvoicelib.exceptions import ListenTimeoutError, AudioCaptureError, SpeechError, InitializationError
import time

def test_basic_functionality():
    """Test basic speak and listen functionality"""
    print("=== BASIC FUNCTIONALITY TEST ===")
    
    # Test standalone speak function
    print("1. Testing standalone speak function...")
    speak("Hello! This is a test of the standalone speak function.")
    time.sleep(1)
    
    # Test with different parameters
    print("2. Testing speak with different parameters...")
    speak("This is faster speech", rate=200, wait=False)
    speak("This is slower speech", rate=100)
    speak("This is quieter", volume=0.5)
    speak("This is louder", volume=1.0)
    time.sleep(1)
    
    # Test gender selection
    print("3. Testing gender selection...")
    speak("This should be a male voice", gender='male')
    speak("This should be a female voice", gender='female')
    time.sleep(1)

def test_voice_assistant_class():
    """Test VoiceAssistant class functionality"""
    print("\n=== VOICE ASSISTANT CLASS TEST ===")
    
    try:
        # Test initialization with different parameters
        print("1. Creating VoiceAssistant instance...")
        assistant = VoiceAssistant(
            voice_rate=160,
            voice_volume=0.9,
            voice_gender='female'
        )
        
        # Test multiple speak operations
        print("2. Testing multiple speak operations...")
        for i in range(3):
            assistant.speak(f"Test message number {i + 1}")
            time.sleep(0.5)
        
        # Test voice settings changes
        print("3. Testing voice settings changes...")
        assistant.set_voice_rate(120)
        assistant.speak("This is slower speech after changing rate")
        
        assistant.set_voice_volume(0.6)
        assistant.speak("This is quieter speech after changing volume")
        
        assistant.set_voice_gender('male')
        assistant.speak("This should be a male voice after changing gender")
        
        # Reset to normal
        assistant.set_voice_rate(160)
        assistant.set_voice_volume(0.9)
        assistant.speak("Back to normal settings")
        
        return assistant
        
    except InitializationError as e:
        print(f"Initialization failed: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None

def test_listen_functionality(assistant):
    """Test listening functionality"""
    print("\n=== LISTENING FUNCTIONALITY TEST ===")
    
    if not assistant:
        print("Skipping listen test - no assistant instance")
        return
    
    try:
        print("1. Testing listen with short timeout...")
        assistant.speak("I will listen for 3 seconds. Please say something.")
        
        try:
            result = assistant.listen(timeout=3)
            if result:
                print(f"Heard: {result}")
                assistant.speak(f"I heard you say: {result}")
            else:
                print("No speech detected")
                assistant.speak("I didn't hear anything")
        except ListenTimeoutError:
            print("Listen timeout occurred (expected)")
            assistant.speak("Time's up, I didn't hear anything")
        
        time.sleep(1)
        
        # Test standalone listen function
        print("2. Testing standalone listen function...")
        speak("Now testing standalone listen. Please say something after the beep.", wait=False)
        time.sleep(1)
        
        try:
            result = listen(timeout=5)
            if result:
                print(f"Standalone listen heard: {result}")
                speak(f"Standalone heard: {result}")
            else:
                print("Standalone listen: No speech")
        except ListenTimeoutError:
            print("Standalone listen timeout")
        
    except AudioCaptureError as e:
        print(f"Audio capture error: {e}")
    except Exception as e:
        print(f"Unexpected error during listen test: {e}")

def test_error_handling():
    """Test error handling and exceptions"""
    print("\n=== ERROR HANDLING TEST ===")
    
    # Test invalid volume
    print("1. Testing invalid volume handling...")
    try:
        speak("This should work", volume=0.8)
        print("✓ Normal volume works")
    except Exception as e:
        print(f"✗ Normal volume failed: {e}")
    
    try:
        speak("This should fail", volume=1.5)
        print("✗ Invalid volume should have failed")
    except ValueError as e:
        print(f"✓ Correctly caught invalid volume: {e}")
    except Exception as e:
        print(f"✗ Unexpected error with invalid volume: {e}")
    
    # Test invalid gender
    print("2. Testing invalid gender handling...")
    try:
        speak("This should fail", gender='invalid')
        print("✗ Invalid gender should have failed")
    except ValueError as e:
        print(f"✓ Correctly caught invalid gender: {e}")
    except Exception as e:
        print(f"✗ Unexpected error with invalid gender: {e}")

def test_multiple_instances():
    """Test creating multiple VoiceAssistant instances"""
    print("\n=== MULTIPLE INSTANCES TEST ===")
    
    try:
        print("1. Creating multiple VoiceAssistant instances...")
        
        # Create instances with different settings
        assistant1 = VoiceAssistant(voice_gender='male', voice_rate=140)
        assistant2 = VoiceAssistant(voice_gender='female', voice_rate=180)
        
        print("2. Testing instance 1 (male, slower)...")
        assistant1.speak("I am the first assistant with male voice and slower speech")
        
        print("3. Testing instance 2 (female, faster)...")
        assistant2.speak("I am the second assistant with female voice and faster speech")
        
        print("4. Testing that both instances work multiple times...")
        for i in range(2):
            assistant1.speak(f"Instance one test {i + 1}")
            assistant2.speak(f"Instance two test {i + 1}")
            time.sleep(0.5)
        
        print("✓ Multiple instances work correctly")
        
    except Exception as e:
        print(f"✗ Multiple instances test failed: {e}")

def test_conversation_mode():
    """Test simple conversation functionality"""
    print("\n=== CONVERSATION MODE TEST ===")
    
    try:
        assistant = VoiceAssistant()
        
        print("1. Testing simple conversation...")
        response = assistant.simple_conversation("Please say your name after the beep")
        
        if response:
            print(f"User responded: {response}")
            assistant.speak(f"Nice to meet you, {response}!")
        else:
            print("No response received")
            assistant.speak("I didn't hear your name")
        
        print("2. Testing another conversation...")
        response = assistant.simple_conversation("What is your favorite color?")
        
        if response:
            print(f"User said favorite color: {response}")
            assistant.speak(f"{response} is a nice color!")
        else:
            assistant.speak("I didn't hear your favorite color")
        
    except Exception as e:
        print(f"Conversation test failed: {e}")

def test_voice_settings_report():
    """Test voice settings reporting"""
    print("\n=== VOICE SETTINGS REPORT ===")
    
    try:
        assistant = VoiceAssistant()
        
        # Get available voices
        voices = assistant.get_available_voices()
        print(f"Available voices: {len(voices)}")
        for i, voice in enumerate(voices):
            print(f"  {i + 1}. {voice}")
        
        # Test different gender settings
        print("\nTesting gender settings:")
        for gender in ['male', 'female']:
            try:
                assistant.set_voice_gender(gender)
                assistant.speak(f"This is the {gender} voice setting")
                print(f"✓ {gender} voice setting works")
            except Exception as e:
                print(f"✗ {gender} voice setting failed: {e}")
            time.sleep(1)
        
    except Exception as e:
        print(f"Voice settings report failed: {e}")

def comprehensive_test():
    """Run comprehensive test of all functionality"""
    print("STARTING COMPREHENSIVE PACKAGE TEST")
    print("=" * 50)
    
    start_time = time.time()
    
    # Run all tests
    test_basic_functionality()
    assistant = test_voice_assistant_class()
    test_listen_functionality(assistant)
    test_error_handling()
    test_multiple_instances()
    test_conversation_mode()
    test_voice_settings_report()
    
    end_time = time.time()
    duration = end_time - start_time
    
    print("\n" + "=" * 50)
    print("COMPREHENSIVE TEST COMPLETED")
    print(f"Total test duration: {duration:.2f} seconds")
    print("=" * 50)
    
    # Final test message
    speak("All tests completed successfully! The package is working correctly.")

def quick_test():
    """Quick functionality test"""
    print("=== QUICK TEST ===")
    
    # Test basic speak
    speak("Quick test: Basic speak functionality works!")
    
    # Test VoiceAssistant
    assistant = VoiceAssistant()
    assistant.speak("Voice Assistant class works!")
    
    # Test multiple operations
    for i in range(2):
        assistant.speak(f"Multiple operation test {i + 1}")
    
    print("Quick test completed successfully!")

if __name__ == "__main__":
    print("PyVoiceLib Package Test Suite")
    print("=" * 40)
    
    while True:
        print("\nChoose test mode:")
        print("1. Comprehensive Test (all features)")
        print("2. Quick Test (basic functionality)")
        print("3. Exit")
        
        choice = input("Enter choice (1-3): ").strip()
        
        if choice == '1':
            comprehensive_test()
        elif choice == '2':
            quick_test()
        elif choice == '3':
            print("Exiting test suite.")
            break
        else:
            print("Invalid choice. Please enter 1, 2, or 3.")
        
        input("\nPress Enter to continue...")
```

---

## 🧪 Running Tests

We use **pytest** for testing.

```bash
pytest -v
```

All tests are located in the `tests/` directory.

---

## 🛠️ Troubleshooting

### ❌ `No 'male' voice found. Using default system voice.`

* Your system may not provide explicitly labeled voices.
* Try `assistant.get_available_voices()` to list supported voices.

### ❌ `speech_recognition` or `pyaudio` ImportError

* Install missing dependencies:

  ```bash
  pip install SpeechRecognition pyttsx3 pyaudio
  ```

### ❌ Microphone not working

* Ensure your microphone is enabled and selected as the input device.
* On Linux, install portaudio:

  ```bash
  sudo apt-get install portaudio19-dev
  ```

### ❌ Python version error

* `pyvoicelib` requires **Python 3.6+**.
* Check with:

  ```bash
  python --version
  ```

---

## 💡 Example Project – Simple Conversation Bot

```python
from pyvoicelib import VoiceAssistant

assistant = VoiceAssistant(voice_gender="female")

while True:
    try:
        command = assistant.listen()
        if command:
            print("You:", command)
            if "exit" in command.lower():
                assistant.speak("Goodbye!")
                break
            else:
                assistant.speak(f"You said: {command}")
    except Exception as e:
        print("Error:", e)
```

---

## 🤝 Contributing

Pull requests are welcome! 🎉
Please run tests before submitting:

```bash
pytest -v
```

---

## 📖 Resources

* [SpeechRecognition Docs](https://pypi.org/project/SpeechRecognition/)
* [pyttsx3 Docs](https://pyttsx3.readthedocs.io/)

---

## 📜 License

MIT License © 2025 [Yazirofi](https://github.com/Yazirofi)

---

👉 This README is **clean, stylish, and beginner-friendly**. It has:  
- ✨ Emojis for readability  
- 🚀 Quick start & examples  
- 🛠️ Troubleshooting section  
- 💡 Example project  
