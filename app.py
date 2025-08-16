
from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv
import os
import io
import logging
from datetime import datetime
from schemas import AudioRequest, AudioResponse, LLMQueryRequest, LLMQueryResponse
from services.tts_service import murf_tts
from services.stt_service import transcribe_audio
from services.llm_service import query_llm

from flask_socketio import SocketIO, send
from flask_sock import Sock


load_dotenv()


app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")
sock = Sock(app)
# ----------------- WebSocket Echo Endpoint -----------------
@sock.route('/ws')
def websocket_echo(ws):
    while True:
        data = ws.receive()
        if data is None:
            break
        logger.info(f"[Flask-Sock WS] Received: {data}")
        ws.send(data)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
# In-memory chat history storage
chat_sessions = {}

# ----------------- WebSocket Echo Endpoint -----------------
@socketio.on('message')
def handle_ws_message(msg):
    logger.info(f"WebSocket received: {msg}")
    send(msg)

# In-memory chat history storage
chat_sessions = {}

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/api")
def api():
    return render_template("api.html")

# -------------- TEXT TO SPEECH (MURF) ----------------


@app.route("/generate-audio", methods=["POST"])
def generate_audio():
    try:
        req_data = request.get_json() if request.is_json else request.form
        text = req_data.get("text")
        if not text:
            return jsonify({"error": "No text provided"}), 400
        audio_url = murf_tts(text)
        if not audio_url:
            return jsonify({"error": "Failed to generate audio. Please try again later."}), 502
        return jsonify({"audio_url": audio_url})
    except Exception as e:
        logger.exception("Error in generate_audio")
        return jsonify({"error": "Internal server error. Please try again later."}), 500

# -------------- ECHO BOT COMBINED ----------------
@app.route("/tts/echo", methods=["POST"])
def echo_bot():
    try:
        if "audio" not in request.files:
            return jsonify({"error": "No audio file"}), 400
        audio_file = request.files["audio"]
        audio_bytes = io.BytesIO(audio_file.read())
        text = transcribe_audio(audio_bytes)
        if not text:
            return jsonify({"error": "Transcription failed. Please try again."}), 502
        audio_url = murf_tts(text)
        if not audio_url:
            return jsonify({"error": "Failed to generate AI voice. Please try again later."}), 502
        return jsonify({"transcription": text, "audio_url": audio_url})
    except Exception as e:
        logger.exception("Error in echo_bot")
        return jsonify({"error": "Internal server error. Please try again later."}), 500

#-----------------------------Gemini API--------------------------



@app.route("/llm/query", methods=["POST"])
def llm_query():
    try:
        if "audio" in request.files:
            audio_file = request.files["audio"]
            if not audio_file:
                return jsonify({"error": "No audio file provided"}), 400
            audio_bytes = io.BytesIO(audio_file.read())
            text = transcribe_audio(audio_bytes)
            if not text:
                return jsonify({"error": "Failed to transcribe audio. Please try again."}), 502
        else:
            payload = request.get_json(force=True)
            text = payload.get("text")
            if not text:
                return jsonify({"error": "No text or audio provided"}), 400
        llm_response = query_llm(text)
        if not llm_response:
            return jsonify({"error": "Empty response from LLM. Please try again later."}), 502
        audio_url = murf_tts(llm_response)
        if not audio_url:
            return jsonify({"error": "Failed to generate audio response. Please try again later."}), 502
        return jsonify({
            "transcription": text if "audio" in request.files else None,
            "llm_response": llm_response,
            "audio_url": audio_url
        }), 200
    except Exception as e:
        logger.exception("Error in llm_query")
        return jsonify({"error": "Internal server error. Please try again later."}), 500

# -------------- CHAT SESSION WITH HISTORY ----------------
def get_or_create_session(session_id):
    """Get existing session or create new one"""
    if session_id not in chat_sessions:
        chat_sessions[session_id] = {
            "messages": [],
            "created_at": datetime.now(),
            "last_activity": datetime.now()
        }
    else:
        chat_sessions[session_id]["last_activity"] = datetime.now()
    return chat_sessions[session_id]

def add_message_to_session(session_id, role, content):
    """Add a message to the session history"""
    session = get_or_create_session(session_id)
    message = {
        "role": role,  # "user" or "assistant"
        "content": content,
        "timestamp": datetime.now()
    }
    session["messages"].append(message)
    return session

def build_conversation_context(session_id, new_user_message):
    """Build conversation context for LLM including chat history"""
    session = get_or_create_session(session_id)
    
    # Build conversation string
    conversation = []
    
    # Add previous messages
    for msg in session["messages"]:
        if msg["role"] == "user":
            conversation.append(f"User: {msg['content']}")
        else:
            conversation.append(f"Assistant: {msg['content']}")
    
    # Add new user message
    conversation.append(f"User: {new_user_message}")
    
    # Join with newlines and add context
    context = "You are a helpful AI assistant. Here is our conversation:\n\n" + "\n".join(conversation)
    
    return context

@app.route("/agent/chat/<session_id>", methods=["POST"])
def agent_chat(session_id):
    """Chat endpoint with session-based history"""
    try:
        # Validate session_id
        if not session_id or len(session_id) < 1:
            return jsonify({"error": "Invalid session ID"}), 400
        # Check if audio file is provided
        if "audio" not in request.files:
            return jsonify({"error": "No audio file provided"}), 400
        audio_file = request.files["audio"]
        if not audio_file:
            return jsonify({"error": "Empty audio file"}), 400
        audio_bytes = io.BytesIO(audio_file.read())
        # Step 1: Transcribe audio
        user_message = transcribe_audio(audio_bytes)
        if not user_message:
            return jsonify({"error": "Failed to transcribe audio. Please try again."}), 502
        # Step 2: Add user message to chat history and build context
        try:
            conversation_context = build_conversation_context(session_id, user_message)
            add_message_to_session(session_id, "user", user_message)
        except Exception as e:
            logger.exception("Chat history error")
            return jsonify({"error": f"Chat history error: {str(e)}"}), 500
        # Step 3: Send conversation context to Gemini LLM
        logger.info(f"[agent_chat] Sending context to LLM: {conversation_context}")
        llm_response = query_llm(conversation_context)
        logger.info(f"[agent_chat] LLM response: {llm_response}")
        if not llm_response:
            logger.error("[agent_chat] Empty response from LLM.")
            return jsonify({"error": "Empty response from LLM. Please try again later."}), 502
        # Step 4: Add LLM response to chat history
        try:
            add_message_to_session(session_id, "assistant", llm_response)
        except Exception as e:
            logger.exception("Failed to save LLM response")
            return jsonify({"error": f"Failed to save LLM response: {str(e)}"}), 500
        # Step 5: Generate audio from LLM response using Murf
        try:
            audio_url = murf_tts(llm_response)
            if not audio_url:
                return jsonify({"error": "Failed to generate audio response. Please try again later."}), 502
        except Exception as e:
            logger.exception("Audio generation failed")
            return jsonify({"error": f"Audio generation failed: {str(e)}"}), 500
        # Step 6: Return response with session info
        session_info = chat_sessions[session_id]
        return jsonify({
            "session_id": session_id,
            "transcription": user_message,
            "llm_response": llm_response,
            "audio_url": audio_url,
            "message_count": len(session_info["messages"]),
            "last_activity": session_info["last_activity"].isoformat()
        })
    except Exception as e:
        logger.exception("Error in agent_chat")
        return jsonify({"error": "Internal server error. Please try again later."}), 500

@app.route("/agent/session/<session_id>/history", methods=["GET"])
def get_session_history(session_id):
    """Get chat history for a specific session"""
    if session_id not in chat_sessions:
        return jsonify({"error": "Session not found"}), 404
    
    session = chat_sessions[session_id]
    return jsonify({
        "session_id": session_id,
        "messages": [
            {
                "role": msg["role"],
                "content": msg["content"],
                "timestamp": msg["timestamp"].isoformat()
            }
            for msg in session["messages"]
        ],
        "created_at": session["created_at"].isoformat(),
        "last_activity": session["last_activity"].isoformat()
    })

@app.route("/agent/session/<session_id>", methods=["DELETE"])
def clear_session(session_id):
    """Clear/delete a chat session"""
    if session_id in chat_sessions:
        del chat_sessions[session_id]
        return jsonify({"message": f"Session {session_id} cleared"})
    else:
        return jsonify({"error": "Session not found"}), 404



socketio = SocketIO(app, cors_allowed_origins="*")

@socketio.on('message', namespace='/ws')
def handle_ws_message(msg):
    print(f"Received via websocket: {msg}")
    send(msg, namespace='/ws')  # Echo back


if __name__ == "__main__":
    socketio.run(app, debug=True)
