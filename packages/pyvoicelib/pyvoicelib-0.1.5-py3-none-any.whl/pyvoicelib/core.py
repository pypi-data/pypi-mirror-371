import warnings
import speech_recognition as sr
import pyttsx3
from typing import Optional
from .constants import *
from .exceptions import *
from .utils import initialize_components

# Global recognizer (can be reused)
_recognizer = None


def _get_recognizer():
    """Lazy initialization of global recognizer"""
    global _recognizer
    if _recognizer is None:
        _recognizer = initialize_components()
    return _recognizer


def _create_engine(rate: int = None, volume: float = None, gender: str = None):
    """
    Create a new pyttsx3 engine with specified settings.

    Args:
        rate: Words per minute
        volume: Volume level (0.0 to 1.0)
        gender: Voice gender preference ('male' or 'female')

    Returns:
        Initialized pyttsx3 engine
    """
    try:
        engine = pyttsx3.init()

        if rate is not None:
            engine.setProperty('rate', rate)
        if volume is not None:
            if 0 <= volume <= 1:
                engine.setProperty('volume', volume)
            else:
                raise ValueError("Volume must be between 0.0 and 1.0")

        # Set voice gender if specified
        if gender is not None:
            _set_engine_voice_gender(engine, gender)

        return engine
    except Exception as e:
        raise SpeechError(f"Failed to create speech engine: {str(e)}")


def _set_engine_voice_gender(engine, gender: str):
    """
    Set voice gender for an engine.

    Args:
        engine: pyttsx3 engine instance
        gender: Voice gender preference ('male' or 'female')

    Raises:
        ValueError: If gender is not supported
    """
    if gender not in ['male', 'female']:
        raise ValueError("Gender must be either 'male' or 'female'")

    voices = engine.getProperty("voices")
    if not voices:
        raise SpeechError("No voices available on this system")

    # Get available voices for the specified gender
    gender_voices = []
    for voice in voices:
        voice_name = voice.name.lower()
        voice_id = voice.id.lower()

        # Check for gender indicators in voice name or ID
        if gender == 'female' and any(keyword in voice_name or keyword in voice_id
                                      for keyword in ['female', 'woman', 'zira', 'eva', 'karen', 'laura']):
            gender_voices.append(voice)
        elif gender == 'male' and any(keyword in voice_name or keyword in voice_id
                                      for keyword in ['male', 'man', 'david', 'mark', 'thomas', 'james']):
            gender_voices.append(voice)

    # If we found voices for the requested gender, use the first one
    if gender_voices:
        engine.setProperty("voice", gender_voices[0].id)
        return

    # Fallback: try to find any voice that might match by name pattern
    for voice in voices:
        voice_name = voice.name.lower()
        if gender in voice_name:
            engine.setProperty("voice", voice.id)
            warnings.warn(f"Using voice with '{gender}' in name: {voice.name}")
            return

    # Last resort: use the first available voice
    if voices:
        engine.setProperty("voice", voices[0].id)
        warnings.warn(f"No specific '{gender}' voice found. Using default system voice: {voices[0].name}")
    else:
        raise SpeechError("No voices available on this system")


def speak(text: str, wait: bool = True, rate: int = None, volume: float = None, gender: str = None):
    """
    Convert text to speech and speak it out loud (standalone function).

    Args:
        text: Text to speak
        wait: Whether to wait for speech to complete
        rate: Optional speech rate (words per minute)
        volume: Optional volume level (0.0 to 1.0)
        gender: Optional voice gender preference ('male' or 'female')
    """
    try:
        # Create a new engine for each speak operation
        engine = _create_engine(rate=rate, volume=volume, gender=gender)

        engine.say(text)
        if wait:
            engine.runAndWait()
    except Exception as e:
        raise SpeechError(f"Text-to-speech error: {str(e)}")


def listen(
        timeout: int = DEFAULT_TIMEOUT,
        phrase_time_limit: int = DEFAULT_PHRASE_TIME_LIMIT
) -> Optional[str]:
    """
    Listen for user speech and return recognized text (standalone function).

    Args:
        timeout: Timeout in seconds for listening
        phrase_time_limit: Maximum time for a phrase

    Returns:
        Recognized text or None if no speech detected
    """
    try:
        recognizer = _get_recognizer()

        with sr.Microphone() as source:
            print("Listening...")  # Can be made configurable later
            audio = recognizer.listen(
                source,
                timeout=timeout,
                phrase_time_limit=phrase_time_limit
            )
            return recognizer.recognize_google(audio)
    except sr.WaitTimeoutError:
        raise ListenTimeoutError("No speech detected within timeout period")
    except sr.UnknownValueError:
        return None
    except Exception as e:
        raise AudioCaptureError(f"Error capturing audio: {str(e)}")


class VoiceAssistant:
    def __init__(self,
                 voice_rate: int = DEFAULT_VOICE_RATE,
                 voice_volume: float = DEFAULT_VOICE_VOLUME,
                 voice_gender: str = 'female'):
        """
        Initialize the voice assistant.

        Args:
            voice_rate: Words per minute
            voice_volume: Volume level (0.0 to 1.0)
            voice_gender: Voice gender ('male' or 'female')
        """
        try:
            self.recognizer = _get_recognizer()
            self.voice_rate = voice_rate
            self.voice_volume = voice_volume
            self.set_voice_gender(voice_gender)  # Use setter for validation
        except Exception as e:
            raise InitializationError(str(e))

    def _create_engine(self):
        """Create a new engine with current settings"""
        return _create_engine(
            rate=self.voice_rate,
            volume=self.voice_volume,
            gender=self.voice_gender
        )

    def set_voice_gender(self, gender: str):
        """
        Set the voice gender.

        Args:
            gender: 'male' or 'female'

        Raises:
            ValueError: If gender is not supported
        """
        if gender not in ['male', 'female']:
            raise ValueError("Gender must be either 'male' or 'female'")
        self.voice_gender = gender

    def get_available_voices(self):
        """Return list of available voice names"""
        # Create temporary engine to get voices
        engine = self._create_engine()
        return [v.name for v in engine.getProperty("voices")]

    def get_available_voices_by_gender(self, gender: str = None):
        """Return list of available voice names filtered by gender"""
        if gender and gender not in ['male', 'female']:
            raise ValueError("Gender must be either 'male' or 'female'")

        engine = self._create_engine()
        voices = engine.getProperty("voices")

        if gender:
            filtered_voices = []
            for voice in voices:
                voice_name = voice.name.lower()
                if gender == 'female' and any(keyword in voice_name for keyword in ['female', 'woman', 'zira']):
                    filtered_voices.append(voice.name)
                elif gender == 'male' and any(keyword in voice_name for keyword in ['male', 'man', 'david']):
                    filtered_voices.append(voice.name)
            return filtered_voices

        return [v.name for v in voices]

    def set_voice_rate(self, rate: int):
        """Set speech rate in words per minute"""
        self.voice_rate = rate

    def set_voice_volume(self, volume: float):
        """Set volume level (0.0 to 1.0)"""
        if 0 <= volume <= 1:
            self.voice_volume = volume
        else:
            raise ValueError("Volume must be between 0.0 and 1.0")

    def speak(self, text: str, wait: bool = True):
        """Convert text to speech and speak it out loud."""
        try:
            engine = self._create_engine()
            engine.say(text)
            if wait:
                engine.runAndWait()
        except Exception as e:
            raise SpeechError(f"Text-to-speech error: {str(e)}")

    def listen(self,
               timeout: int = DEFAULT_TIMEOUT,
               phrase_time_limit: int = DEFAULT_PHRASE_TIME_LIMIT) -> Optional[str]:
        """Listen for user speech and return the recognized text."""
        try:
            with sr.Microphone() as source:
                print("Listening...")
                audio = self.recognizer.listen(
                    source,
                    timeout=timeout,
                    phrase_time_limit=phrase_time_limit
                )
                return self.recognizer.recognize_google(audio)
        except sr.WaitTimeoutError:
            raise ListenTimeoutError("No speech detected within timeout period")
        except sr.UnknownValueError:
            return None
        except Exception as e:
            raise AudioCaptureError(f"Error capturing audio: {str(e)}")

    def simple_conversation(self, prompt: str):
        """A simple conversation helper that speaks and then listens."""
        self.speak(prompt)
        return self.listen()