import os
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Tu API Key debe estar en las variables de entorno de Render
API_KEY = os.environ.get("API_KEY")

# ==================== CAMBIO PRINCIPAL ====================
# REEMPLAZA ESTE URI con el que te dé Google cuando subas tu PDF "programa_gobierno"
URI_PROGRAMA_GOBIERNO = "https://generativelanguage.googleapis.com/v1beta/files/bgo499repak4"  
# Ejemplo: https://generativelanguage.googleapis.com/v1beta/files/abc123def456

# ==================== CACHED CONTENT ====================
# DEBES crear un nuevo CachedContent con SOLO este archivo.
# Instrucción rápida: ve a Google AI Studio → Files → sube el PDF → crea Cached Content con ese archivo
# y pega aquí el "name" que te dé (empieza con cachedContents/...)
CACHED_CONTENT_NAME = "cachedContents/t3urovieuwzla77b9znecslvhdtfvyx34kll3afw"  
# Ejemplo: "cachedContents/xyz789abc123def456"

@app.route('/api/chat', methods=['POST'])
def chat():
    if not API_KEY:
        return jsonify({"error": "Falta configuración del servidor (API KEY)"}), 500

    data = request.json
    user_message = data.get('message', '')
    history = data.get('history', [])

    # Solo 1 archivo ahora
    files_context = [
        {"fileData": {"mimeType": "application/pdf", "fileUri": URI_PROGRAMA_GOBIERNO}}
    ]

    # Instrucción de sistema actualizada (solo 1 documento)
    system_instruction = {
        "parts": [{
            "text": """Eres el asistente de la campaña de Sergio Fajardo. 
            REGLAS:
            1. Responde de forma MUY CORTA y directa (máximo 2 párrafos breves).
            2. Usa tono pedagógico y decente.
            3. Basa tu respuesta SOLO en el documento "Programa de Gobierno" adjunto.
            4. Si preguntan de otro tema, di amablemente que solo manejas el Plan de Gobierno completo de Sergio Fajardo."""
        }]
    }

    current_turn = {
        "role": "user",
        "parts": [{"text": user_message}]
    }

    contents = history + [current_turn]

    payload = {
        "cachedContent": CACHED_CONTENT_NAME,
        "contents": contents,
        "generationConfig": {
            "temperature": 0.1,
            "topP": 0.95
        }
    }

    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={API_KEY}"
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
    return jsonify({"status": "alive", "message": "I'm working!"}), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=port)