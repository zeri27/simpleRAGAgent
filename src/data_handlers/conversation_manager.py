from data_handlers.data_manager import STORAGE_DIR
from uuid import uuid4
from datetime import datetime
import json
import os

CONV_DIR = STORAGE_DIR / "conversations"

def create_conversation(title="New Conversation"):
    CONV_DIR.mkdir(parents=True, exist_ok=True)
    conversation_id = uuid4().hex
    conversation_data = {
        "id": conversation_id,
        "title": title,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
        "summary": {
            "text": "",
            "index": 0
        },
        "messages": []
    }

    conversation_path = CONV_DIR / f"{conversation_id}.json"
    with conversation_path.open("w", encoding="utf-8") as f:
        json.dump(conversation_data, f, indent=4)

    return conversation_id

def retrieve_conversation_history(conversation_id, max_messages=10):
    conversation = load_conversation(conversation_id)
    return conversation["messages"][-max_messages:]

def load_conversation(conversation_id):
    conversation_path = CONV_DIR / f"{conversation_id}.json"
    if not conversation_path.exists():
        raise FileNotFoundError(f"Conversation with ID {conversation_id} not found.")
    with conversation_path.open("r", encoding="utf-8") as f:
        return json.load(f)

def save_conversation(conversation_data):
    conversation_id = conversation_data["id"]
    conversation_path = CONV_DIR / f"{conversation_id}.json"
    conversation_data["updated_at"] = datetime.now().isoformat()
    with conversation_path.open("w", encoding="utf-8") as f:
        json.dump(conversation_data, f, indent=4)
        
def append_message(conversation_id, role, content):
    conversation = load_conversation(conversation_id)
    if conversation:
        conversation["messages"].append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })
        save_conversation(conversation)

def append_exchange(conversation_id, query, response):
    append_message(conversation_id, "user", query)
    append_message(conversation_id, "assistant", response)

def list_conversations():
    if not CONV_DIR.exists():
        return []
    
    conversations = []
    for filename in os.listdir(CONV_DIR):
        if filename.endswith(".json"):
            conversation_path = CONV_DIR / filename
            with conversation_path.open("r", encoding="utf-8") as f:
                conversation_data = json.load(f)
                conversations.append(conversation_data)
    conversations.sort(key=lambda x: x["updated_at"], reverse=True)
    return conversations

def get_conversation_name(conversation_id):
    conversation = load_conversation(conversation_id)
    return conversation["title"]

def rename_conversation(conversation_id, new_title):
    conversation = load_conversation(conversation_id)
    if conversation:
        conversation["title"] = new_title
        save_conversation(conversation)

def delete_conversation(conversation_id):
    conversation_path = CONV_DIR / f"{conversation_id}.json"
    if conversation_path.exists():
        os.remove(conversation_path)

def retrieve_conversation_summary(conversation_id):
    conversation = load_conversation(conversation_id)
    return conversation["summary"]["text"]

def save_conversation_summary(conversation_id, summary_text):
    conversation = load_conversation(conversation_id)
    if conversation:
        conversation["summary"]["text"] = summary_text
        conversation["summary"]["index"] += 10
        save_conversation(conversation)

def retrieve_summary_index(conversation_id):
    conversation = load_conversation(conversation_id)
    return conversation["summary"]["index"]

def retrieve_length_user_messages(conversation_id):
    conversation = load_conversation(conversation_id)
    user_messages = [msg for msg in conversation["messages"] if msg["role"] == "user"]
    return len(user_messages)

