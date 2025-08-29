from bs4 import BeautifulSoup

def search_web_and_enhance_answer(query: str) -> str:
    """
    Search the web for the query, extract a summary, and enhance the LLM answer with web info.
    """
    try:
        # Use DuckDuckGo for scraping-friendly search
        search_url = f"https://html.duckduckgo.com/html/?q={requests.utils.quote(query)}"
        resp = requests.get(search_url, timeout=5, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(resp.text, "html.parser")
        results = soup.find_all('a', class_='result__a', limit=3)
        snippets = []
        for a in results:
            snippet = a.get_text(strip=True)
            if snippet:
                snippets.append(snippet)
        web_summary = " | ".join(snippets) if snippets else "(No web summary found)"
    except Exception as e:
        web_summary = f"(Web search failed: {e})"

    # Enhance LLM answer with web info
    llm_prompt = f"User question: {query}\nWeb search summary: {web_summary}\nAnswer the user's question, using the web info if helpful:"
    answer = query_llm(llm_prompt)
    return answer or f"Web info: {web_summary}"
import requests

# Set your ESP32 IP address here
ESP32_IP = "192.168.31.241"  # <-- CHANGE THIS to your ESP32's IP

def maybe_control_esp32_led(user_prompt: str) -> str | None:
    """
    If the user prompt is a home automation command, send HTTP request to ESP32 and return feedback string.
    """
    prompt = user_prompt.lower()
    print(f"[maybe_control_esp32_led] Called with prompt: {prompt}")
    import re
    # Regex for any combination of (turn|switch) (on|off) (the)? (led|light)
    on_patterns = [
        r"(turn|switch) (on) (the )?(led|light)",
        r"(led|light) (on)",
        r"(on) (led|light)"
    ]
    off_patterns = [
        r"(turn|switch) (off) (the )?(led|light)",
        r"(led|light) (off)",
        r"(off) (led|light)"
    ]
    if any(re.search(p, prompt) for p in on_patterns):
        print("[maybe_control_esp32_led] Detected ON command, sending request...")
        try:
            url = f"http://{ESP32_IP}/led/on"
            print(f"[maybe_control_esp32_led] Requesting: {url}")
            r = requests.get(url, timeout=2)
            print(f"[maybe_control_esp32_led] Response status: {r.status_code}")
            if r.status_code == 200:
                print("[maybe_control_esp32_led] LED turned on!")
                return "LED turned on!"
            else:
                print("[maybe_control_esp32_led] ESP32 error on ON")
                return "Failed to turn on LED (ESP32 error)"
        except Exception as e:
            print(f"[maybe_control_esp32_led] Exception: {e}")
            return f"Failed to turn on LED: {e}"
    if any(re.search(p, prompt) for p in off_patterns):
        print("[maybe_control_esp32_led] Detected OFF command, sending request...")
        try:
            url = f"http://{ESP32_IP}/led/off"
            print(f"[maybe_control_esp32_led] Requesting: {url}")
            r = requests.get(url, timeout=2)
            print(f"[maybe_control_esp32_led] Response status: {r.status_code}")
            if r.status_code == 200:
                print("[maybe_control_esp32_led] LED turned off!")
                return "LED turned off!"
            else:
                print("[maybe_control_esp32_led] ESP32 error on OFF")
                return "Failed to turn off LED (ESP32 error)"
        except Exception as e:
            print(f"[maybe_control_esp32_led] Exception: {e}")
            return f"Failed to turn off LED: {e}"
    print("[maybe_control_esp32_led] No LED command detected.")
    return None
import webbrowser
import re


def maybe_open_in_chrome(user_prompt: str) -> bool:
    """
    If the user prompt looks like a web search/news/info request, open it in Chrome and return True. Otherwise, return False.
    """
    # Simple heuristic: look for keywords
    search_keywords = [
        r"search for ",
        r"google ",
        r"look up ",
        r"latest news",
        r"wikipedia ",
        r"find ",
        r"open (the )?website",
        r"show me (the )?news",
        r"who won",
        r"what happened",
        r"current events",
        r"Open"
    ]
    import logging
    print(f"[maybe_open_in_chrome] Called with prompt: {user_prompt}")
    prompt = user_prompt.lower().strip()
    # Direct site redirects
    site_map = {
        "youtube": "https://www.youtube.com",
        "github": "https://www.github.com",
        "wikipedia": "https://www.wikipedia.org",
        "gmail": "https://mail.google.com",
        "google drive": "https://drive.google.com",
        "reddit": "https://www.reddit.com",
        "twitter": "https://twitter.com",
        "facebook": "https://facebook.com",
        "instagram": "https://instagram.com"
    }
    for key, url in site_map.items():
        if f"open {key}" in prompt or f"open {key} website" in prompt:
            print(f"[maybe_open_in_chrome] Directly opening {key}: {url}")
            try:
                webbrowser.open_new_tab(url)
                print("[maybe_open_in_chrome] Browser open command issued.")
            except Exception as e:
                print(f"[maybe_open_in_chrome] Failed to open browser: {e}")
            return True
    # Fallback: Google search
    search_keywords = [
        "search for",
        "google",
        "look up",
        "latest news",
        "find",
        "show me the news",
        "who won",
        "what happened",
        "current events"
    ]
    matched = False
    for kw in search_keywords:
        if kw in prompt:
            matched = True
            break
    if matched:
        query = user_prompt
        for kw in search_keywords:
            query = query.replace(kw, '', 1)
        url = f'https://www.google.com/search?q={query.strip().replace(" ", "+")}'
        print(f"[maybe_open_in_chrome] Attempting to open URL: {url}")
        try:
            webbrowser.open_new_tab(url)
            print("[maybe_open_in_chrome] Browser open command issued.")
        except Exception as e:
            print(f"[maybe_open_in_chrome] Failed to open browser: {e}")
        return True
    return False
import openai

def generate_dalle_image(prompt: str, openai_api_key: str) -> str | None:
    """
    Generate an image using OpenAI DALL·E API. Returns the image URL.
    """
    try:
        openai.api_key = openai_api_key
        response = openai.Image.create(
            prompt=prompt,
            n=1,
            size="512x512",
            model="dall-e-3"
        )
        if response and 'data' in response and len(response['data']) > 0:
            return response['data'][0]['url']
        return None
    except Exception as e:
        logger.error(f"DALL·E Image Generation Error: {e}")
        return None
def stream_llm_response_chunks(text: str, chunk_size: int = 20):
    """
    Simulate streaming Gemini response by splitting the response into chunks of N words.
    Accepts either a string or a list of chat messages.
    """
    if isinstance(text, list):
        # Concatenate all user and assistant messages for context
        prompt = '\n'.join([msg['content'] for msg in text])
    else:
        prompt = text
    full_response = query_llm(prompt)
    if not full_response:
        return
    words = full_response.split()
    for i in range(0, len(words), chunk_size):
        yield ' '.join(words[i:i+chunk_size])


import os
from dotenv import load_dotenv
load_dotenv()
import logging
logger = logging.getLogger(__name__)

from google import genai
def query_llm(text: str, gemini_api_key: str) -> str | None:
    try:
        # If text is a list (chat history), concatenate all messages
        if isinstance(text, list):
            prompt = '\n'.join([msg['content'] for msg in text if 'content' in msg])
        else:
            prompt = str(text)
        gemini_client = genai.Client(api_key=gemini_api_key)
        response = gemini_client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        return response.text
    except Exception as e:
        logger.error(f"Gemini LLM Error: {e}")
        return None
