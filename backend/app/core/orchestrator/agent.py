"""
Agent - formats conversation history naturally for LLM
"""
from typing import Dict, Optional, List
from app.core.llm.groq_client import groq_client
from app.core.llm.prompt_templates import PromptTemplates
from app.core.rag.retriever import retriever
from app.core.search.tavily_client import tavily_client
from app.core.orchestrator.router import query_router, QueryType
from app.utils.logger import get_logger

logger = get_logger(__name__)


class BankingSupportAgent:
    """Main orchestration agent"""
    
    def __init__(self):
        self.llm = groq_client
        self.retriever = retriever
        self.search = tavily_client
        self.router = query_router
    
    async def process_query(
        self, 
        query: str, 
        conversation_history: Optional[List[Dict]] = None
    ) -> Dict:
        """Process query with conversation history"""
        try:
            conversation_history = conversation_history or []
            
            # Route based on current query
            query_type, metadata = await self.router.route(query, {})
            logger.info(f"Query type: {query_type.value}")
            
            # Handle based on type
            if query_type == QueryType.ESCALATE:
                return self._handle_escalation(metadata)
            elif query_type == QueryType.RAG_ONLY:
                return await self._handle_rag(query, conversation_history)
            elif query_type == QueryType.SEARCH_ONLY:
                return await self._handle_search(query, conversation_history)
            else:  # HYBRID or FORM
                return await self._handle_hybrid(query, conversation_history)
                
        except Exception as e:
            logger.error(f"Error: {e}")
            return {"answer": "Error occurred.", "error": str(e)}
    
    async def _handle_rag(self, query: str, history: List[Dict]) -> Dict:
        """RAG with conversation context"""
        docs = await self.retriever.retrieve(query)
        
        if not docs:
            return {"answer": "No info found.", "sources": [], "method": "rag_no_results"}
        
        # Build context
        context = "\n\n".join([f"[{d['metadata'].get('source')}]\n{d['text'][:400]}" for d in docs[:3]])
        
        # Build messages with conversation history
        messages = [{"role": "system", "content": PromptTemplates.BANKING_ASSISTANT_SYSTEM}]
        
        # Add history
        if history:
            recent_history = history[-4:] if len(history) >= 4 else history
            for msg in recent_history:
                if isinstance(msg, dict) and "role" in msg and "content" in msg:
                    messages.append({
                        "role": msg["role"], 
                        "content": msg["content"][:500] if msg["content"] else ""
                    })
        
        # Add current query with context
        messages.append({
            "role": "user",
            "content": f"Documents:\n{context}\n\nQuestion: {query}"
        })
        
        answer = await self.llm.generate(messages)
        
        return {
            "answer": answer,
            "sources": [{"source": d["metadata"].get("source")} for d in docs[:3]],
            "method": "rag"
        }
    
    async def _handle_search(self, query: str, history: List[Dict]) -> Dict:
        """Search with conversation context"""
        
        # Enhance search query with conversation context
        search_query = query
        if history and len(history) >= 2:
            # Get the last user question
            last_user_msg = None
            for msg in reversed(history):
                if msg.get("role") == "user":
                    last_user_msg = msg.get("content", "")
                    break
            
            # If current query is short/vague, combine with previous context
            if last_user_msg and len(query.split()) <= 5:
                search_query = f"{last_user_msg} {query}"
                print(f"[DEBUG SEARCH] Enhanced query: {search_query}")
        
        results = await self.search.search_banking_info(search_query)
        
        if not results:
            return {"answer": "No results found.", "sources": [], "method": "search_no_results"}
        
        context = "\n\n".join([f"[{r['title']}]\n{r['content'][:400]}" for r in results[:3]])
        
        # Build messages
        messages = [{"role": "system", "content": PromptTemplates.BANKING_ASSISTANT_SYSTEM}]
        
        # Add history
        if history:
            recent_history = history[-4:] if len(history) >= 4 else history
            for msg in recent_history:
                if isinstance(msg, dict) and "role" in msg and "content" in msg:
                    messages.append({
                        "role": msg["role"], 
                        "content": msg["content"][:500] if msg["content"] else ""
                    })
        
        # Add current with search results
        messages.append({
            "role": "user",
            "content": f"Web results:\n{context}\n\nQuestion: {query}"
        })
        
        answer = await self.llm.generate(messages)
        
        return {
            "answer": answer,
            "sources": [{"title": r["title"], "url": r["url"]} for r in results[:3]],
            "method": "search"
        }
    
    async def _handle_hybrid(self, query: str, history: List[Dict]) -> Dict:
        """Hybrid with conversation context"""
        
        docs = await self.retriever.retrieve(query, top_k=2)
        
        # Enhance search query with conversation context
        search_query = query
        if history and len(history) >= 2:
            # Get the last user question
            last_user_msg = None
            for msg in reversed(history):
                if msg.get("role") == "user":
                    last_user_msg = msg.get("content", "")
                    break
            
            # If current query is short/vague, combine with previous context
            if last_user_msg and len(query.split()) <= 5:
                search_query = f"{last_user_msg} {query}"
                print(f"[DEBUG HYBRID SEARCH] Enhanced query: {search_query}")
        
        results = await self.search.search_banking_info(search_query)
        
        contexts = []
        if docs:
            contexts.append("Internal:\n" + "\n".join([d['text'][:300] for d in docs]))
        if results:
            contexts.append("Web:\n" + "\n".join([r['content'][:300] for r in results[:2]]))
        
        if not contexts:
            return {"answer": "No info found.", "sources": [], "method": "hybrid_no_results"}
        
        # Build messages
        messages = [{"role": "system", "content": PromptTemplates.BANKING_ASSISTANT_SYSTEM}]
        
        # Add history
        if history:
            recent_history = history[-4:] if len(history) >= 4 else history
            for msg in recent_history:
                if isinstance(msg, dict) and "role" in msg and "content" in msg:
                    messages.append({
                        "role": msg["role"], 
                        "content": msg["content"][:500] if msg["content"] else ""
                    })
        
        # Add current with combined context
        messages.append({
            "role": "user",
            "content": f"{chr(10).join(contexts)}\n\nQuestion: {query}"
        })
        
        answer = await self.llm.generate(messages)
        
        all_sources = []
        if docs:
            all_sources.extend([{"source": d["metadata"].get("source")} for d in docs])
        if results:
            all_sources.extend([{"title": r["title"], "url": r["url"]} for r in results[:2]])
        
        return {"answer": answer, "sources": all_sources, "method": "hybrid"}
    
    def _handle_escalation(self, metadata: Dict) -> Dict:
        reason = metadata.get("reason")
        
        if reason == "sensitive_information":
            msg = "Can't handle passwords/PINs. Call 1-800-555-BANK."
        elif reason == "account_access_required":
            msg = "Need to transfer you to access your account."
        else:
            msg = "Need a specialist for this."
        
        return {"answer": msg, "escalate": True, "reason": reason, "method": "escalation"}


banking_agent = BankingSupportAgent()