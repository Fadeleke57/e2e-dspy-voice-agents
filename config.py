import os
from dataclasses import dataclass
from typing import List, Optional
from pathlib import Path


@dataclass
class ModelConfig:
    """Configuration for the language model."""
    model_name: str = "openai/gpt-4o-mini"
    temperature: float = 0.7
    max_tokens: int = 1000
    api_key: Optional[str] = None
    
    def __post_init__(self):
        if self.api_key is None:
            self.api_key = os.getenv("OPENAI_API_KEY")


@dataclass
class VoiceConfig:
    """Configuration for voice processing."""
    sample_rate: int = 16000
    chunk_size: int = 1024
    channels: int = 1
    format: str = "wav"
    silence_threshold: int = 500
    silence_duration: float = 2.0
    
    # Speech-to-text settings
    stt_service: str = "openai"  # openai, google, azure, etc.
    stt_model: str = "whisper-1"
    
    # Text-to-speech settings
    tts_service: str = "openai"  # openai, google, azure, etc.
    tts_voice: str = "alloy"
    tts_speed: float = 1.0


@dataclass
class AgentConfig:
    """Configuration for the customer support agent."""
    escalation_threshold: float = 0.3  # Confidence threshold for escalation
    max_conversation_turns: int = 10
    knowledge_base_path: str = "knowledge_base.json"
    
    # Intent categories
    supported_intents: List[str] = None
    
    # Escalation triggers
    escalation_keywords: List[str] = None
    urgent_keywords: List[str] = None
    
    def __post_init__(self):
        if self.supported_intents is None:
            self.supported_intents = [
                "billing", "technical", "refund", "account", "general", 
                "shipping", "product", "cancellation", "complaint"
            ]
        
        if self.escalation_keywords is None:
            self.escalation_keywords = [
                "manager", "supervisor", "complaint", "legal", "lawsuit",
                "terrible", "awful", "horrible", "unacceptable"
            ]
        
        if self.urgent_keywords is None:
            self.urgent_keywords = [
                "urgent", "emergency", "critical", "asap", "immediately",
                "can't access", "locked out", "security"
            ]


@dataclass
class AppConfig:
    """Main application configuration."""
    model: ModelConfig = None
    voice: VoiceConfig = None
    agent: AgentConfig = None
    
    # Logging
    log_level: str = "INFO"
    log_file: str = "customer_support.log"
    
    # Session settings
    session_timeout: int = 1800  # 30 minutes
    save_conversations: bool = True
    conversations_dir: str = "conversations"
    
    def __post_init__(self):
        if self.model is None:
            self.model = ModelConfig()
        if self.voice is None:
            self.voice = VoiceConfig()
        if self.agent is None:
            self.agent = AgentConfig()


def load_config_from_env() -> AppConfig:
    """Load configuration from environment variables."""
    config = AppConfig()
    
    # Model configuration
    if model_name := os.getenv("MODEL_NAME"):
        config.model.model_name = model_name
    if temperature := os.getenv("MODEL_TEMPERATURE"):
        config.model.temperature = float(temperature)
    if max_tokens := os.getenv("MODEL_MAX_TOKENS"):
        config.model.max_tokens = int(max_tokens)
    
    # Voice configuration
    if stt_service := os.getenv("STT_SERVICE"):
        config.voice.stt_service = stt_service
    if tts_service := os.getenv("TTS_SERVICE"):
        config.voice.tts_service = tts_service
    if tts_voice := os.getenv("TTS_VOICE"):
        config.voice.tts_voice = tts_voice
    
    # Agent configuration
    if escalation_threshold := os.getenv("ESCALATION_THRESHOLD"):
        config.agent.escalation_threshold = float(escalation_threshold)
    if max_turns := os.getenv("MAX_CONVERSATION_TURNS"):
        config.agent.max_conversation_turns = int(max_turns)
    
    # App configuration
    if log_level := os.getenv("LOG_LEVEL"):
        config.log_level = log_level
    if session_timeout := os.getenv("SESSION_TIMEOUT"):
        config.session_timeout = int(session_timeout)
    
    return config


def create_directories(config: AppConfig) -> None:
    """Create necessary directories for the application."""
    directories = [
        config.conversations_dir,
        "logs",
        "data"
    ]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)


# Default configuration instance
default_config = AppConfig()