import os
import requests
from flask import Flask, request, jsonify
from google import genai

app = Flask(__name__)

# --- CONFIGURACIÓN DE IA ---
# Usamos el modelo que viste en la imagen
GEMINI_API_KEY = "AIzaSyCH4POJYJjAICKXR1v9uv69vf8k5HZgNGQ"
client = genai.Client(api_key=GEMINI_API_KEY)

# --- CONFIGURACIÓN DE WHATSAPP ---
ACCESS_TOKEN = "EAAPHywZC06M8BRLE0cZCfZBwOIUZBfEPn9T2ctEZB1jS8a1mvUX1SAzFIuuhSJDz2ZCcnnOC22RsGHS6iG76Up2ZCLoQBU7mazAs9ZAbjWtKMJzNrwerUj9ndDpwwavP1vxi5G3wiQ9gnwI6v5fjGJBQo19sSTlk6rfEuWH5DH57B9ntvt9OEKAHShxgbeKdSMGucAZDZD"
PHONE_NUMBER_ID = "1016082411589978"

SYSTEM_PROMPT = "Eres Rama, asesor de Vaovao. Vendes madera plástica reciclada. Sé amable y breve. ♻️🪵"

@app.route('/webhook', methods=['GET'])
def verificar_token():
    token = request.args.get('hub.verify_token')
    challenge = request.args.get('hub.challenge')
    if token == "vaovao_token_seguro":
        return challenge
    return "Error", 403

@app.route('/webhook', methods=['POST'])
def recibir_mensajes():
    try:
        body = request.get_json()
        if 'messages' in body['entry'][0]['changes'][0]['value']:
            entry = body['entry'][0]['changes'][0]['value']
            mensaje_texto = entry['messages'][0]['text']['body']
            numero_cliente = entry['messages'][0]['from']
            
            print(f"--- NUEVO MENSAJE: {mensaje_texto} ---")

            # IA piensa usando GEMINI 3 FLASH
            response_ia = client.models.generate_content(
                model="gemini-3-flash", 
                contents=f"{SYSTEM_PROMPT}\nCliente: {mensaje_texto}"
            )
            texto_para_enviar = response_ia.text

            # Enviar a WhatsApp
            url = f"https://graph.facebook.com/v18.0/{PHONE_NUMBER_ID}/messages"
            headers = {"Authorization": f"Bearer {ACCESS_TOKEN}", "Content-Type": "application/json"}
            payload = {
                "messaging_product": "whatsapp",
                "to": numero_cliente,
                "type": "text",
                "text": {"body": texto_para_enviar}
            }
            
            res_meta = requests.post(url, json=payload, headers=headers)
            print(f"Estado Meta: {res_meta.status_code}")

        return jsonify({"status": "ok"}), 200
    except Exception as e:
        print(f"ERROR: {e}")
        return jsonify({"status": "error"}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
