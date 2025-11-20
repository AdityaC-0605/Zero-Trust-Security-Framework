"""Security Assistant - Claude API integration"""
import os

CLAUDE_API_KEY = os.getenv('CLAUDE_API_KEY', '')
CLAUDE_MODEL = os.getenv('CLAUDE_MODEL', 'claude-3-5-sonnet-20241022')

try:
    from anthropic import Anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

class SecurityAssistant:
    def __init__(self):
        self.enabled = os.getenv('SECURITY_ASSISTANT_ENABLED', 'false').lower() == 'true'
        self.client = None
        
        # Initialize client only if available and API key is provided
        if ANTHROPIC_AVAILABLE and CLAUDE_API_KEY:
            try:
                self.client = Anthropic(api_key=CLAUDE_API_KEY)
            except Exception as e:
                print(f"Warning: Failed to initialize Anthropic client: {e}")
                print("Security assistant will be disabled.")
                self.client = None
    
    def generate_response(self, user_query, context=None):
        """Generate response using Claude API"""
        if not self.client:
            return "Security assistant is not available"
        
        system_prompt = """You are a helpful security assistant for a zero-trust security system. 
        Provide clear, concise answers about security policies, access requests, and best practices."""
        
        try:
            message = self.client.messages.create(
                model=CLAUDE_MODEL,
                max_tokens=1024,
                system=system_prompt,
                messages=[{"role": "user", "content": user_query}]
            )
            return message.content[0].text
        except:
            return "Unable to generate response"
    
    def explain_access_denial(self, denial_reason):
        """Explain why access was denied"""
        query = f"Explain in simple terms why this access was denied: {denial_reason}"
        return self.generate_response(query)
    
    def guide_mfa_setup(self):
        """Provide MFA setup guidance"""
        return self.generate_response("Provide step-by-step instructions for setting up multi-factor authentication")

security_assistant = SecurityAssistant()
