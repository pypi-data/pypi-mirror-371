"""
Memory Manager Module - Core component for managing conversation memory
"""

import logging
import asyncio
from functools import wraps
from typing import Dict, Optional, List
from datetime import datetime, timezone
from bson import ObjectId

from ..utils.config import Config
from .conversation_analyzer import ConversationAnalyzer
from .session_manager import SessionManager
from .vector_store import VectorStore
from .base import ManagerBase

logger = logging.getLogger(__name__)

def performance_log(func):
    """
    Decorator: Log method performance
    - Record execution time
    - Capture exceptions
    - Provide detailed performance and error logs
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = datetime.now()
        method_name = func.__name__
        session_id = kwargs.get('session_id', 'unknown')
        
        try:
            result = await func(*args, **kwargs)
            
            duration = (datetime.now() - start_time).total_seconds()
            logger.info(f"Method {method_name} completed in {duration:.4f} seconds for session {session_id}")
            
            return result
        
        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds()
            logger.error(
                f"Error in {method_name} after {duration:.4f} seconds: "
                f"session={session_id}, error={str(e)}", 
                exc_info=True
            )
            raise
    
    return wrapper

class MemoryManager(ManagerBase):
    def __init__(self, config: Config):
        super().__init__(config)
        
        self.conversation_analyzer = ConversationAnalyzer(config)
        self.session_manager = SessionManager(config)
        self.vector_store = VectorStore(config, self.session_manager)
        
        # MongoDB collection names
        self.mongo_db = 'mfcs_memory'
        
    def _smart_truncate_text(self, text: str, max_length: int, preserve_ends: bool = True) -> str:
        """
        Intelligently truncate text, preserving important information
        
        Args:
            text: Text to truncate
            max_length: Maximum length
            preserve_ends: Whether to preserve beginning and end
        
        Returns:
            Truncated text
        """
        if len(text) <= max_length:
            return text
        
        if not preserve_ends:
            # Simple truncation
            return text[:max_length-3] + "..."
        
        # Intelligent truncation: preserve beginning and end
        if max_length < 100:
            return text[:max_length-3] + "..."
        
        # Calculate preservation length
        keep_start = max_length // 3
        keep_end = max_length // 3
        truncated_info = f"\n[...truncated {len(text) - max_length} characters...]\n"
        
        # Ensure not exceeding max length
        available_length = max_length - len(truncated_info)
        keep_start = min(keep_start, available_length // 2)
        keep_end = min(keep_end, available_length - keep_start)
        
        return text[:keep_start] + truncated_info + text[-keep_end:]
    

    
    def _validate_total_prompt_length(self, prompt: str) -> str:
        """
        Validate and control total prompt length
        
        Args:
            prompt: Complete system prompt
            
        Returns:
            Processed prompt
        """
        current_length = len(prompt)
        max_length = self.config.max_total_prompt_length
        warning_threshold = self.config.prompt_warning_threshold
        
        # Log length information
        logger.info(f"System prompt length: {current_length} characters")
        
        if current_length >= warning_threshold:
            logger.warning(f"Prompt length approaching limit: {current_length}/{max_length} characters ({current_length/max_length*100:.1f}%)")
        
        if current_length <= max_length:
            return prompt
        
        logger.error(f"Prompt exceeds limit: {current_length} > {max_length} characters, truncating")
        
        # Emergency truncation - preserve most important parts
        return self._smart_truncate_text(prompt, max_length, preserve_ends=True)

    async def get(self, memory_id: str, content: Optional[str] = None, top_k: int = 2) -> str:
        """
        Quickly retrieve memory updated after last retrieval
        - Includes latest immediate context
        - Optional vector retrieval
        
        :param memory_id: Session identifier
        :param content: Optional context content for historical retrieval
        :param top_k: Number of relevant histories to retrieve, default 2
        """
        try:
            # Get or create session
            session = await self.session_manager.get_or_create_session(memory_id)
            session_id = str(session["_id"])

            # Build memory layers
            memory_layers = await self._build_layered_memory(session_id, session)

            # If content provided and vector retrieval configured, attempt to get relevant history
            if content and top_k > 0:
                try:
                    # Get relevant dialog history
                    relevant_history = await self._get_relevant_dialogs(
                        session_id, 
                        content, 
                        top_k, 
                        similarity_threshold=self.config.local_similarity_threshold
                    )
                    
                    # If relevant history exists, add to memory layers
                    if relevant_history:
                        memory_layers["relevant_history"] = "\n".join([
                            f"User: {dialog['user']}\nAssistant: {dialog['assistant']}" 
                            for dialog in relevant_history
                        ])
                except Exception as history_error:
                    logger.warning(f"Vector retrieval failed: {str(history_error)}")

            # Build system prompt
            system_prompt = await self._build_system_prompt(memory_layers)
            return system_prompt
            
        except Exception as e:
            logger.error(f"Memory retrieval error for {memory_id}: {str(e)}")
            return ""

    async def _update_location_context(self, session_id: str, content: str) -> None:
        """
        Asynchronously update location context in session
        This method runs in background to avoid blocking main flow
        """
        try:
            # Get current session
            session = await self.session_manager.get_session(session_id)
            if not session:
                logger.warning(f"Session {session_id} not found for location context update")
                return
            
            # Extract location context using conversation analyzer
            memory_layers = {
                "current_context": content,
                "validated_facts": session.get("user_memory_summary", ""),
                "recent_interactions": session.get("conversation_summary", "")
            }
            location_context = await self.conversation_analyzer.extract_location_context(memory_layers)
            
            # Update session with new location context
            if location_context:
                await self.session_manager.update_session_memory(
                    session_id, 
                    {"location_context": location_context}
                )
                logger.info(f"Location context updated for session {session_id}")
            
        except Exception as e:
            logger.error(f"Error updating location context for session {session_id}: {str(e)}")

    @performance_log
    async def _get_relevant_dialogs(
        self, 
        session_id: str, 
        content: str, 
        top_k: int, 
        similarity_threshold: float = 0.7
    ) -> List[Dict]:
        """
        Get relevant dialog history
        - Directly use Qdrant similarity score to avoid redundant calculations
        - Single embedding calculation, efficient retrieval
        """
        try:
            # Search relevant dialogs from vector store, directly using Qdrant similarity score
            relevant_dialogs = await self.vector_store.search_dialog_with_chunk(
                session_id, 
                content, 
                top_k * 2,  # Get more candidates, then filter by threshold
                query_embedding=None  # Let VectorStore calculate embedding once
            )
            
            # Filter using Qdrant similarity score (avoid redundant calculation)
            filtered_dialogs = []
            for dialog in relevant_dialogs:
                # Qdrant returns similarity as cosine similarity
                if dialog.get('similarity', 0) >= similarity_threshold:
                    filtered_dialogs.append(dialog)
                else:
                    logger.debug(f"Dialog filtered out due to low similarity: {dialog.get('similarity', 0)}")
            
            # Already sorted by similarity, directly return
            return filtered_dialogs[:top_k]
                        
        except Exception as e:
            logger.error(f"Error retrieving relevant dialogs for session {session_id}: {str(e)}")
            return []

    async def update(self, memory_id: str, content: str, assistant_response: str) -> bool:
        """
        Quickly update conversation memory, asynchronously process data persistence
        - Supports multi-processing
        - Fast return
        - Asynchronous data storage
        """
        try:
            # Get or create session
            session = await self.session_manager.get_or_create_session(memory_id)
            session_id = str(session["_id"])

            # Prepare dialog data to store
            dialog_entry = {
                "session_id": session_id,
                "memory_id": memory_id,
                "user_content": content,
                "assistant_response": assistant_response,
                "timestamp": datetime.now(timezone.utc)
            }

            # Asynchronously start background processing task with dialog history update
            task = asyncio.create_task(self._comprehensive_memory_processing(
                session=session, 
                content=content, 
                assistant_response=assistant_response, 
                memory_id=memory_id
            ))
            # Add task exception handling callback
            task.add_done_callback(self._handle_task_completion)

            return True
        except Exception as e:
            logger.error(f"Memory update error for {memory_id}: {str(e)}")
            return False

    @performance_log
    async def _comprehensive_memory_processing(
        self, 
        session: Dict, 
        content: str, 
        assistant_response: str, 
        memory_id: str,
        session_id: Optional[str] = None
    ):
        """
        Comprehensive asynchronous background memory processing
        - Does not block main process
        - Supports multi-processing
        - Intelligent context and location tracking
        """
        session_id = session_id or str(session["_id"])
        
        try:
            # Default analysis result, ensure basic processing even if analysis fails
            analysis_result = {
                "requires_memory_update": True,
                "requires_summary_update": True
            }
            
            conversation_summary = ""
            user_memory = ""
            
            try:
                # Attempt parallel processing of conversation analysis, summary generation, and memory update
                analysis_result, conversation_summary, user_memory = await asyncio.gather(
                    # Analyze conversation updates
                    self.conversation_analyzer.analyze_conversation_updates(session, {
                        "user": content, 
                        "assistant": assistant_response
                    }),
                    
                    # Generate conversation summary
                    self._generate_conversation_summary(content, assistant_response),
                    
                    # Update user memory
                    self._update_user_memory(session, content, assistant_response),
                    
                    return_exceptions=True  # Prevent single task failure from affecting overall
                )
                
                # Check if any tasks returned exceptions
                if isinstance(analysis_result, Exception):
                    logger.warning(f"Conversation analysis failed: {analysis_result}")
                    analysis_result = {"requires_memory_update": True, "requires_summary_update": True}
                
                if isinstance(conversation_summary, Exception):
                    logger.warning(f"Conversation summary failed: {conversation_summary}")
                    conversation_summary = ""
                    
                if isinstance(user_memory, Exception):
                    logger.warning(f"User memory update failed: {user_memory}")
                    user_memory = ""
                    
            except asyncio.CancelledError:
                logger.warning(f"Parallel processing was cancelled for session_id={session_id}")
                # Use default analysis result when task is cancelled, but keep existing summary and memory
                analysis_result = {"requires_memory_update": True, "requires_summary_update": True}
                # Do not reset conversation_summary and user_memory, they are already initialized as ""
                # If needed, can attempt to retrieve from session
                if not conversation_summary:
                    conversation_summary = session.get("conversation_summary", "")
                if not user_memory:
                    user_memory = session.get("user_memory_summary", "")
            except Exception as processing_error:
                logger.warning(f"Memory processing partial failure: {str(processing_error)}")
                # Generate basic summary even if processing fails
                try:
                    conversation_summary = await self._generate_conversation_summary(content, assistant_response)
                    user_memory = await self._update_user_memory(session, content, assistant_response)
                except asyncio.CancelledError:
                    logger.warning(f"Fallback processing was cancelled")
                    # Keep existing values, do not reset to empty
                    if not conversation_summary:
                        conversation_summary = session.get("conversation_summary", "")
                    if not user_memory:
                        user_memory = session.get("user_memory_summary", "")
                except Exception as fallback_error:
                    logger.error(f"Fallback processing also failed: {fallback_error}")
                    # Final fallback: try to recover from session, reset to empty only if that fails
                    if not conversation_summary:
                        conversation_summary = session.get("conversation_summary", "")
                    if not user_memory:
                        user_memory = session.get("user_memory_summary", "")

            # First update location context to get the latest location information
            await self._update_location_context(session_id, content)
            
            # Get updated session with latest location context
            updated_session = await self.session_manager.get_session(session_id)
            if not updated_session:
                updated_session = session  # Fallback to original session
            
            # Build layered memory with updated session data
            memory_layers = await self._build_layered_memory(
                session_id, 
                updated_session
            )

            # Prepare dialog entry for batch storage
            dialog_entry = {
                "session_id": session_id,
                "memory_id": memory_id,
                "user_content": content,
                "assistant_response": assistant_response,
                "timestamp": datetime.now(timezone.utc)
            }
            
            # Parallel storage and update (removed memory_layers from session update to avoid overwrite)
            await asyncio.gather(
                # Batch store dialog, dialog history, and preprocessed memories
                self._store_memory_data(session_id, dialog_entry, memory_layers, content, assistant_response),
                
                # Update session record (without memory_layers to avoid overwriting location_context)
                self.session_manager.update_session_memory(session_id, {
                    "conversation_summary": conversation_summary,
                    "user_memory_summary": user_memory
                }),
                
                # Vector storage
                self.vector_store.save_dialog_with_chunk(
                    session_id, 
                    content, 
                    assistant_response, 
                    memory_id
                )
            )
            
            # Data consistency validation: verify location_context was updated correctly
            try:
                final_session = await self.session_manager.get_session(session_id)
                if final_session:
                    final_location = final_session.get("location_context", "")
                    memory_location = memory_layers.get("location_context", "")
                    if final_location != memory_location:
                        logger.warning(f"Location context mismatch detected for session {session_id}: "
                                     f"session='{final_location}' vs memory_layers='{memory_location}'")
                    else:
                        logger.debug(f"Location context validation passed for session {session_id}: '{final_location}'")
            except Exception as validation_error:
                logger.error(f"Data consistency validation failed for session {session_id}: {validation_error}")
            
        except Exception as e:
            logger.error(f"Comprehensive memory processing error for session {session_id}: {str(e)}")
            # Even with severe errors, record basic dialog
            try:
                await self.session_manager.update_dialog_history(session["_id"], content, assistant_response)
            except Exception as final_error:
                logger.critical(f"Failed to even update dialog history: {str(final_error)}")
    
    def _handle_task_completion(self, task):
        """Handle async task completion callback"""
        try:
            if task.cancelled():
                logger.warning(f"Background memory processing task was cancelled")
                return
                
            exception = task.exception()
            if exception:
                if isinstance(exception, asyncio.CancelledError):
                    logger.warning(f"Background memory processing task was cancelled during execution")
                else:
                    logger.error(f"Background memory processing task failed: {exception}")
            else:
                logger.info(f"Background memory processing task completed successfully")
        except asyncio.CancelledError:
            logger.warning(f"Task completion callback was cancelled")
        except Exception as e:
            logger.error(f"Error in task completion callback: {str(e)}")

    async def _store_memory_data(self, session_id: str, dialog_entry: Dict, memory_layers: Dict, content: str, assistant_response: str) -> None:
        """
        Store dialog record, dialog history update, and preprocessed memory layers in batch
        - Reduced database calls
        - Asynchronous storage
        - Includes dialog history update
        """
        try:
            # Batch storage operations including dialog history update
            tasks = [
                # Store dialog record
                asyncio.to_thread(
                    self.session_manager.mongo_client[self.mongo_db]['dialog_records'].insert_one,
                    dialog_entry
                ),
                # Update dialog history in session
                asyncio.to_thread(
                    self.session_manager.mongo_client[self.mongo_db]['memory_sessions'].find_one_and_update,
                    {"_id": ObjectId(session_id)},
                    {
                        "$push": {"dialog_history": {"user": content, "assistant": assistant_response}},
                        "$set": {"updated_at": datetime.now(timezone.utc)}
                    },
                    return_document=True
                ),
                # Store preprocessed memory layers
                asyncio.to_thread(
                    self.session_manager.mongo_client[self.mongo_db]['pre_processed_memories'].update_one,
                    {"session_id": session_id},
                    {"$set": {
                        "session_id": session_id,
                        "current_context": memory_layers.get("current_context", ""),
                        "validated_facts": memory_layers.get("validated_facts", ""),
                        "recent_interactions": memory_layers.get("recent_interactions", ""),
                        "location_context": memory_layers.get("location_context", ""),
                        "updated_at": datetime.now(timezone.utc)
                    }},
                    upsert=True
                )
            ]
            await asyncio.gather(*tasks)
        except Exception as e:
            logger.error(f"Error storing memory data: {str(e)}")

    async def _build_system_prompt(self, memory_layers: Dict) -> str:
        """
        Build system prompt - simplified version
        - Reduce complex priority logic
        - Focus on core functionality
        """
        prompt_parts = []
        
        # 1. Immediate instructions (highest priority)
        current_context = memory_layers.get("current_context")
        if current_context:
            prompt_parts.append(f"## Immediate Instructions\nIMMEDIATE USER INSTRUCTIONS - HIGHEST PRIORITY (overrides all previous settings)\n{current_context}")
        
        # 2. User identity settings (only when no immediate instructions)
        elif memory_layers.get("validated_facts"):
            user_profile = memory_layers["validated_facts"]
            prompt_parts.append(f"## Identity & Role Settings\nUser-defined identity, gender, role, and behavioral instructions (HIGHEST PRIORITY)\n{user_profile}")
        
        # 3. Conversation context
        interaction_context = memory_layers.get("recent_interactions")
        if interaction_context:
            prompt_parts.append(f"## Interaction Context\nRecent conversation details and active dialogue\n{interaction_context}")
        
        # 4. Location information
        location_context = memory_layers.get("location_context")
        if location_context:
            prompt_parts.append(f"## Location Context\nUser's geographical location and environment\n{location_context}")
        
        # 5. Relevant history (if any)
        relevant_history = memory_layers.get("relevant_history")
        if relevant_history:
            prompt_parts.append(f"## Relevant History\nRelated past conversations\n{relevant_history}")

        final_prompt = "\n\n".join(prompt_parts)
        
        # Validate and control total prompt length
        return self._validate_total_prompt_length(final_prompt)

    async def _build_layered_memory(self, session_id: str, session: Dict) -> Dict[str, str]:
        """Build layered memory system"""
        layers = {
            "current_context": "",
            "validated_facts": "",
            "recent_interactions": "",
            "location_context": ""
        }
        
        try:
            # 1. Intelligently process user memory - as supplementary information
            if session.get("user_memory_summary"):
                layers["validated_facts"] = session["user_memory_summary"]
                    
            # 2. Intelligently process conversation summary
            if session.get("conversation_summary"):
                layers["recent_interactions"] = session["conversation_summary"]
            
            # 3. Get cached location context from session (async processing)
            if session.get("location_context"):
                layers["location_context"] = session["location_context"]
            
            return layers

        except Exception as e:
            logger.error(f"Error building layered memory for {session_id}: {str(e)}")
            return layers

    async def _generate_conversation_summary(self, content: str, assistant_response: str) -> str:
        """Generate conversation summary"""
        try:
            return await self.conversation_analyzer.generate_summary(content, assistant_response) or ""
        except Exception as e:
            logger.error(f"Error generating conversation summary: {str(e)}")
            return ""

    async def _update_user_memory(self, session: Dict, content: str, assistant_response: str) -> str:
        """Update user memory"""
        try:
            return await self.conversation_analyzer.update_user_memory(session, content, assistant_response) or ""
        except Exception as e:
            logger.error(f"Error updating user memory: {str(e)}")
            return ""
