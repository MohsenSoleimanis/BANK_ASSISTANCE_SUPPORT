"""
Centralized prompt templates for LLM interactions
"""
from typing import Dict, List, Optional
from string import Template


class PromptTemplates:
    """Collection of prompt templates"""
    
    # System prompts
    BANKING_ASSISTANT_SYSTEM = """You are a professional bank support assistant helping customers with their banking needs.

Your capabilities:
- Answer questions using the bank's knowledge base
- Search the web for current banking information
- Help customers fill out forms step-by-step
- Escalate complex issues to human agents

Your constraints:
- NEVER make up account balances, transaction details, or personal information
- NEVER guess on regulatory or compliance matters
- ALWAYS cite your sources when answering from documents
- If you're unsure, say so and offer to escalate to a human agent
- For account-specific queries, explain that you need to transfer to a specialist

Your tone:
- Professional, helpful, and empathetic
- Use clear language and avoid unnecessary jargon
- Be patient and thorough"""

    # RAG prompts
    RAG_QUERY_TEMPLATE = Template("""You are a bank support assistant. Answer the user's question based ONLY on the provided documents.

DOCUMENTS:
$context

RULES:
1. Cite every claim with [Source: document_name]
2. If documents don't contain the answer, say: "I don't have that information in our knowledge base. Let me search for current information."
3. For account-specific queries, say: "I'll need to transfer you to a specialist who can access your account."
4. Never guess numbers (interest rates, fees, limits)
5. If information seems outdated, mention this and offer to search for current data

QUERY: $query

ANSWER:""")

    # Search prompts
    SEARCH_QUERY_TEMPLATE = Template("""Based on this question, generate an optimized search query.

QUESTION: $query

CONTEXT: $context

Generate a concise search query (1-6 words) that will find the most relevant current information.
Focus on: specific terms, current year if relevant, official sources.

SEARCH QUERY:""")

    # Form filling prompts
    FORM_START = Template("""I'll help you fill out the $form_name step by step.

This form requires:
$required_fields

I'll ask you for each field one at a time. You can skip optional fields or go back to change answers.

Let's start with: $first_field""")

    FORM_FIELD_REQUEST = Template("""Next, I need: $field_name

$field_description

$validation_rules

Please provide this information:""")

    FORM_VALIDATION_ERROR = Template("""I noticed an issue with that input: $error_message

Could you please provide it in this format: $expected_format""")

    FORM_PROGRESS = Template("""Great! You've completed $completed out of $total required fields.

$remaining_fields""")

    # Escalation prompts
    ESCALATION_PROMPT = Template("""I need to transfer you to a specialist for this request.

Reason: $reason

A specialist will be able to:
$specialist_capabilities

Would you like me to initiate the transfer?""")

    # Query routing prompts
    ROUTING_ANALYSIS = Template("""Analyze this query and determine the best approach:

QUERY: $query
CONTEXT: $context

Classify as one of:
1. RAG_ONLY - Can be answered from knowledge base
2. SEARCH_ONLY - Needs current web information
3. HYBRID - Needs both knowledge base and web search
4. FORM_FILLING - User wants to fill out a form
5. ESCALATE - Requires human agent

Respond with just the classification and confidence (0-1):""")


def format_rag_prompt(query: str, context: List[Dict]) -> str:
    """Format RAG prompt with retrieved context"""
    context_str = "\n\n".join([
        f"[Document {i+1}: {doc['source']}]\n{doc['content']}"
        for i, doc in enumerate(context)
    ])
    
    return PromptTemplates.RAG_QUERY_TEMPLATE.substitute(
        context=context_str,
        query=query
    )


def format_search_query_prompt(query: str, context: str = "") -> str:
    """Format prompt for search query generation"""
    return PromptTemplates.SEARCH_QUERY_TEMPLATE.substitute(
        query=query,
        context=context or "No additional context"
    )


def format_form_start_prompt(form_name: str, required_fields: List[str], first_field: str) -> str:
    """Format form filling start prompt"""
    fields_str = "\n".join([f"- {field}" for field in required_fields])
    
    return PromptTemplates.FORM_START.substitute(
        form_name=form_name,
        required_fields=fields_str,
        first_field=first_field
    )
