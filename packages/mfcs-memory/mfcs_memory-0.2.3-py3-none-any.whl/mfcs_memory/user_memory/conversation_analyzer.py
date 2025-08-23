"""
Conversation Analyzer Module - Responsible for analyzing conversation content and user profiles
"""

import json
import logging
from typing import Dict, List, Optional
from openai import AsyncOpenAI

from ..utils.config import Config
from .base import ManagerBase, SessionData, safe_async_call

logger = logging.getLogger(__name__)

class ConversationAnalyzer(ManagerBase):
    def __init__(self, config: Config):
        super().__init__(config)

        # Initialize OpenAI client
        self.openai_client = AsyncOpenAI(
            api_key=self.config.openai_api_key,
            base_url=self.config.openai_api_base
        )
        logger.info("OpenAI connection initialized successfully")

    async def analyze_conversation_updates(self, session: Dict, new_dialog: Dict) -> Dict:
        """Analyze the impact of new conversation"""
        # Safely handle session data using SessionData
        session_data = SessionData.from_dict(session)
        
        # Get session information
        existing_summary = session_data.conversation_summary
        existing_memory = session_data.user_memory_summary
        dialog_history = session_data.dialog_history
        
        # Conservative but reliable context strategy
        def get_context_rounds(total_rounds: int) -> int:
            """
            Determine context based on total conversation rounds
            - Fully preserve few conversations
            - Preserve recent 3 rounds for medium conversations
            - Preserve recent 5 rounds for large conversations
            """
            if total_rounds <= 2:
                return total_rounds  # Fully preserve
            elif total_rounds <= 5:
                return min(3, total_rounds)  # Max 3 rounds
            else:
                return 5  # Max 5 rounds, avoid excessive tokens
        
        # Get appropriate conversation context
        recent_context = ""
        if dialog_history:
            context_rounds = get_context_rounds(len(dialog_history))
            recent_dialogs = dialog_history[-context_rounds:]
            recent_context = "\n".join([
                f"User: {d['user']}\nAssistant: {d['assistant']}" 
                for d in recent_dialogs
            ])
        
        # Build concise analysis prompt
        analysis_prompt = f'''
Analyze user instructions and behavioral changes:

Context: {existing_summary[:200]}...
Memory: {existing_memory[:200]}...
Recent: {recent_context[:300]}...

New Dialog:
User: {new_dialog['user']}
Assistant: {new_dialog['assistant']}

Detect:
1. Identity/role instructions
2. Behavioral change requests
3. New interaction rules

Return JSON:
{{
    "requires_memory_update": true/false,
    "requires_summary_update": true/false,
    "interaction_mode_change": true/false
}}
'''
        
        try:
            response = await self.openai_client.chat.completions.create(
                model=self.config.llm_model,
                messages=[
                    {"role": "system", "content": "You are a user instruction analysis expert. Your job is to identify and SUPPORT user requests for identity/role changes. When users give identity instructions, you should help implement them, not resist them."},
                    {"role": "user", "content": analysis_prompt}
                ],
                temperature=0.1,
                max_tokens=300,
                response_format={"type": "json_object"}
            )
            
            result_text = response.choices[0].message.content.strip()
            
            # Clean possible markdown markers
            if result_text.startswith('```json'):
                result_text = result_text[7:]
            if result_text.endswith('```'):
                result_text = result_text[:-3]
            
            try:
                result = json.loads(result_text.strip())
                
                # If interaction mode changes, force memory update
                if result.get('interaction_mode_change', False):
                    result['requires_memory_update'] = True
                    result['requires_summary_update'] = True
                
                return result
            except json.JSONDecodeError as json_error:
                logger.error(f"JSON parsing failed: {json_error}, raw text: {result_text}")
                raise
            
        except Exception as e:
            logger.error(f"Error analyzing conversation updates: {str(e)}", exc_info=True)
            # Default conservative strategy
            return {
                "requires_memory_update": True,
                "requires_summary_update": True,
                "interaction_mode_change": False
            }

    async def analyze_user_profile(self, dialog_history: List[Dict], n: int = 10) -> str:
        """Analyze user profile"""
        # Safely get history
        dialog_history_copy = dialog_history.copy()
        
        recent_history = dialog_history_copy[-n:]
        history_text = "\n".join([f"User: {d['user']}\nAssistant: {d['assistant']}" for d in recent_history])

        analysis_prompt = f'''
Extract user settings from conversation history. Use imperative language ("You must...", "You are...").

PRIORITY ORDER:
1. Identity & Gender - Highest priority
2. Behavioral Rules
3. Preferences & Styles
4. Other Settings

RULES:
- Use latest instructions if conflicting
- Only extract from actual user input
- No AI identity mentions
- Imperative language only

History:
{history_text}
'''
        try:
            messages = [
                {"role": "system", "content": "You are a professional conversation analysis assistant specializing in identity and role extraction. PRIORITIZE identity, gender, and role settings above all else. Only output imperative settings using clear, direct language like 'Your gender is male' or 'You are a male assistant'. Don't add other explanations."},
                {"role": "user", "content": analysis_prompt}
            ]
            response = await self.openai_client.chat.completions.create(
                model=self.config.llm_model,
                messages=messages,
                temperature=0.1,
                max_tokens=300
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"Error analyzing user profile: {str(e)}", exc_info=True)
            return ""

    async def update_conversation_summary(self, session: Dict, n: int = 5) -> str:
        """Update conversation summary"""
        # Safely handle session data using SessionData
        session_data = SessionData.from_dict(session)
        
        if not session:
            logger.error("Cannot update conversation summary: session does not exist")
            return ""

        summary = session_data.conversation_summary
        dialog_history = session_data.dialog_history

        # Get recent N rounds
        new_dialogs = dialog_history[-n:]
        new_dialogs_text = "\n".join([f"User: {d['user']}\nAssistant: {d['assistant']}" for d in new_dialogs])

        # Construct concise summary prompt
        summary_prompt = f"""
Generate updated conversation summary. No prefixes, direct output only.

Requirements:
- Combine existing + new conversations
- Preserve important information
- Max 200 words
- Objective language

Existing: {summary}
New: {new_dialogs_text}
"""
        try:
            messages = [
                {"role": "system", "content": "You are a professional conversation analysis assistant. Output summary content directly without adding any prefixes or explanatory text."},
                {"role": "user", "content": summary_prompt}
            ]
            # Call LLM to generate summary
            response = await self.openai_client.chat.completions.create(
                model=self.config.llm_model,
                messages=messages,
                temperature=0.1,
                max_tokens=300
            )
            new_summary = response.choices[0].message.content.strip()
            return new_summary
        except Exception as e:
            logger.error(f"Error generating summary: {str(e)}", exc_info=True)
            return ""

    @safe_async_call(default_return="")
    async def generate_summary(self, content: str, assistant_response: str) -> str:
        """Generate a concise summary of the conversation"""
        # Build summary prompt
        dialog_history = [{"user": content, "assistant": assistant_response}]
        summary_prompt = f'''
Create concise conversation summary:

Dialog: {json.dumps(dialog_history, ensure_ascii=False)}

Guidelines:
- Max 200 words
- Key points only
- Objective tone
- Essential information
'''
        
        messages = [
            {"role": "system", "content": "You are an expert at generating precise and informative conversation summaries."},
            {"role": "user", "content": summary_prompt}
        ]
        
        response = await self.openai_client.chat.completions.create(
            model=self.config.llm_model,
            messages=messages,
            temperature=0.1,
            max_tokens=150
        )
        
        summary = response.choices[0].message.content.strip()
        return summary

    async def update_user_memory(self, session: Dict, content: str, assistant_response: str) -> str:
        """Update user memory based on conversation history"""
        # Get existing user memory
        existing_memory = session.get("user_memory_summary", "")
        
        # Get full dialog history for better context understanding
        session_data = SessionData.from_dict(session)
        full_dialog_history = session_data.get_recent_dialogs(10)  # Get recent 10 dialogs
        
        # Add current dialog
        current_dialog = {"user": content, "assistant": assistant_response}
        full_dialog_history.append(current_dialog)
        
        # Build concise user memory update prompt
        memory_update_prompt = f'''
Update user memory with priority focus:

Existing: {existing_memory}
History: {json.dumps(full_dialog_history[-5:], ensure_ascii=False)}

PRIORITIES:
1. Identity & Role (highest)
2. Location
3. Behavioral rules
4. Preferences
5. Other facts

RULES:
- Use imperative language ("You are...", "You must...")
- Latest instructions override previous
- Extract location from context
- Focus on actionable instructions

Output: Updated memory summary with identity/role at top.
'''
        
        try:
            messages = [
                {"role": "system", "content": "You are an expert at updating user memory with special focus on identity and role settings. Always prioritize explicit identity definitions, gender settings, and behavioral instructions from users. Use imperative language for role-based instructions."},
                {"role": "user", "content": memory_update_prompt}
            ]
            
            response = await self.openai_client.chat.completions.create(
                model=self.config.llm_model,
                messages=messages,
                temperature=0.1,
                max_tokens=250
            )
            
            updated_memory = response.choices[0].message.content.strip()
            return updated_memory
        
        except Exception as e:
            logger.error(f"Error updating user memory: {str(e)}")
            return existing_memory

    @safe_async_call(default_return="")
    async def extract_location_context(self, memory_layers: Dict) -> Optional[str]:
        """
        Intelligently extract location context
        - Completely rely on LLM to identify and process location information
        - Integrate location information from multiple sources
        - Provide concise, valuable location description
        """
        # Get all possible texts containing location information
        current_context = memory_layers.get("current_context", "")
        user_memory = memory_layers.get("validated_facts", "")
        conversation_summary = memory_layers.get("recent_interactions", "")
        
        try:
            location_extraction_prompt = f"""
Extract location by priority:
1. Context: {current_context[:100]}...
2. Memory: {user_memory[:100]}...
3. Summary: {conversation_summary[:100]}...

Keywords: "in X", "at X", "located in X"
Output: Specific location or "Not specified"
"""
            
            response = await self.openai_client.chat.completions.create(
                model=self.config.llm_model,
                messages=[
                    {"role": "system", "content": "You are a deterministic location extraction system. You MUST follow the priority rules exactly: Current Context > User Memory > Conversation Summary. Always use the same logic for the same input. Be consistent and deterministic."},
                    {"role": "user", "content": location_extraction_prompt}
                ],
                temperature=0.0,  # Completely deterministic
                max_tokens=200,
                seed=42  # Fixed seed to ensure consistency
            )
            
            location_details = response.choices[0].message.content.strip()
            
            return location_details if location_details else None
            
        except Exception as e:
            logger.warning(f"LLM location context extraction failed: {str(e)}")
            return None
