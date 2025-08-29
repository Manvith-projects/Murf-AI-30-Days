import json
import logging
from flask import Flask, render_template, request, jsonify
from flask_sock import Sock
from services.llm_service import send_mqtt_command

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
sock = Sock(app)

# Device control API (MQTT)
@app.route('/control-device', methods=['POST'])
def control_device():
    data = request.json
    topic = data.get('topic')
    command = data.get('command')
    # Use public Mosquitto broker by default
    mqtt_host = data.get('mqttHost') or "broker.hivemq.com"
    mqtt_port = int(data.get('mqttPort') or 1883)
    mqtt_user = data.get('mqttUser') or None
    mqtt_pass = data.get('mqttPass') or None
    if not topic or not command:
        return jsonify({'success': False, 'error': 'Missing required fields'}), 400
    ok = send_mqtt_command(command, topic, mqtt_host, mqtt_port, mqtt_user, mqtt_pass)
    return jsonify({'success': ok})
import json
import logging
from flask import Flask, render_template
from flask_sock import Sock

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
sock = Sock(app)

@app.route("/")
def index():
    return render_template("index.html")

@sock.route('/transcribe-ws')
def transcribe_ws(ws):
    from assemblyai.streaming.v3 import StreamingClient, StreamingClientOptions, StreamingParameters, StreamingEvents, TurnEvent
    api_keys = {"assembly": None, "gemini": None, "murf": None, "openai": None}
    first_msg = ws.receive()
    try:
        keys = json.loads(first_msg)
        api_keys["assembly"] = keys.get("assemblyKey")
        api_keys["gemini"] = keys.get("geminiKey")
        api_keys["murf"] = keys.get("murfKey")
        api_keys["openai"] = keys.get("openaiKey")
    except Exception:
        api_keys = {"assembly": "none", "gemini": "none", "murf": "none", "openai": "none"}
    client = StreamingClient(StreamingClientOptions(api_key=api_keys["assembly"] or "none", api_host="streaming.assemblyai.com"))
    from services.llm_service import query_llm, maybe_open_in_chrome, search_web_and_enhance_answer
    from services.tts_service import murf_tts
    persona = {
        "role": "system",
        "content": (
            "You are Buzz Lightyear. If asked your name or who you are, always reply 'I am Buzz Lightyear.' "
            "Keep your responses short, direct, and helpful, like a personal assistant. Avoid long role-played speeches."
        )
    }
    chat_history = [persona]
    import re
    transcript_accumulator = {'text': ''}
    streaming_started = {'done': False}
    def is_image_request(text):
        keywords = [r"draw (me|an|a|the)?", r"show (me|an|a|the)?", r"generate (an|a|the)? image", r"create (an|a|the)? image", r"picture of", r"image of", r"visualize", r"illustrate"]
        text = text.lower()
        return any(re.search(kw, text) for kw in keywords)
    def on_turn(self, event: TurnEvent):
        logger.info(f"[WS] {event.transcript} (end_of_turn={event.end_of_turn})")
        # Always send partial transcript for live update
        try:
            ws.send(json.dumps({
                "type": "partial",
                "transcript": event.transcript
            }))
        except Exception as e:
            logger.warning(f"WebSocket send (partial) failed: {e}")
        # Accumulate transcript until end_of_turn
        transcript_accumulator['text'] = event.transcript
        # If end_of_turn, process only the first one per session
        if event.end_of_turn and not streaming_started['done']:
            streaming_started['done'] = True
            try:
                ws.send(json.dumps({
                    "type": "end_of_turn",
                    "transcript": event.transcript
                }))
            except Exception as e:
                logger.warning(f"WebSocket send (end_of_turn) failed: {e}")
            # Save user message to chat history
            chat_history.append({"role": "user", "content": transcript_accumulator['text']})
            user_prompt = transcript_accumulator['text']
            from services.llm_service import maybe_control_esp32_led
            led_feedback = maybe_control_esp32_led(user_prompt)
            tts_text = None
            if led_feedback:
                try:
                    ws.send(json.dumps({
                        "type": "assistant_chunk",
                        "text": led_feedback
                    }))
                    logger.info("Sent LED feedback to client.")
                except Exception as e:
                    logger.warning(f"WebSocket send (LED feedback) failed: {e}")
                tts_text = led_feedback
            elif maybe_open_in_chrome(user_prompt):
                try:
                    ws.send(json.dumps({
                        "type": "web_search_opened"
                    }))
                    logger.info("Sent web_search_opened to client.")
                except Exception as e:
                    logger.warning(f"WebSocket send (web_search_opened) failed: {e}")
                tts_text = "Opened web search in your browser."
            else:
                # If the prompt looks like a question, use web search to enhance answer
                question_words = ("who", "what", "when", "where", "why", "how")
                is_question = user_prompt.strip().endswith("?") or user_prompt.lower().startswith(question_words)
                
                identity_keywords = [
                    "your name", "who are you", "what are you", "identify yourself", "are you buzz", "are you buzz lightyear"
                ]
                if any(kw in user_prompt.lower() for kw in identity_keywords):
                    logger.info("Identity question detected, using persona LLM only.")
                    llm_response = query_llm(chat_history, api_keys["gemini"])
                    logger.info(f"[LLM persona response]: {llm_response}")
                    chat_history.append({"role": "assistant", "content": llm_response})
                    try:
                        ws.send(json.dumps({
                            "type": "assistant_chunk",
                            "text": llm_response
                        }))
                        logger.info("Sent assistant_chunk to client.")
                    except Exception as e:
                        logger.warning(f"WebSocket send (assistant_chunk) failed: {e}")
                    tts_text = llm_response
                elif is_question:
                    logger.info("Getting enhanced answer with web search...")
                    enhanced_answer = search_web_and_enhance_answer(user_prompt, api_keys["gemini"])
                    logger.info(f"[Web-enhanced answer]: {enhanced_answer}")
                    chat_history.append({"role": "assistant", "content": enhanced_answer})
                    try:
                        ws.send(json.dumps({
                            "type": "assistant_chunk",
                            "text": enhanced_answer
                        }))
                        logger.info("Sent assistant_chunk to client.")
                    except Exception as e:
                        logger.warning(f"WebSocket send (assistant_chunk) failed: {e}")
                    tts_text = enhanced_answer
                else:
                    logger.info("Getting full Gemini response...")
                    llm_response = query_llm(chat_history, api_keys["gemini"])
                    logger.info(f"[LLM full response]: {llm_response}")
                    chat_history.append({"role": "assistant", "content": llm_response})
                    try:
                        ws.send(json.dumps({
                            "type": "assistant_chunk",
                            "text": llm_response
                        }))
                        logger.info("Sent assistant_chunk to client.")
                    except Exception as e:
                        logger.warning(f"WebSocket send (assistant_chunk) failed: {e}")
                    tts_text = llm_response
            # Call TTS only if tts_text is set
            if tts_text:
                audio_b64 = murf_tts(tts_text, api_keys["murf"])
                logger.info(f"[Murf audio]: {str(audio_b64)[:30]} ...")
                try:
                    ws.send(json.dumps({
                        "type": "audio_chunk",
                        "audio_b64": audio_b64,
                        "audio_mime": "audio/mpeg"
                    }))
                    logger.info(f"Audio chunk sent to client. Length: {len(audio_b64) if audio_b64 else 0}")
                except Exception as e:
                    logger.warning(f"WebSocket send (audio_chunk) failed: {e}")
                try:
                    ws.send(json.dumps({"type": "audio_done"}))
                    logger.info("Sent audio_done to client.")
                except Exception as e:
                    logger.warning(f"WebSocket send (audio_done) failed: {e}")
                logger.info("Finished streaming all chunks.")

    client.on(StreamingEvents.Turn, on_turn)
    client.connect(StreamingParameters(sample_rate=16000, format_turns=True))
    try:
        while True:
            data = ws.receive()
            if data is None:
                break
            client.stream(data)
    finally:
        client.disconnect(terminate=True)

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host="0.0.0.0", port=port)
