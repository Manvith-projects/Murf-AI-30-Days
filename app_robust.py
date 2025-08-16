"""
Robust Flask Application with Comprehensive Error Handling
Features:
- Try-catch blocks for all API calls
- Fallback responses for each service
- Error simulation capabilities
- Graceful degradation
- Detailed logging
"""

from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv
import os
import requests
from werkzeug.utils import secure_filename
import assemblyai as aai
import io
from google import genai
import uuid
from datetime import datetime
import logging
import time
import base64
from functools import wraps

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

load_dotenv()

app = Flask(__name__)

# In-memory chat history storage
chat_sessions = {}

# Configuration with fallback handling
class AppConfig:
    def __init__(self):
        self.murf_api_key = os.getenv("MURF_API_KEY")
        self.assemblyai_api_key = os.getenv("ASSEMBLYAI_API_KEY")
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")
        
        # Error simulation flags (set to True to simulate API failures)
        self.simulate_murf_error = False
        self.simulate_assemblyai_error = False
        self.simulate_gemini_error = False
        
        # Fallback settings
        self.fallback_audio_enabled = True
        self.fallback_text_responses = {
            "stt_error": "I'm having trouble hearing you right now. Could you please try again?",
            "llm_error": "I'm having trouble connecting to my brain right now. Please try again in a moment.",
            "tts_error": "I'm having trouble speaking right now, but I can still help you with text responses.",
            "general_error": "I'm experiencing some technical difficulties. Please try again later."
        }
        
        logger.info(f"Configuration loaded:")
        logger.info(f"- MURF API Key: {'✓ Available' if self.murf_api_key else '✗ Missing'}")
        logger.info(f"- AssemblyAI API Key: {'✓ Available' if self.assemblyai_api_key else '✗ Missing'}")
        logger.info(f"- Gemini API Key: {'✓ Available' if self.gemini_api_key else '✗ Missing'}")

config = AppConfig()

# Initialize APIs with error handling
try:
    if config.assemblyai_api_key:
        aai.settings.api_key = config.assemblyai_api_key
        logger.info("AssemblyAI initialized successfully")
    else:
        logger.warning("AssemblyAI API key not found")
except Exception as e:
    logger.error(f"Failed to initialize AssemblyAI: {e}")

try:
    if config.gemini_api_key:
        gemini_client = genai.Client(api_key=config.gemini_api_key)
        logger.info("Gemini client initialized successfully")
    else:
        logger.warning("Gemini API key not found")
        gemini_client = None
except Exception as e:
    logger.error(f"Failed to initialize Gemini client: {e}")
    gemini_client = None

# Error handling decorator
def handle_errors(fallback_message="Service temporarily unavailable"):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.error(f"Error in {func.__name__}: {str(e)}")
                return {"error": str(e), "fallback": fallback_message}, 500
        return wrapper
    return decorator

# Fallback audio generation (simple TTS alternative)
def generate_fallback_audio(text):
    """Generate a simple fallback audio response"""
    try:
        # This could be replaced with a local TTS library like pyttsx3
        # For now, we'll return a base64 encoded silence or use a simple TTS service
        logger.info(f"Generating fallback audio for: {text[:50]}...")
        
        # Return None for now - frontend should handle text-only responses
        return None
    except Exception as e:
        logger.error(f"Fallback audio generation failed: {e}")
        return None

# -------------- ROBUST TEXT TO SPEECH (MURF) ----------------
@handle_errors("Audio generation temporarily unavailable")
def murf_tts(text, timeout=30):
    """
    Robust TTS with comprehensive error handling
    """
    if config.simulate_murf_error:
        logger.info("Simulating MURF API error")
        raise Exception("Simulated MURF API failure")
    
    if not config.murf_api_key:
        logger.error("MURF API key not configured")
        raise Exception("TTS service not configured")
    
    if not text or not text.strip():
        logger.error("Empty text provided to TTS")
        raise Exception("No text provided for speech synthesis")
    
    # Truncate text if too long
    max_chars = 5000
    if len(text) > max_chars:
        text = text[:max_chars] + "..."
        logger.warning(f"Text truncated to {max_chars} characters")
    
    headers = {"api-key": config.murf_api_key}
    payload = {
        "text": text,
        "voiceId": "en-US-natalie",
    }
    
    logger.info(f"MURF Request: {len(text)} characters")
    
    try:
        response = requests.post(
            "https://api.murf.ai/v1/speech/generate",
            headers=headers, 
            json=payload,
            timeout=timeout
        )
        
        logger.info(f"MURF Response Status: {response.status_code}")
        
        if response.status_code == 401:
            raise Exception("MURF API authentication failed - check API key")
        elif response.status_code == 429:
            raise Exception("MURF API rate limit exceeded - please try again later")
        elif response.status_code >= 500:
            raise Exception("MURF API server error - service temporarily unavailable")
        
        response.raise_for_status()
        data = response.json()
        
        audio_file = data.get("audioFile")
        if not audio_file:
            raise Exception("No audio file in MURF response")
        
        logger.info("MURF TTS successful")
        return audio_file, None
        
    except requests.exceptions.Timeout:
        raise Exception("MURF API timeout - please try again")
    except requests.exceptions.ConnectionError:
        raise Exception("MURF API connection failed - check internet connection")
    except requests.exceptions.RequestException as e:
        raise Exception(f"MURF API request failed: {str(e)}")
    except Exception as e:
        if "Simulated" in str(e):
            raise e
        raise Exception(f"MURF TTS failed: {str(e)}")

# -------------- ROBUST SPEECH TO TEXT (ASSEMBLYAI) ----------------
@handle_errors("Speech recognition temporarily unavailable")
def assemblyai_stt(audio_data, timeout=60):
    """
    Robust STT with comprehensive error handling
    """
    if config.simulate_assemblyai_error:
        logger.info("Simulating AssemblyAI error")
        raise Exception("Simulated AssemblyAI failure")
    
    if not config.assemblyai_api_key:
        logger.error("AssemblyAI API key not configured")
        raise Exception("Speech recognition service not configured")
    
    if not audio_data:
        raise Exception("No audio data provided")
    
    try:
        transcriber = aai.Transcriber()
        
        # Add timeout configuration
        transcript = transcriber.transcribe(audio_data)
        
        if transcript.status == aai.TranscriptStatus.error:
            raise Exception(f"AssemblyAI transcription failed: {transcript.error}")
        
        if not transcript.text or not transcript.text.strip():
            raise Exception("No speech detected in audio")
        
        logger.info(f"AssemblyAI STT successful: {len(transcript.text)} characters")
        return transcript.text, None
        
    except Exception as e:
        if "Simulated" in str(e):
            raise e
        raise Exception(f"Speech recognition failed: {str(e)}")

# -------------- ROBUST LLM (GEMINI) ----------------
@handle_errors("AI assistant temporarily unavailable")
def gemini_llm(prompt, timeout=30):
    """
    Robust LLM with comprehensive error handling
    """
    if config.simulate_gemini_error:
        logger.info("Simulating Gemini API error")
        raise Exception("Simulated Gemini API failure")
    
    if not config.gemini_api_key or not gemini_client:
        logger.error("Gemini API not configured")
        raise Exception("AI assistant service not configured")
    
    if not prompt or not prompt.strip():
        raise Exception("No input provided to AI assistant")
    
    # Truncate prompt if too long
    max_chars = 10000
    if len(prompt) > max_chars:
        prompt = prompt[:max_chars] + "..."
        logger.warning(f"Prompt truncated to {max_chars} characters")
    
    try:
        logger.info(f"Gemini Request: {len(prompt)} characters")
        
        response = gemini_client.models.generate_content(
            model="gemini-2.5-flash", 
            contents=prompt
        )
        
        if not response.text or not response.text.strip():
            raise Exception("Empty response from AI assistant")
        
        logger.info(f"Gemini LLM successful: {len(response.text)} characters")
        return response.text, None
        
    except Exception as e:
        if "Simulated" in str(e):
            raise e
        raise Exception(f"AI assistant failed: {str(e)}")

# -------------- ROBUST ROUTES ----------------

@app.route("/")
def home():
    return render_template("index_robust.html")

@app.route("/api")
def api():
    return render_template("api.html")

@app.route("/original")
def original():
    return render_template("index.html")

@app.route("/health")
def health_check():
    """Health check endpoint to test API availability"""
    health_status = {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "murf": {
                "configured": bool(config.murf_api_key),
                "simulated_error": config.simulate_murf_error
            },
            "assemblyai": {
                "configured": bool(config.assemblyai_api_key),
                "simulated_error": config.simulate_assemblyai_error
            },
            "gemini": {
                "configured": bool(config.gemini_api_key),
                "simulated_error": config.simulate_gemini_error
            }
        }
    }
    return jsonify(health_status)

@app.route("/admin/simulate-error", methods=["POST"])
def simulate_error():
    """Admin endpoint to simulate API errors for testing"""
    data = request.get_json()
    service = data.get("service")
    enabled = data.get("enabled", True)
    
    if service == "murf":
        config.simulate_murf_error = enabled
    elif service == "assemblyai":
        config.simulate_assemblyai_error = enabled
    elif service == "gemini":
        config.simulate_gemini_error = enabled
    else:
        return jsonify({"error": "Invalid service"}), 400
    
    logger.info(f"Error simulation for {service}: {'enabled' if enabled else 'disabled'}")
    return jsonify({"message": f"Error simulation for {service} {'enabled' if enabled else 'disabled'}"})

@app.route("/generate-audio", methods=["POST"])
def generate_audio():
    """Robust audio generation endpoint"""
    try:
        text = request.json.get("text") if request.is_json else request.form.get("text")
        if not text:
            return jsonify({"error": "No text provided"}), 400

        # Try MURF TTS
        result, error = murf_tts(text)
        
        if error:
            logger.warning(f"MURF TTS failed: {error}")
            
            # Try fallback audio
            fallback_audio = generate_fallback_audio(text)
            
            if fallback_audio:
                return jsonify({
                    "audio_url": fallback_audio,
                    "fallback": True,
                    "message": "Using fallback audio service"
                })
            else:
                # Return text-only response
                return jsonify({
                    "error": "Audio generation failed",
                    "text": text,
                    "fallback_message": config.fallback_text_responses["tts_error"],
                    "fallback": True
                }), 200  # 200 because we're providing a fallback

        if request.is_json:
            return jsonify({"audio_url": result})
        return render_template("audio.html", audio_url=result)
        
    except Exception as e:
        logger.error(f"Generate audio error: {e}")
        return jsonify({
            "error": str(e),
            "fallback_message": config.fallback_text_responses["general_error"],
            "fallback": True
        }), 200

@app.route("/tts/echo", methods=["POST"])
def echo_bot():
    """Robust echo bot with comprehensive error handling"""
    try:
        if "audio" not in request.files:
            return jsonify({"error": "No audio file"}), 400

        audio_file = request.files["audio"]
        if not audio_file:
            return jsonify({"error": "Empty audio file"}), 400
            
        audio_bytes = io.BytesIO(audio_file.read())

        # Step 1: Transcribe with AssemblyAI
        transcription, stt_error = assemblyai_stt(audio_bytes)
        
        if stt_error:
            logger.warning(f"STT failed: {stt_error}")
            return jsonify({
                "error": "Speech recognition failed",
                "fallback_message": config.fallback_text_responses["stt_error"],
                "fallback": True
            }), 200

        # Step 2: Convert to AI voice with Murf
        audio_url, tts_error = murf_tts(transcription)
        
        if tts_error:
            logger.warning(f"TTS failed: {tts_error}")
            # Return transcription only
            return jsonify({
                "transcription": transcription,
                "audio_url": None,
                "fallback_message": config.fallback_text_responses["tts_error"],
                "fallback": True
            }), 200

        return jsonify({
            "transcription": transcription,
            "audio_url": audio_url,
            "success": True
        })
        
    except Exception as e:
        logger.error(f"Echo bot error: {e}")
        return jsonify({
            "error": str(e),
            "fallback_message": config.fallback_text_responses["general_error"],
            "fallback": True
        }), 200

@app.route("/llm/query", methods=["POST"])
def llm_query():
    """Robust LLM query with comprehensive error handling"""
    transcription = None
    
    try:
        # Handle audio or text input
        if "audio" in request.files:
            audio_file = request.files["audio"]
            if not audio_file:
                return jsonify({"error": "No audio file provided"}), 400
            
            audio_bytes = io.BytesIO(audio_file.read())
            
            # Step 1: Transcribe audio
            transcription, stt_error = assemblyai_stt(audio_bytes)
            
            if stt_error:
                logger.warning(f"STT failed: {stt_error}")
                return jsonify({
                    "error": "Speech recognition failed",
                    "fallback_message": config.fallback_text_responses["stt_error"],
                    "fallback": True
                }), 200
                
            text = transcription
        else:
            # Handle text input
            payload = request.get_json(force=True)
            text = payload.get("text")
            if not text:
                return jsonify({"error": "No text or audio provided"}), 400

        # Step 2: Send to Gemini LLM
        llm_response, llm_error = gemini_llm(text)
        
        if llm_error:
            logger.warning(f"LLM failed: {llm_error}")
            return jsonify({
                "transcription": transcription,
                "llm_response": None,
                "audio_url": None,
                "error": "AI assistant unavailable",
                "fallback_message": config.fallback_text_responses["llm_error"],
                "fallback": True
            }), 200

        # Step 3: Generate audio from LLM response
        audio_url, tts_error = murf_tts(llm_response)
        
        if tts_error:
            logger.warning(f"TTS failed: {tts_error}")
            # Return text response without audio
            return jsonify({
                "transcription": transcription,
                "llm_response": llm_response,
                "audio_url": None,
                "fallback_message": config.fallback_text_responses["tts_error"],
                "fallback": True
            }), 200

        # Success response
        return jsonify({
            "transcription": transcription,
            "llm_response": llm_response,
            "audio_url": audio_url,
            "success": True
        }), 200
        
    except Exception as e:
        logger.error(f"LLM query error: {e}")
        return jsonify({
            "error": str(e),
            "fallback_message": config.fallback_text_responses["general_error"],
            "fallback": True
        }), 200

# -------------- CHAT SESSION WITH HISTORY (ROBUST) ----------------
def get_or_create_session(session_id):
    """Get existing session or create new one"""
    try:
        if session_id not in chat_sessions:
            chat_sessions[session_id] = {
                "messages": [],
                "created_at": datetime.now(),
                "last_activity": datetime.now()
            }
        else:
            chat_sessions[session_id]["last_activity"] = datetime.now()
        return chat_sessions[session_id]
    except Exception as e:
        logger.error(f"Session management error: {e}")
        raise Exception("Session management failed")

def add_message_to_session(session_id, role, content):
    """Add a message to the session history"""
    try:
        session = get_or_create_session(session_id)
        message = {
            "role": role,  # "user" or "assistant"
            "content": content,
            "timestamp": datetime.now()
        }
        session["messages"].append(message)
        return session
    except Exception as e:
        logger.error(f"Add message error: {e}")
        raise Exception("Failed to save message")

def build_conversation_context(session_id, new_user_message):
    """Build conversation context for LLM including chat history"""
    try:
        session = get_or_create_session(session_id)
        
        # Build conversation string
        conversation = []
        
        # Add previous messages (limit to last 10 for context management)
        recent_messages = session["messages"][-10:] if len(session["messages"]) > 10 else session["messages"]
        
        for msg in recent_messages:
            if msg["role"] == "user":
                conversation.append(f"User: {msg['content']}")
            else:
                conversation.append(f"Assistant: {msg['content']}")
        
        # Add new user message
        conversation.append(f"User: {new_user_message}")
        
        # Join with newlines and add context
        context = "You are a helpful AI assistant. Here is our conversation:\n\n" + "\n".join(conversation)
        
        return context
    except Exception as e:
        logger.error(f"Context building error: {e}")
        raise Exception("Failed to build conversation context")

@app.route("/agent/chat/<session_id>", methods=["POST"])
def agent_chat(session_id):
    """Robust chat endpoint with comprehensive error handling"""
    transcription = None
    
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
        transcription, stt_error = assemblyai_stt(audio_bytes)
        
        if stt_error:
            logger.warning(f"STT failed in chat: {stt_error}")
            return jsonify({
                "session_id": session_id,
                "error": "Speech recognition failed",
                "fallback_message": config.fallback_text_responses["stt_error"],
                "fallback": True
            }), 200
        
        # Step 2: Build conversation context and add to history
        try:
            conversation_context = build_conversation_context(session_id, transcription)
            add_message_to_session(session_id, "user", transcription)
        except Exception as e:
            logger.error(f"Chat history error: {e}")
            # Continue without history
            conversation_context = f"User: {transcription}"
        
        # Step 3: Get LLM response
        llm_response, llm_error = gemini_llm(conversation_context)
        
        if llm_error:
            logger.warning(f"LLM failed in chat: {llm_error}")
            return jsonify({
                "session_id": session_id,
                "transcription": transcription,
                "error": "AI assistant unavailable",
                "fallback_message": config.fallback_text_responses["llm_error"],
                "fallback": True
            }), 200
        
        # Step 4: Save LLM response to history
        try:
            add_message_to_session(session_id, "assistant", llm_response)
        except Exception as e:
            logger.warning(f"Failed to save LLM response: {e}")
            # Continue without saving to history
        
        # Step 5: Generate audio response
        audio_url, tts_error = murf_tts(llm_response)
        
        if tts_error:
            logger.warning(f"TTS failed in chat: {tts_error}")
            # Return text-only response
            session_info = chat_sessions.get(session_id, {})
            return jsonify({
                "session_id": session_id,
                "transcription": transcription,
                "llm_response": llm_response,
                "audio_url": None,
                "message_count": len(session_info.get("messages", [])),
                "fallback_message": config.fallback_text_responses["tts_error"],
                "fallback": True
            }), 200
        
        # Success response
        session_info = chat_sessions[session_id]
        return jsonify({
            "session_id": session_id,
            "transcription": transcription,
            "llm_response": llm_response,
            "audio_url": audio_url,
            "message_count": len(session_info["messages"]),
            "session_created": session_info["created_at"].isoformat(),
            "last_activity": session_info["last_activity"].isoformat(),
            "success": True
        }), 200
        
    except Exception as e:
        logger.error(f"Agent chat error: {e}")
        return jsonify({
            "session_id": session_id,
            "transcription": transcription,
            "error": str(e),
            "fallback_message": config.fallback_text_responses["general_error"],
            "fallback": True
        }), 200

@app.route("/agent/sessions", methods=["GET"])
def list_sessions():
    """List all active chat sessions"""
    try:
        sessions_info = {}
        for session_id, session_data in chat_sessions.items():
            sessions_info[session_id] = {
                "message_count": len(session_data["messages"]),
                "created_at": session_data["created_at"].isoformat(),
                "last_activity": session_data["last_activity"].isoformat()
            }
        return jsonify(sessions_info)
    except Exception as e:
        logger.error(f"List sessions error: {e}")
        return jsonify({"error": "Failed to retrieve sessions"}), 500

@app.route("/agent/session/<session_id>/history", methods=["GET"])
def get_session_history(session_id):
    """Get chat history for a specific session"""
    try:
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
    except Exception as e:
        logger.error(f"Get session history error: {e}")
        return jsonify({"error": "Failed to retrieve session history"}), 500

@app.route("/agent/session/<session_id>", methods=["DELETE"])
def clear_session(session_id):
    """Clear/delete a chat session"""
    try:
        if session_id in chat_sessions:
            del chat_sessions[session_id]
            return jsonify({"message": f"Session {session_id} cleared"})
        else:
            return jsonify({"error": "Session not found"}), 404
    except Exception as e:
        logger.error(f"Clear session error: {e}")
        return jsonify({"error": "Failed to clear session"}), 500

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal server error: {error}")
    return jsonify({
        "error": "Internal server error",
        "fallback_message": config.fallback_text_responses["general_error"]
    }), 500

if __name__ == "__main__":
    logger.info("Starting robust Flask application")
    app.run(debug=True, host='0.0.0.0', port=5000)
