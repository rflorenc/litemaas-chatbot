"""
Main Flask application for the Open Source Mentor Bot.
"""

import os
import logging
from flask import Flask, request, jsonify, render_template_string
from app.litemaas_client import LiteMAASClient
from app.utils import sanitize_input, validate_chat_request

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Initialize LiteMAAS client
litemaas_client = LiteMAASClient(
    base_url=os.getenv('LITEMAAS_BASE_URL', 'https://lite-maas.example/api'),
    api_key=os.getenv('LITEMAAS_API_KEY', 'changeme')
)


# Simple HTML UI template
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Open Source Mentor Bot</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Red Hat Display', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }
        .container {
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            max-width: 800px;
            width: 100%;
            padding: 40px;
        }
        h1 {
            color: #ee0000;
            margin-bottom: 10px;
            font-size: 2.5em;
            display: flex;
            align-items: center;
            gap: 15px;
        }
        .logo {
            width: 50px;
            height: 50px;
            object-fit: contain;
        }
        .subtitle {
            color: #666;
            margin-bottom: 30px;
            font-size: 1.1em;
        }
        .chat-box {
            background: #f8f9fa;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 20px;
            min-height: 300px;
            max-height: 400px;
            overflow-y: auto;
        }
        .message {
            margin-bottom: 15px;
            padding: 10px 15px;
            border-radius: 10px;
            max-width: 80%;
        }
        .user-message {
            background: #667eea;
            color: white;
            margin-left: auto;
            text-align: right;
        }
        .bot-message {
            background: #e9ecef;
            color: #333;
        }
        .input-group {
            display: flex;
            gap: 10px;
        }
        input[type="text"] {
            flex: 1;
            padding: 15px;
            border: 2px solid #ddd;
            border-radius: 10px;
            font-size: 1em;
            transition: border-color 0.3s;
        }
        input[type="text"]:focus {
            outline: none;
            border-color: #667eea;
        }
        button {
            padding: 15px 30px;
            background: #ee0000;
            color: white;
            border: none;
            border-radius: 10px;
            font-size: 1em;
            cursor: pointer;
            transition: background 0.3s;
        }
        button:hover {
            background: #cc0000;
        }
        button:disabled {
            background: #ccc;
            cursor: not-allowed;
        }
        .loading {
            display: none;
            text-align: center;
            padding: 10px;
            color: #667eea;
        }
        .error {
            background: #fee;
            color: #c00;
            padding: 10px;
            border-radius: 5px;
            margin-bottom: 10px;
            display: none;
        }
        .footer {
            margin-top: 20px;
            text-align: center;
            color: #999;
            font-size: 0.9em;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>
            <img src="data:image/png;base64,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" alt="Logo" class="logo">
            Open Source Mentor Bot
        </h1>
        <p class="subtitle">Ask me anything about open source, Red Hat, and community collaboration!</p>

        <div class="error" id="error"></div>

        <div class="chat-box" id="chatBox">
            <div class="message bot-message">
                👋 Hello! I'm your Open Source Mentor Bot. I'm here to help you learn about:
                <ul style="margin-top: 10px;">
                    <li>Open source best practices</li>
                    <li>Red Hat values and culture</li>
                    <li>Community collaboration</li>
                    <li>Getting started with contributions</li>
                </ul>
                What would you like to know?
            </div>
        </div>

        <div class="loading" id="loading">🤔 Thinking...</div>

        <div class="input-group">
            <input type="text" id="userInput" placeholder="Type your question here..."
                   onkeypress="if(event.key==='Enter') sendMessage()">
            <button onclick="sendMessage()" id="sendBtn">Send</button>
        </div>

        <div class="footer">
            Built with ❤️ using Podman, Python, and LiteMAAS |
            Red Hat Open Source Values: Transparency, Automation, Community First
        </div>
    </div>

    <script>
        function sendMessage() {
            const input = document.getElementById('userInput');
            const message = input.value.trim();

            if (!message) return;

            // Add user message to chat
            addMessage(message, 'user');
            input.value = '';

            // Show loading
            document.getElementById('loading').style.display = 'block';
            document.getElementById('sendBtn').disabled = true;
            document.getElementById('error').style.display = 'none';

            // Send to API
            fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ message: message })
            })
            .then(response => response.json())
            .then(data => {
                document.getElementById('loading').style.display = 'none';
                document.getElementById('sendBtn').disabled = false;

                if (data.error) {
                    showError(data.error);
                    addMessage('Sorry, I encountered an error. Please try again.', 'bot');
                } else {
                    addMessage(data.response, 'bot');
                }
            })
            .catch(error => {
                document.getElementById('loading').style.display = 'none';
                document.getElementById('sendBtn').disabled = false;
                showError('Failed to connect to the server: ' + error);
                addMessage('Sorry, I could not process your request. Please try again.', 'bot');
            });
        }

        function addMessage(text, sender) {
            const chatBox = document.getElementById('chatBox');
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${sender}-message`;
            messageDiv.textContent = text;
            chatBox.appendChild(messageDiv);
            chatBox.scrollTop = chatBox.scrollHeight;
        }

        function showError(message) {
            const errorDiv = document.getElementById('error');
            errorDiv.textContent = message;
            errorDiv.style.display = 'block';
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    """Serve the web UI"""
    return render_template_string(HTML_TEMPLATE)


@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'open-source-mentor-bot',
        'version': '1.0.0'
    }), 200


@app.route('/api/chat', methods=['POST'])
def chat():
    """
    Chat endpoint that processes user messages and returns bot responses.

    Expected JSON payload:
    {
        "message": "user's question"
    }

    Returns:
    {
        "response": "bot's answer"
    }
    """
    try:
        # Validate request
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Invalid JSON'}), 400

        validation_error = validate_chat_request(data)
        if validation_error:
            return jsonify({'error': validation_error}), 400

        # Sanitize input
        user_message = sanitize_input(data['message'])

        logger.info(f"Received message: {user_message[:50]}...")

        # Get response from LiteMAAS
        bot_response = litemaas_client.get_completion(user_message)

        logger.info(f"Generated response: {bot_response[:50]}...")

        return jsonify({
            'response': bot_response,
            'status': 'success'
        }), 200

    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}", exc_info=True)
        return jsonify({
            'error': 'Internal server error',
            'status': 'error'
        }), 500


if __name__ == '__main__':
    port = int(os.getenv('PORT', 8080))
    debug = os.getenv('FLASK_ENV') == 'development'

    logger.info(f"Starting Open Source Mentor Bot on port {port}")
    app.run(host='0.0.0.0', port=port, debug=debug)
