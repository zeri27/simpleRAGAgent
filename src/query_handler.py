from data_handlers.embed_manager import embed
from data_handlers.memory_handler import retrieve_from_memory
from data_handlers.conversation_manager import (
    retrieve_conversation_history, 
    append_exchange, 
    rename_conversation, 
    get_conversation_name,
    retrieve_conversation_summary,
    retrieve_summary_index,
    retrieve_length_user_messages,
    save_conversation_summary
)

import ollama
import re

LLM_MODEL = "llama3.1:8b"

def setup():
    embed()

def retrieve_context(query):
    relevant_chunks = retrieve_from_memory(query)
    formatted_context = ""
    for i, item in enumerate(relevant_chunks, start=1):
        formatted_context += f"CONTEXT {i}:\n{item['chunk_text']}\n\n"
    return formatted_context

def generate_title(query):
    ollama_client = ollama.Client()
    prompt = f"""
    Task: Write a 2 to 3 word title summarizing the user query.
    
    Strict Rules:
    - Return EXACTLY 2 or 3 words.
    - Do NOT use quotes, punctuation, or full sentences.
    - Do NOT include conversational filler (eg, "Here is your title:", "Title:").
    
    User Query: "{query}"
    """
    response = ollama_client.generate(
        model=LLM_MODEL, 
        prompt=prompt,
        options={
            "temperature": 0.3, # Low temperature prevents chatty variations
        }
    )
    # Strip quotes, trailing punctuation, line breaks, and extra spaces
    clean_title = response['response'].strip()
    clean_title = re.sub(r'["\']', '', clean_title)
    clean_title = re.sub(r'[^\w\s]', '', clean_title) 
    clean_title = " ".join(clean_title.split()) 
    # Fallback safety check: enforce word count limit strictly
    words = clean_title.split()
    if len(words) > 3:
        clean_title = " ".join(words[:3])
    return clean_title.title()

def generate_summary(conversation_id):
    old_summary = retrieve_conversation_summary(conversation_id)
    conversation_history = retrieve_conversation_history(conversation_id)

    ollama_client = ollama.Client()

    prompt = f"""
    Task: Create a concise conversation summary.

    Strict Rules:

    - Return ONLY the summary.
    - Do NOT write introductions.
    - Do NOT write explanations.
    - Do NOT write "Here is a summary".
    - Do NOT write "Summary:".
    - Do NOT use bullet points.
    - Maximum 4 sentences.
    - Focus only on important facts, decisions, goals, and topics.
    - If an old summary exists, merge it with the new information.

    Old Summary:
    {old_summary}

    Conversation History:
    {conversation_history}
    """
    response = ollama_client.generate(
        model=LLM_MODEL,
        prompt=prompt,
        options={
            "temperature": 0.2,
        }
    )
    summary = response["response"].strip()
    summary = re.sub(
        r'^(here\s+is\s+(a\s+)?summary[:\-]?\s*)',
        '',
        summary,
        flags=re.IGNORECASE
    )
    summary = re.sub(
        r'^(summary[:\-]?\s*)',
        '',
        summary,
        flags=re.IGNORECASE
    )
    summary = re.sub(r'\s+', ' ', summary).strip()
    save_conversation_summary(conversation_id, summary)

def handle_query(conversation_id, query, memory_required=False):
    context = retrieve_context(query)

    if memory_required and not context:
        yield "No relevant context found. Unable to answer the question."
        return

    if get_conversation_name(conversation_id) == "New Conversation":
        new_title = generate_title(query)
        rename_conversation(conversation_id, new_title)

    if retrieve_length_user_messages(conversation_id) - retrieve_summary_index(conversation_id) >= 10:
        generate_summary(conversation_id)

    conversation_summary = retrieve_conversation_summary(conversation_id)
    conversation_history = retrieve_conversation_history(conversation_id)

    if memory_required:
        system_prompt = f"""
        You are a helpful assistant. You MUST answer using only the provided knowledge base context.

        Rules:
        - Treat the knowledge base as the source of truth.
        - Do not use outside knowledge.
        - Do not invent information.
        - If the answer cannot be found in the context, reply:
        "I don't have enough information to answer that."

        Conversation Summary:
        {conversation_summary}

        Knowledge Base Context:
        {context}
        """
    else:
        system_prompt = f"""
        You are a helpful assistant. 

        Use the provided context as additional reference material,
        but you may also rely on your own knowledge.

        If the context conflicts with known facts, mention the conflict and explain your reasoning.

        Conversation Summary:
        {conversation_summary}

        Knowledge Base Context:
        {context}
        """

    messages = [{"role": "system", "content": system_prompt}]
    messages.extend(conversation_history)
    messages.append({"role": "user", "content": query})

    ollama_client = ollama.Client()

    stream = ollama_client.chat(model=LLM_MODEL, messages=messages, stream=True)

    full_response = ""

    for chunk in stream:
        token = chunk["message"]["content"]
        full_response += token
        yield token

    append_exchange(conversation_id, query, full_response)
