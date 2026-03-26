import os
import requests
from flask import Flask, request, jsonify
from google import genai

app = Flask(__name__)

# --- 1. CONFIGURACIÓN DE IA (GOOGLE GEMINI) ---
# Usamos tu API KEY directamente para evitar errores de lectura
GEMINI_API_KEY = "AIzaSyCH4POJYJjAICKXR1v9uv69vf8k5HZgNGQ"
client = genai.Client(api_key=GEMINI_API_KEY)

# --- 2. CONFIGURACIÓN DE WHATSAPP (META) ---
# Tu Token Permanente y el ID de tu número de Vaovao
ACCESS_TOKEN = "EAAPHywZC06M8BRLE0cZCfZBwOIUZBfEPn9T2ctEZB1jS8a1mvUX1SAzFIuuhSJDz2ZCcnnOC22RsGHS6iG76Up2ZCLoQBU7mazAs9ZAbjWtKMJzNrwerUj9ndDpwwavP1vxi5G3wiQ9gnwI6v5fjGJBQo19sSTlk6rfEuWH5DH57B9ntvt9OEKAHShxgbeKdSMGucAZDZD"
PHONE_NUMBER_ID = "1016082411589978"

# PERSONALIDAD DE RAMA
SYSTEM_PROMPT = """
Eres Rama, el asistente virtual de Vaovao (www.vaovao.com.ar). 
Asesoras sobre madera plástica 100% reciclada para Decks y Pérgolas.
REGLAS: 
- El material NO es PVC ni WPC, es plástico reciclado puro. 
- Es eterna y no lleva mantenimiento (no se pinta, no se pudre). 
- Si piden presupuesto, pedí nombre, zona y qué proyecto quieren hacer.
- Sé muy amable y usa emojis. ♻️🪵
"""

@app.route('/webhook', methods=['GET'])
def verificar_token():
    # El "apretón de manos" con Meta para validar el Webhook
    token = request.args.get('hub.verify_token')
    challenge = request.args.get('hub.challenge')
    if token == "vaovao_token_seguro":
        return challenge
    return "Error de token", 403

@app.route('/webhook', methods=['POST'])
def recibir_mensajes():
    try:
        body = request.get_json()
        
        # Verificamos si el JSON tiene un mensaje de texto
        entry = body['entry'][0]['changes'][0]['value']
        if 'messages' in entry:
            mensaje_texto = entry['messages'][0]['text']['body']
            numero_cliente = entry['messages'][0]['from']
            
            print(f"--- NUEVO MENSAJE: {mensaje_texto} (de {numero_cliente}) ---")

            # 1. Rama genera la respuesta usando Gemini 1.5 Flash
            response_ia = client.models.generate_content(
                model="gemini-1.5-flash", 
                contents=f"{SYSTEM_PROMPT}\nCliente dice: {mensaje_texto}"
            )
            texto_respuesta = response_ia.text

            # 2. Enviamos la respuesta de vuelta a WhatsApp
            url = f"https://graph.facebook.com/v18.0/{PHONE_NUMBER_ID}/messages"
            headers = {
                "Authorization": f"Bearer {ACCESS_TOKEN}", 
                "Content-Type": "application/json"
            }
            payload = {
                "messaging_product": "whatsapp",
                "to": numero_cliente,
                "type": "text",
                "text": {"body": texto_respuesta}
            }
            
            respuesta_meta = requests.post(url, json=payload, headers=headers)
            print(f"Estado envío Meta: {respuesta_meta.status_code}")

        return jsonify({"status": "ok"}), 200
    except Exception as e:
        print(f"ERROR CRÍTICO: {e}")
        return jsonify({"status": "error"}), 500

if __name__ == "__main__":
    # Render usa el puerto 10000 por defecto
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
