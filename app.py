import os
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

API_KEY = os.environ.get("API_KEY")

# ==================== CONFIGURACIÓN OPTIMIZADA ====================
# 1. Asegúrate de que este URI sea del archivo .txt (mimeType: text/plain)
URI_PROGRAMA_GOBIERNO = "https://generativelanguage.googleapis.com/v1beta/files/wll7t6l4qetm"

# 2. Este caché DEBE haber sido creado usando el modelo gemini-2.5-flash-lite
CACHED_CONTENT_NAME = "cachedContents/22vr05i6scynrrz34wbqqjr9v52gzzckwmwksd5b"

@app.route('/api/chat', methods=['POST'])
def chat():
    if not API_KEY:
        return jsonify({"error": "Falta API KEY"}), 500

    data = request.json
    user_message = data.get('message', '')
    history = data.get('history', [])

    # NOTA: Eliminamos 'files_context' porque ya está incluido en el CACHED_CONTENT_NAME.
    # Esto reduce el tamaño del payload y acelera la respuesta.

    current_turn = {
        "role": "user",
        "parts": [{"text": user_message}]
    }

    # Mantén el historial corto para no perder la ventaja del caché
    contents = history[-4:] + [current_turn] 

    payload = {
        "cachedContent": CACHED_CONTENT_NAME,
        "contents": contents,
        "generationConfig": {
            "temperature": 0.1,
            "topP": 0.95,
            #"maxOutputTokens": 300 # Limitar la salida hace que la respuesta sea más rápida
        }
    }

    try:
        # Usando el endpoint de la versión 2.5-flash-lite
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-lite:generateContent?key={API_KEY}"
        
        response = requests.post(url, json=payload)
        response_data = response.json()

        if "error" in response_data:
            return jsonify({"error": response_data["error"]["message"]}), 500

        bot_reply = response_data["candidates"][0]["content"]["parts"][0]["text"]
        return jsonify({"reply": bot_reply})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "alive"}), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=port)