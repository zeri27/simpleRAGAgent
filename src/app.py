from flask import Flask, render_template, request, Response, jsonify
import json
import random
import time
from data_handlers.conversation_manager import (
    create_conversation,
    list_conversations,
    load_conversation,
    delete_conversation
)
from query_handler import handle_query, setup

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/conversations", methods=["GET"])
def get_conversations():
    return jsonify(list_conversations())

@app.route("/api/conversations", methods=["POST"])
def new_conversation():
    data = request.get_json() or {}
    title = data.get("title", "New Conversation")
    conv_id = create_conversation(title=title)
    return jsonify({"id": conv_id, "title": title})

@app.route("/api/conversations/<conv_id>", methods=["GET"])
def get_conversation(conv_id):
    try:
        return jsonify(load_conversation(conv_id))
    except FileNotFoundError:
        return jsonify({"error": "Conversation not found"}), 404

@app.route("/api/conversations/<conv_id>", methods=["DELETE"])
def remove_conversation(conv_id):
    delete_conversation(conv_id)
    return jsonify({"success": True})

@app.route("/api/chat/stream", methods=["POST"])
def stream_chat():
    data = request.get_json()
    conv_id = data.get("conversation_id")
    query = data.get("query")
    memory_required = data.get("memory_required", False)

    def generate():
        generator = handle_query(conv_id, query, memory_required)
        for chunk in generator:
            # Server-Sent Event format: data: <payload>\n\n
            yield f"data: {json.dumps({'content': chunk})}\n\n"
            if any(p in chunk for p in [".", "!", "?", "\n"]):
                time.sleep(random.uniform(0.15, 0.30))
            elif any(p in chunk for p in [",", ";", ":"]):
                time.sleep(random.uniform(0.08, 0.15))
            else:
                time.sleep(random.uniform(0.02, 0.05))

    return Response(generate(), mimetype="text/event-stream")

if __name__ == "__main__":
    setup()
    app.run(debug=True, port=5000)