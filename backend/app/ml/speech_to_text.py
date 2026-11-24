"""
SPEECH TO TEXT MODULE
=====================
Purpose: Convert audio (voice complaints) into text
Why: Voice is just another INPUT method - we convert it to text first,
     then process it like any other text complaint.

IMPORTANT: This is NOT a separate ML pipeline!
           Voice → Text → Same ML Pipeline as text complaints

We use Whisper (OpenAI's open-source model) which can run locally.
"""

import os
import threading
from typing import Optional
import tempfile

try:
    from faster_whisper import WhisperModel as FasterWhisperModel
    FASTER_WHISPER_AVAILABLE = True
except ImportError:
    FASTER_WHISPER_AVAILABLE = False

# Option 1: Local Whisper (FREE - No API key needed)
# Uncomment this if you want to run Whisper locally
try:
    import whisper
    WHISPER_LOCAL_AVAILABLE = True
except ImportError:
    WHISPER_LOCAL_AVAILABLE = False
    print("⚠️ Local Whisper not installed. Install with: pip install openai-whisper")

# Option 2: OpenAI Whisper API (OPTIONAL - Requires API key)
# Only use this if you want cloud-based processing
try:
    from openai import OpenAI
    OPENAI_API_AVAILABLE = True
except ImportError:
    OPENAI_API_AVAILABLE = False


class SpeechToText:
    """
    Converts audio files to text using Whisper.
    
    Why Whisper?
    - Supports Hindi and English (and many other languages)
    - Can run locally (no internet needed)
    - Free and open-source
    - Good accuracy for Indian accents
    """
    
    def __init__(self, use_api: bool = False, api_key: Optional[str] = None):
        """
        Initialize the speech-to-text converter.
        
        Args:
            use_api: If True, use OpenAI API (requires API key)
                    If False, use local Whisper (default, FREE)
            api_key: OpenAI API key (only needed if use_api=True)
                    Get it from: https://platform.openai.com/api-keys
        """
        self.use_api = use_api
        self.model_name = os.getenv("WHISPER_MODEL", "small").strip() or "small"
        self.use_faster_whisper = os.getenv("USE_FASTER_WHISPER", "true").strip().lower() in {
            "1", "true", "yes", "on"
        }
        self.decode_preset = os.getenv("WHISPER_DECODE_PRESET", "balanced").strip().lower() or "balanced"
        # Prompt helps preserve frequent domain words in transcriptions.
        self.initial_prompt = (
            "Campus complaint from a student. Common words: hostel, warden, mess, wifi, "
            "library, classroom, administration, harassment, maintenance."
        )
        
        if use_api:
            if not OPENAI_API_AVAILABLE:
                raise ImportError("OpenAI package not installed. Run: pip install openai")
            if not api_key:
                raise ValueError("API key required for OpenAI Whisper API")
            self.client = OpenAI(api_key=api_key)
            print("✅ Using OpenAI Whisper API (cloud-based)")
        else:
            faster_whisper_selected = self.use_faster_whisper and FASTER_WHISPER_AVAILABLE
            if not WHISPER_LOCAL_AVAILABLE and not faster_whisper_selected:
                raise ImportError(
                    "No local speech engine is installed. Install faster-whisper or openai-whisper.\n"
                    "Or set use_api=True to use OpenAI API"
                )

            self.model = None
            self.faster_model = None
            self._model_load_lock = threading.Lock()

            # Load the large speech model only when a voice complaint arrives.
            # This keeps ordinary API startup and health checks lightweight.

    def _ensure_local_model(self) -> None:
        if self.faster_model is not None or self.model is not None:
            return
        with self._model_load_lock:
            if self.faster_model is not None or self.model is not None:
                return
            if self.use_faster_whisper and FASTER_WHISPER_AVAILABLE:
                self.faster_model = FasterWhisperModel(
                    self.model_name,
                    device="cpu",
                    compute_type="int8",
                )
                print(f"✅ Using Faster-Whisper model: {self.model_name} (cpu/int8)")
            else:
                self.model = whisper.load_model(self.model_name)
                print(f"✅ Using Local Whisper model: {self.model_name} (free, no API key needed)")
    
    def transcribe(self, audio_file_path: str, language: Optional[str] = None) -> dict:
        """
        Convert audio file to text.
        
        Args:
            audio_file_path: Path to audio file (mp3, wav, m4a, etc.)
            language: Optional language hint ('en' for English, 'hi' for Hindi)
                     If None, Whisper will auto-detect
        
        Returns:
            dict with:
                - text: Transcribed text
                - language: Detected language
                - confidence: How confident the model is (if available)
        
        Example:
            >>> stt = SpeechToText()
            >>> result = stt.transcribe("complaint.mp3")
            >>> print(result['text'])
            "Hostel mein hot water nahi aa raha hai"
        """
        
        normalized_language = self._normalize_language_hint(language)

        if self.use_api:
            return self._transcribe_api(audio_file_path, normalized_language)
        else:
            return self._transcribe_local(audio_file_path, normalized_language)

    def _normalize_language_hint(self, language: Optional[str]) -> Optional[str]:
        if language is None:
            return None

        normalized = language.strip().lower()
        if not normalized:
            return None

        alias_map = {
            "en": "en",
            "english": "en",
            "hi": "hi",
            "hindi": "hi",
            # Hinglish is mixed language, so auto-detection usually works better.
            "hinglish": None,
            "auto": None,
        }
        return alias_map.get(normalized)
    
    def _transcribe_local(self, audio_file_path: str, language: Optional[str]) -> dict:
        """
        Transcribe using local Whisper model.
        This runs on your computer - no internet needed!
        """
        preset = self.decode_preset if self.decode_preset in {"fast", "balanced", "accurate"} else "balanced"
        self._ensure_local_model()

        if self.faster_model is not None:
            beam_size = {"fast": 2, "balanced": 4, "accurate": 6}[preset]
            vad_filter = preset != "accurate"
            segments, info = self.faster_model.transcribe(
                audio_file_path,
                language=language,
                task="transcribe",
                beam_size=beam_size,
                condition_on_previous_text=True,
                vad_filter=vad_filter,
                initial_prompt=self.initial_prompt,
            )
            text = " ".join(segment.text.strip() for segment in segments).strip()

            return {
                "text": text,
                "language": getattr(info, "language", "unknown") or "unknown",
                "confidence": None,
                "method": "faster-whisper",
            }

        # Fallback path: openai-whisper
        best_of = {"fast": 2, "balanced": 3, "accurate": 5}[preset]
        beam_size = {"fast": 2, "balanced": 3, "accurate": 5}[preset]
        result = self.model.transcribe(
            audio_file_path,
            language=language,
            task="transcribe",
            fp16=False,
            temperature=0,
            best_of=best_of,
            beam_size=beam_size,
            condition_on_previous_text=True,
            initial_prompt=self.initial_prompt,
        )
        
        return {
            "text": result["text"].strip(),
            "language": result.get("language", "unknown"),
            "confidence": None,  # Local Whisper doesn't provide confidence
            "method": "local"
        }
    
    def _transcribe_api(self, audio_file_path: str, language: Optional[str]) -> dict:
        """
        Transcribe using OpenAI Whisper API.
        This requires internet and API key.
        """
        with open(audio_file_path, "rb") as audio_file:
            # Call OpenAI API
            transcript = self.client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                language=language  # 'en' or 'hi' or None for auto-detect
            )
        
        return {
            "text": transcript.text.strip(),
            "language": language or "auto-detected",
            "confidence": None,  # API doesn't provide confidence
            "method": "api"
        }
    
    def transcribe_from_bytes(
        self,
        audio_bytes: bytes,
        filename: str = "audio.mp3",
        language: Optional[str] = None,
    ) -> dict:
        """
        Transcribe audio from bytes (useful for uploaded files).
        
        Args:
            audio_bytes: Audio file content as bytes
            filename: Original filename (for format detection)
        
        Returns:
            Same as transcribe()
        """
        # Save bytes to temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(filename)[1]) as tmp_file:
            tmp_file.write(audio_bytes)
            tmp_path = tmp_file.name
        
        try:
            # Transcribe the temporary file
            result = self.transcribe(tmp_path, language=language)
            return result
        finally:
            # Clean up temporary file
            if os.path.exists(tmp_path):
                os.remove(tmp_path)


# Example usage for testing
if __name__ == "__main__":
    """
    HOW TO TEST THIS MODULE:
    
    1. For local Whisper (FREE):
       pip install openai-whisper
       
    2. Record a voice complaint or use a sample audio file
    
    3. Run this file:
       python speech_to_text.py
    """
    
    # Initialize (local by default)
    stt = SpeechToText(use_api=False)
    
    # Test with an audio file
    # result = stt.transcribe("test_audio.mp3")
    # print(f"Transcribed: {result['text']}")
    # print(f"Language: {result['language']}")
    
    print("\n📝 Speech-to-Text module ready!")
    print("   - Supports Hindi, English, and Hinglish")
    print("   - Can run locally (no API key needed)")
    print("   - Voice complaints will be converted to text first")
