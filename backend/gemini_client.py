"""
gemini_client.py
----------------
A lightweight Gemini AI + Web Search integration module.

Features:
- Supports direct chat and web-enhanced research mode.
- Integrates Google Gemini 2.5 API with DuckDuckGo Search.
- Auto-handles missing keys, search failures, and context building.
- Clean, modular design for use in backend APIs or chatbots.

Author: Osondu Mgbemena
Version: 1.0.0
Date: October 2025
"""

import os
import logging
from typing import List, Dict, Union
from dotenv import load_dotenv
from ddgs import DDGS
import google.generativeai as genai

# Silence gRPC warnings
os.environ["GRPC_VERBOSITY"] = "ERROR"
os.environ["GRPC_LOG_SEVERITY_LEVEL"] = "ERROR"

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)

load_dotenv()

def perform_web_search(query: str, max_results: int = 6) -> List[Dict[str, str]]:
    """Perform a DuckDuckGo search and return a list of results."""
    results: List[Dict[str, str]] = []
    try:
        with DDGS() as ddgs:
            for result in ddgs.text(query, max_results=max_results):
                if not isinstance(result, dict):
                    continue
                title = result.get("title", "")
                href = result.get("href", "")
                body = result.get("body", "")
                if title and href:
                    results.append({"title": title, "href": href, "body": body})
        return results
    except Exception as e:
        logger.error(f"DuckDuckGo search error: {e}")
        return []

class GeminiClient:
    """Manages interaction with Google Gemini API and handles intelligent responses."""

    def __init__(self):
        try:
            api_key = os.getenv("GEMINI_API_KEY")
            if not api_key:
                raise EnvironmentError("❌ GEMINI_API_KEY not found in environment variables.")
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel("models/gemini-2.5-flash")
            self.chat = self.model.start_chat(history=[])
            logger.info("✅ GeminiClient initialized successfully.")
        except Exception as e:
            logger.error(f"Error configuring Gemini API: {e}")
            self.chat = None

    def generate_response(self, user_input: str) -> Union[str, Dict[str, str]]:
        """Generate an AI response with optional web search when prefixed."""
        if not self.chat:
            return "AI service is not configured correctly."

        try:
            text = user_input.strip()
            lower = text.lower()

            # Detect search trigger
            search_query = None
            if lower.startswith("search:"):
                search_query = text.split(":", 1)[1].strip()
            elif lower.startswith("/search "):
                search_query = text.split(" ", 1)[1].strip()

            # Perform search if triggered
            if search_query:
                web_results = perform_web_search(search_query, max_results=6)
                if not web_results:
                    return {"success": False, "response": "Could not retrieve web results."}

                refs_block = "\n\n".join(
                    [f"[{i+1}] {r['title']} — {r['href']}\n{r['body']}" for i, r in enumerate(web_results)]
                )
                system_prompt = (
                    "You are an AI research assistant. Use the provided web results to answer the user query. "
                    "Cite sources inline like [1], [2], and include a concise summary."
                )
                composed = (
                    f"<system>\n{system_prompt}\n</system>\n"
                    f"<user_query>\n{search_query}\n</user_query>\n"
                    f"<web_results>\n{refs_block}\n</web_results>"
                )

                response = self.chat.send_message(composed)
                return {"success": True, "mode": "web_search", "query": search_query, "response": response.text.strip()}

            # Default chat
            response = self.chat.send_message(text)
            return {"success": True, "mode": "chat", "response": response.text.strip()}
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return {"success": False, "response": "An error occurred while processing your request."}


if __name__ == "__main__":
    client = GeminiClient()
    logger.info("💬 Gemini Client ready. Type 'exit' to quit.\n")
    while True:
        user_input = input("You: ")
        if user_input.lower() in ["exit", "quit"]:
            break
        result = client.generate_response(user_input)
        print("\nGemini:", result["response"] if isinstance(result, dict) else result, "\n")

# -------------------------------------------------------
# Developed by: Osondu Mgbemena
# GitHub: https://github.com/Victor-MGB
# LinkedIn: https://www.linkedin.com/in/victor-osondu-1985a7237/
# -------------------------------------------------------
