import asyncio
import os
from voice_agent import CustomerSupportAgent
from voice_processor import VoiceAgentInterface, VoiceConfig


async def demo_text_interaction():
    """Demo the agent with text-based interactions."""
    print("🤖 Customer Support Agent - Text Demo")
    print("=" * 40)
    
    # support agent
    agent = CustomerSupportAgent()
    
    # test queries
    test_queries = [
        "Hi, I'm having trouble with my billing. I was charged twice.",
        "My order #12345 hasn't arrived yet and it's been two weeks",
        "I can't log into my account. The password reset isn't working",
        "This is ridiculous! Your service is terrible and I want a full refund now!",
        "The mobile app keeps crashing when I try to upload photos"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n--- Query {i} ---")
        print(f"👤 Customer: {query}")
        
        response = await agent.process_query(query)
        
        print(f"🤖 Agent: {response.response}")
        print(f"📊 Confidence: {response.confidence:.2f}")
        print(f"🔄 Escalate: {response.escalate}")
        if response.suggested_actions:
            print(f"💡 Actions: {', '.join(response.suggested_actions)}")


async def demo_voice_interaction():
    """Demo the agent with voice-based interactions."""
    print("\n🎙️  Customer Support Agent - Voice Demo")
    print("=" * 40)
    
    # initialize components
    agent = CustomerSupportAgent()
    voice_config = VoiceConfig(sample_rate=16000, chunk_size=1024)
    voice_interface = VoiceAgentInterface(agent, voice_config)
    
    # start voice session
    await voice_interface.start_session()
    
    # print session summary
    summary = voice_interface.get_session_summary()
    print(f"\n📋 Session Summary:")
    print(f"   Total interactions: {summary['total_interactions']}")
    print(f"   Escalated: {summary['escalated']}")


async def interactive_mode():
    """Interactive mode for testing with custom queries."""
    print("\n💬 Interactive Mode - Enter your queries (type 'quit' to exit)")
    print("=" * 50)
    
    agent = CustomerSupportAgent()
    
    while True:
        try:
            query = input("\n👤 You: ").strip()
            if query.lower() in ['quit', 'exit', 'q']:
                break
            
            if not query:
                continue
                
            response = await agent.process_query(query)
            
            print(f"🤖 Agent: {response.response}")
            
            if response.escalate:
                print("⚠️  This query would be escalated to a human agent.")
            
            if response.suggested_actions:
                print(f"💡 Suggested actions: {', '.join(response.suggested_actions)}")
                
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print("\n👋 Goodbye!")


async def main():
    """Main application entry point."""
    print("🎯 DSPy Customer Support Voice Agent")
    print("====================================")
    
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  Warning: OPENAI_API_KEY not found in environment variables")
        print("   Make sure to set it in your .env file or environment")
    
    # run demos
    await demo_text_interaction()
    await demo_voice_interaction()
    
    # interactive mode
    await interactive_mode()


if __name__ == "__main__":
    asyncio.run(main())