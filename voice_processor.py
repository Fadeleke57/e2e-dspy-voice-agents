import asyncio
import json
from typing import Optional, Callable, Dict, Any
from dataclasses import dataclass
import wave
import threading
from queue import Queue


@dataclass
class VoiceConfig:
    sample_rate: int = 16000
    chunk_size: int = 1024
    channels: int = 1
    format: str = "wav"
    silence_threshold: int = 500
    silence_duration: float = 2.0


class VoiceProcessor:
    """Handles voice input/output processing for the customer support agent."""
    
    def __init__(self, config: VoiceConfig = None):
        self.config = config or VoiceConfig()
        self.is_recording = False
        self.audio_queue = Queue()
        self.transcription_callback: Optional[Callable] = None
        self.synthesis_callback: Optional[Callable] = None
        
    def set_transcription_callback(self, callback: Callable[[bytes], str]):
        """Set the speech-to-text callback function."""
        self.transcription_callback = callback
    
    def set_synthesis_callback(self, callback: Callable[[str], bytes]):
        """Set the text-to-speech callback function."""
        self.synthesis_callback = callback
    
    async def start_listening(self) -> None:
        """Start continuous voice input processing."""
        self.is_recording = True
        
        # this would interface with microphone
        print("🎤 Voice input started. Listening for customer queries...")
        
        while self.is_recording:
            # simulate audio chunk processing
            await asyncio.sleep(0.1)
            
            # in real implementation:
            # 1. capture audio from microphone
            # 2. detect voice activity
            # 3. buffer audio until silence detected
            # 4. send to transcription when complete utterance detected
    
    def stop_listening(self) -> None:
        """Stop voice input processing."""
        self.is_recording = False
        print("🔇 Voice input stopped.")
    
    async def process_audio_chunk(self, audio_data: bytes) -> Optional[str]:
        """Process an audio chunk and return transcribed text if available."""
        if self.transcription_callback:
            try:
                transcribed_text = self.transcription_callback(audio_data)
                return transcribed_text
            except Exception as e:
                print(f"Transcription error: {e}")
                return None
        return None
    
    async def synthesize_response(self, text: str) -> Optional[bytes]:
        """Convert text response to audio."""
        if self.synthesis_callback:
            try:
                audio_data = self.synthesis_callback(text)
                return audio_data
            except Exception as e:
                print(f"Synthesis error: {e}")
                return None
        return None
    
    async def play_audio(self, audio_data: bytes) -> None:
        """Play audio response to the user."""
        # this would play audio through speakers
        print(f"🔊 Playing audio response ({len(audio_data)} bytes)")


class MockTranscriptionService:
    """Mock transcription service for testing."""
    
    def __init__(self):
        # simulated customer queries for testing
        self.mock_queries = [
            "Hi, I'm having trouble with my billing account",
            "My order hasn't arrived yet and it's been two weeks",
            "I need help resetting my password",
            "I want to cancel my subscription",
            "The app keeps crashing on my phone",
            "I was charged twice for the same order"
        ]
        self.query_index = 0
    
    def transcribe(self, audio_data: bytes) -> str:
        """Mock transcription that returns predefined queries."""
        if self.query_index < len(self.mock_queries):
            query = self.mock_queries[self.query_index]
            self.query_index += 1
            return query
        return "Thank you for your help"


class MockSynthesisService:
    """Mock text-to-speech service for testing."""
    
    def synthesize(self, text: str) -> bytes:
        """Mock synthesis that returns placeholder audio data."""
        # this would return actual audio bytes
        return f"[AUDIO: {text}]".encode()


class VoiceAgentInterface:
    """Main interface combining voice processing with the support agent."""
    
    def __init__(self, support_agent, voice_config: VoiceConfig = None):
        self.support_agent = support_agent
        self.voice_processor = VoiceProcessor(voice_config)
        self.transcription_service = MockTranscriptionService()
        self.synthesis_service = MockSynthesisService()
        
        # Set up callbacks
        self.voice_processor.set_transcription_callback(self.transcription_service.transcribe)
        self.voice_processor.set_synthesis_callback(self.synthesis_service.synthesize)
        
        self.conversation_history = []
    
    async def start_session(self) -> None:
        """Start a voice-based customer support session."""
        print("🎙️  Customer Support Voice Agent Started")
        print("=" * 50)
        
        await self.voice_processor.start_listening()
        
        # simulate conversation flow
        for i in range(3):  # process a few mock queries
            await self._process_voice_interaction()
            await asyncio.sleep(1)
        
        self.voice_processor.stop_listening()
        print("\n📞 Session ended")
    
    async def _process_voice_interaction(self) -> None:
        """Process a single voice interaction."""
        # simulate audio capture and transcription
        mock_audio = b"mock_audio_data"
        transcribed_text = await self.voice_processor.process_audio_chunk(mock_audio)
        
        if transcribed_text:
            print(f"\n👤 Customer: {transcribed_text}")
            
            # process through support agent
            response = await self.support_agent.process_query(
                transcribed_text, 
                self._get_conversation_context()
            )
            
            print(f"🤖 Agent: {response.response}")
            
            if response.escalate:
                print("⚠️  Escalating to human agent...")
                return
            
            if response.suggested_actions:
                print(f"💡 Suggested actions: {', '.join(response.suggested_actions)}")
            
            # convert response to audio
            audio_response = await self.voice_processor.synthesize_response(response.response)
            if audio_response:
                await self.voice_processor.play_audio(audio_response)
            
            # update conversation history
            self.conversation_history.append({
                "customer": transcribed_text,
                "agent": response.response,
                "escalated": response.escalate
            })
    
    def _get_conversation_context(self) -> str:
        """Get conversation context for better responses."""
        context = ""
        for entry in self.conversation_history[-3:]:  # last 3 exchanges
            context += f"Customer: {entry['customer']}\nAgent: {entry['agent']}\n"
        return context
    
    def get_session_summary(self) -> Dict[str, Any]:
        """Get a summary of the current session."""
        return {
            "total_interactions": len(self.conversation_history),
            "escalated": any(entry["escalated"] for entry in self.conversation_history),
            "conversation": self.conversation_history
        }