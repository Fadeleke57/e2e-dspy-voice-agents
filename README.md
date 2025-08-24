# DSPy Customer Support Voice Agent

A comprehensive customer support voice agent built with the DSPy framework, featuring intelligent intent classification, sentiment analysis, and multi-modal interaction capabilities.

## Features

- 🎯 **Intent Classification**: Automatically categorizes customer queries (billing, technical, refund, etc.)
- 😊 **Sentiment Analysis**: Detects customer emotions and adjusts responses accordingly
- 🤖 **Smart Escalation**: Intelligently decides when to escalate to human agents
- 🎙️ **Voice Interface**: Supports both text and voice-based interactions
- 📊 **Conversation Tracking**: Maintains context across multi-turn conversations
- ⚙️ **Configurable**: Flexible configuration for different deployment scenarios

## Architecture

The agent is built using DSPy's signature-based approach with the following components:

### Core DSPy Modules (`voice_agent.py`)
- `IntentClassifier`: Categorizes customer queries
- `SentimentAnalyzer`: Analyzes emotional tone
- `EntityExtractor`: Extracts relevant information (order IDs, emails, etc.)
- `ResponseGenerator`: Creates appropriate responses
- `EscalationDecider`: Determines when human intervention is needed

### Voice Processing (`voice_processor.py`)
- `VoiceProcessor`: Handles audio input/output
- `VoiceAgentInterface`: Combines voice processing with the support agent
- Mock services for testing without external dependencies

### Configuration (`config.py`)
- Centralized configuration management
- Environment variable support
- Customizable thresholds and settings

## Quick Start

1. **Install dependencies**:
   ```bash
   pip install -e .
   
   # For voice capabilities (optional)
   pip install -e .[voice]
   ```

2. **Configure environment**:
   ```bash
   cp .env.example .env
   # Edit .env and add your OPENAI_API_KEY
   ```

3. **Run the agent**:
   ```bash
   python main.py
   ```

## Usage Examples

### Text-based Interaction
```python
from voice_agent import CustomerSupportAgent

agent = CustomerSupportAgent()
response = await agent.process_query("I need help with my billing")

print(response.response)  # Agent's response
print(response.escalate)  # Whether to escalate
print(response.suggested_actions)  # Recommended actions
```

### Voice-based Interaction
```python
from voice_processor import VoiceAgentInterface
from voice_agent import CustomerSupportAgent

agent = CustomerSupportAgent()
voice_interface = VoiceAgentInterface(agent)
await voice_interface.start_session()
```

## Configuration

Create a `.env` file based on `.env.example`:

```env
OPENAI_API_KEY=your_key_here
MODEL_TEMPERATURE=0.7
ESCALATION_THRESHOLD=0.3
MAX_CONVERSATION_TURNS=10
```

## Supported Intents

- **billing**: Payment issues, charges, invoices
- **technical**: App problems, bugs, performance issues  
- **refund**: Refund requests and processing
- **account**: Login issues, profile management
- **shipping**: Order status, delivery problems
- **product**: Product questions and information
- **cancellation**: Service cancellation requests
- **general**: General inquiries

## Escalation Triggers

The agent automatically escalates conversations when:

- Intent classification confidence is below threshold
- Customer uses escalation keywords ("manager", "complaint", etc.)
- Urgent situations are detected
- Customer sentiment is extremely negative
- Complex issues requiring human expertise

## Development

### Running Tests
```bash
pytest tests/
```

### Adding New Intents
1. Update `supported_intents` in `config.py`
2. Add examples to the knowledge base
3. Update the `IntentClassifier` signature if needed

### Extending Voice Capabilities
The current implementation uses mock voice services. To integrate real services:

1. Implement actual transcription in `MockTranscriptionService`
2. Implement actual TTS in `MockSynthesisService`
3. Add audio I/O handling in `VoiceProcessor`

## API Integration

Uses OpenAI GPT-4o-mini by default. To use other providers:

```python
# Example: Using different models
agent = CustomerSupportAgent(lm_model="openai/gpt-4")
```

## License

MIT License