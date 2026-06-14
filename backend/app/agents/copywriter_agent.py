import logging
import json
from datetime import datetime, timezone
from app.agents.llm_client import call_llm
from app.agents.state import AgentStep

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """
You are Xeno Oracle's Copywriter Agent. You write direct-response marketing messages
that feel human, not automated. You match each persona's voice exactly.

Constraints:
1. Never use: 'You've been selected', 'Exclusive offer for you', 'Don't miss out'
2. Always include {{first_name}} personalisation token
3. SMS: ≤160 characters. Email subject: ≤60 chars, body: ≤150 words
4. Match the persona's communication_style exactly
5. Include ONE specific personalisation beyond first name
6. CTA must be action-first: 'Shop now', 'Claim your offer'
7. Output ONLY valid JSON
"""


async def run(campaign_id: str, intent: str, personas: list[dict], strategy: dict) -> tuple[list[dict], AgentStep]:
    """Generate persona-specific, brand-voice-consistent message variants."""
    started_at = datetime.now(timezone.utc).isoformat()
    
    all_copies = []
    
    for persona in personas:
        persona_channel = strategy.get("persona_channel_map", {}).get(persona["name"])
        channels_to_write = [persona_channel] if persona_channel else ["email", "sms"]
        
        for channel in channels_to_write:
            char_limit = "≤160 characters total" if channel == "sms" else "subject ≤60 chars, body ≤150 words"
            
            prompt = f"""
Campaign goal: "{intent}"

Persona: {persona['name']}
Traits: {', '.join(persona.get('traits', []))}
Tone: {persona.get('message_tone', 'warm')}
Communication style: {persona.get('communication_style', 'casual')}
Price sensitive: {persona.get('price_sensitive', False)}
Urgency responsive: {persona.get('urgency_responsive', False)}
Key motivation: {persona.get('key_motivation', 'quality products')}

Channel: {channel.upper()}
Length constraint: {char_limit}

Available personalisation tokens: {{{{first_name}}}}, {{{{last_purchase_category}}}}, {{{{days_since_last_order}}}}, {{{{city}}}}

Write 2 message variants. Output JSON:
{{
  "copies": [
    {{
      "variant": 1,
      "subject": "<email subject or null for SMS>",
      "body": "<message body>",
      "cta": "<call to action text>",
      "tokens_used": ["{{{{first_name}}}}"],
      "why_it_works": "<1 sentence explanation>"
    }},
    {{
      "variant": 2,
      ...
    }}
  ]
}}
"""
            
            result = await call_llm(prompt, SYSTEM_PROMPT, temperature=0.8)
            raw_copies = result.get("copies", [])
            
            for copy in raw_copies:
                all_copies.append({
                    "persona_name": persona["name"],
                    "channel": channel,
                    "variant": copy.get("variant", 1),
                    "subject": copy.get("subject"),
                    "body": copy.get("body", ""),
                    "cta": copy.get("cta", "Shop now"),
                    "personalisation_tokens": copy.get("tokens_used", ["{first_name}"]),
                    "why_it_works": copy.get("why_it_works", "")
                })
    
    step = AgentStep(
        agent_id="copywriter_agent",
        agent_name="Copywriter Agent",
        status="completed",
        input_summary=f"{len(personas)} personas, strategy: {strategy.get('campaign_structure', 'single_blast')}",
        output_summary=f"Generated {len(all_copies)} message variants across {len(personas)} personas",
        reasoning=f"Created channel-specific copy for each persona matching their communication style and motivation",
        confidence=0.82,
        started_at=started_at,
        completed_at=datetime.now(timezone.utc).isoformat()
    )
    
    return all_copies, step
