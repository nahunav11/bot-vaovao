import os
import requests
from flask import Flask, request, jsonify
import google.generativeai as genai

app = Flask(__name__)

# 1. CONFIGURACIÓN DE IA (Google Gemini)
# Usamos 'gemini-pro' que es la versión estable compatible con tu librería
genai.configure(api_key="AIzaSyCH4POJYJjAICKXR1v9uv69vf8k5HZgNGQ")
model = genai.GenerativeModel('gemini-1.5-flash-latest')

# 2. CONFIGURACIÓN DE WHATSAPP (Meta) - TOKEN PERMANENTE
ACCESS_TOKEN = "EAAPHywZC06M8BRLE0cZCfZBwOIUZBfEPn9T2ctEZB1jS8a1mvUX1SAzFIuuhSJDz2ZCcnnOC22RsGHS6iG76Up2ZCLoQBU7mazAs9ZAbjWtKMJzNrwerUj9ndDpwwavP1vxi5G3wiQ9gnwI6v5fjGJBQo19sSTlk6rfEuWH5DH57B9ntvt9OEKAHShxgbeKdSMGucAZDZD"
PHONE_NUMBER_ID = "1016082411589978"

# PERSONALIDAD DE RAMA (Modificá esto cuando quieras cambiar cómo responde)
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
    # Este es el "apretón de manos" con Meta
    token = request.args.get('hub.verify_token')
    challenge = request.args.get('hub.challenge')
    if token == "vaovao_token_seguro":
        return challenge
    return "Error de token", 403

@app.route('/webhook', methods=['POST'])
def recibir_mensajes():
    try:
        body = request.get_json()
        
        # Verificamos si es un mensaje de WhatsApp
        entry = body['entry'][0]['changes'][0]['value']
        if 'messages' in entry:
            mensaje_texto = entry['messages'][0]['text']['body']
            numero_cliente = entry['messages'][0]['from']
            
            print(f"--- MENSAJE RECIBIDO ---")
            print(f"Cliente: {numero_cliente} dice: {mensaje_texto}")

            # 1. La IA genera la respuesta
            prompt_ia = f"{SYSTEM_PROMPT}\nCliente dice: {mensaje_texto}"
            respuesta_ia = model.generate_content(prompt_ia).text

            # 2. Enviamos la respuesta a través de Meta
            url = f"https://graph.facebook.com/v18.0/{PHONE_NUMBER_ID}/messages"
            headers = {
                "Authorization": f"Bearer {ACCESS_TOKEN}", 
                "Content-Type": "application/json"
            }
            data = {
                "messaging_product": "whatsapp",
                "to": numero_cliente,
                "type": "text",
                "text": {"body": respuesta_ia}
            }
            
            envio = requests.post(url, json=data, headers=headers)
            print(f"Estado envío Meta: {envio.status_code}")
            if envio.status_code != 200:
                print(f"Error de Meta: {envio.text}")

        return jsonify({"status": "ok"}), 200
    except Exception as e:
        print(f"ERROR: {e}")
        return jsonify({"status": "error"}), 500

if __name__ == "__main__":
    # Render usa el puerto 10000 por defecto
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
