"""
app.py
------
Flask Web Server for Gemini + Web Search Assistant.

Features:
- Web UI with Flask templates.
- /api/chat endpoint for client interactions.
- Integrates GeminiClient (AI + DuckDuckGo search).
- Clean error handling, JSON responses, and logging.

Author: Osondu Mgbemena
Version: 1.0.0
Date: October 2025
"""

import os
import logging
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from gemini_client import GeminiClient

# -------------------------------------------------------
# Configuration & Logging
# -------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)

# -------------------------------------------------------
# Environment Setup
# -------------------------------------------------------
if not os.getenv("GEMINI_API_KEY"):
    logger.warning("⚠️ GEMINI_API_KEY not found. Please configure it in your .env file.")

app = Flask(__name__, template_folder="../templates", static_folder="../static")
CORS(app)  # Allows cross-origin access for frontend apps

# Initialize AI client
client = GeminiClient()

# -------------------------------------------------------
# Routes
# -------------------------------------------------------

@app.route("/")
def index():
    """Render homepage (basic chat UI)."""
    return render_template("index.html")


@app.route("/api/chat", methods=["POST"])
def chat():
    """Handle chat messages sent from the frontend."""
    payload = request.get_json(silent=True) or {}
    user_message = payload.get("message", "").strip()

    if not user_message:
        logger.warning("Empty message received.")
        return jsonify({"success": False, "error": "No message provided."}), 400

    try:
        response_data = client.generate_response(user_message)

        # In case response is a dict from GeminiClient
        if isinstance(response_data, dict):
            return jsonify({"success": True, "response": response_data.get("response", "")})

        # Fallback (if GeminiClient returned raw string)
        return jsonify({"success": True, "response": response_data})

    except Exception as e:
        logger.error(f"Error generating response: {e}")
        return jsonify({"success": False, "error": "Error generating response."}), 500


# -------------------------------------------------------
# Server Entry Point
# -------------------------------------------------------
if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    debug_mode = os.getenv("DEBUG", "true").lower() == "true"

    logger.info(f"🚀 Starting Flask app on port {port} (debug={debug_mode})")
    app.run(host="0.0.0.0", port=port, debug=debug_mode)

# -------------------------------------------------------
# Developed by: Osondu Mgbemena
# GitHub: https://github.com/Victor-MGB
# LinkedIn: https://www.linkedin.com/in/victor-osondu-1985a7237/
# -------------------------------------------------------
