import dspy
from typing import List, Dict
from dataclasses import dataclass
import json
import opik
from opik.integrations.dspy.callback import OpikCallback
import os

project_name = "farouk/customer-support-agent" # in modaic this will usually be the string {entityName}/{agentName}
opik.configure(use_local=os.getenv("ENVIRONMENT", "dev") == "dev")
opik_callback = OpikCallback(project_name=project_name)


@dataclass
class CustomerQuery:
    text: str
    sentiment: str
    intent: str
    entities: Dict[str, str]


@dataclass
class SupportResponse:
    response: str
    confidence: float
    escalate: bool
    suggested_actions: List[str]


class IntentClassifier(dspy.Signature):
    """Classify customer support queries into specific intents."""
    
    query: str = dspy.InputField(desc="Customer query text")
    intent: str = dspy.OutputField(desc="Intent category: billing, technical, refund, account, general")
    confidence: float = dspy.OutputField(desc="Confidence score between 0 and 1")


class SentimentAnalyzer(dspy.Signature):
    """Analyze the sentiment of customer messages."""
    
    message: str = dspy.InputField(desc="Customer message")
    sentiment: str = dspy.OutputField(desc="Sentiment: positive, negative, neutral, frustrated, urgent")
    intensity: float = dspy.OutputField(desc="Intensity score between 0 and 1")


class EntityExtractor(dspy.Signature):
    """Extract relevant entities from customer queries."""
    
    query: str = dspy.InputField(desc="Customer query")
    entities: str = dspy.OutputField(desc="JSON string of extracted entities (order_id, product_name, account_email, etc.)")


class ResponseGenerator(dspy.Signature):
    """Generate appropriate customer support responses."""
    
    query: str = dspy.InputField(desc="Original customer query")
    intent: str = dspy.InputField(desc="Classified intent")
    sentiment: str = dspy.InputField(desc="Customer sentiment")
    entities: str = dspy.InputField(desc="Extracted entities")
    context: str = dspy.InputField(desc="Additional context or previous conversation")
    
    response: str = dspy.OutputField(desc="Professional customer support response")
    escalate: bool = dspy.OutputField(desc="Whether to escalate to human agent")
    suggested_actions: str = dspy.OutputField(desc="Comma-separated list of suggested next actions")


class EscalationDecider(dspy.Signature):
    """Decide whether a query should be escalated to human agents."""
    
    query: str = dspy.InputField(desc="Customer query")
    intent: str = dspy.InputField(desc="Query intent")
    sentiment: str = dspy.InputField(desc="Customer sentiment")
    confidence: float = dspy.InputField(desc="Intent classification confidence")
    
    escalate: bool = dspy.OutputField(desc="Whether to escalate to human")
    reason: str = dspy.OutputField(desc="Reason for escalation decision")


class CustomerSupportAgent:
    def __init__(self, lm_model: str = "openai/gpt-4o-mini"):
        self.lm = dspy.LM(lm_model)
        dspy.configure(lm=self.lm)

        dspy.settings.configure(
            callbacks=[opik_callback],
        )
        
        # Initialize DSPy modules
        self.intent_classifier = dspy.ChainOfThought(IntentClassifier)
        self.sentiment_analyzer = dspy.ChainOfThought(SentimentAnalyzer)
        self.entity_extractor = dspy.ChainOfThought(EntityExtractor)
        self.response_generator = dspy.ChainOfThought(ResponseGenerator)
        self.escalation_decider = dspy.ChainOfThought(EscalationDecider)
        
        # Knowledge base for common issues
        self.knowledge_base = {
            "billing": [
                "Check payment method and billing cycle",
                "Review recent charges and invoices",
                "Update payment information if needed"
            ],
            "technical": [
                "Restart the application or device",
                "Check internet connection",
                "Clear cache and cookies",
                "Update to latest version"
            ],
            "refund": [
                "Review refund policy terms",
                "Verify purchase details",
                "Process refund if eligible"
            ],
            "account": [
                "Verify account information",
                "Reset password if needed",
                "Update profile settings"
            ]
        }
    
    async def process_query(self, query_text: str, context: str = "") -> SupportResponse:
        """Process a customer support query through the complete pipeline."""
        
        # classify intent
        intent_result = self.intent_classifier(query=query_text)
        
        # analyze sentiment
        sentiment_result = self.sentiment_analyzer(message=query_text)
        
        # extract entities
        entity_result = self.entity_extractor(query=query_text)
        
        # check if escalation is needed
        escalation_result = self.escalation_decider(
            query=query_text,
            intent=intent_result.intent,
            sentiment=sentiment_result.sentiment,
            confidence=intent_result.confidence
        )
        
        # generate response
        response_result = self.response_generator(
            query=query_text,
            intent=intent_result.intent,
            sentiment=sentiment_result.sentiment,
            entities=entity_result.entities,
            context=context
        )
        
        # parse entities safely
        try:
            entities = json.loads(entity_result.entities)
        except:
            entities = {}
        
        # parse suggested actions
        suggested_actions = [action.strip() for action in response_result.suggested_actions.split(",")]
        
        return SupportResponse(
            response=response_result.response,
            confidence=float(intent_result.confidence),
            escalate=escalation_result.escalate or response_result.escalate,
            suggested_actions=suggested_actions
        )
    
    def get_knowledge_base_suggestions(self, intent: str) -> List[str]:
        """Get relevant suggestions from knowledge base."""
        return self.knowledge_base.get(intent, ["Contact support for assistance"])
    
    async def handle_conversation(self, messages: List[str]) -> List[SupportResponse]:
        """Handle a multi-turn conversation."""
        responses = []
        context = ""
        
        for i, message in enumerate(messages):
            response = await self.process_query(message, context)
            responses.append(response)
            
            # update context for next turn
            context += f"Customer: {message}\nAgent: {response.response}\n"
            
            # stop if escalation is needed
            if response.escalate:
                break
                
        return responses