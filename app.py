import os
import requests
import traceback
from flask import Flask, request
from google import genai

app = Flask(__name__)

# --- CONFIGURACIÓN ---
GEMINI_API_KEY = "AIzaSyDftsxbZN40mh4kkFOBjhPCbEdWNU2qryA"
ACCESS_TOKEN = "EAAPHywZC06M8BRLE0cZCfZBwOIUZBfEPn9T2ctEZB1jS8a1mvUX1SAzFIuuhSJDz2ZCcnnOC22RsGHS6iG76Up2ZCLoQBU7mazAs9ZAbjWtKMJzNrwerUj9ndDpwwavP1vxi5G3wiQ9gnwI6v5fjGJBQo19sSTlk6rfEuWH5DH57B9ntvt9OEKAHShxgbeKdSMGucAZDZD"
PHONE_NUMBER_ID = "1016082411589978"

client = genai.Client(api_key=GEMINI_API_KEY)

SYSTEM_PROMPT = "Eres Rama, asesor de Vaovao. Vendes madera plástica reciclada. Sé amable, claro y breve. ♻️🪵"

# --- VERIFICACIÓN WEBHOOK (Meta) ---
@app.route('/webhook', methods=['GET'])
def verificar():
    if request.args.get('hub.verify_token') == "vaovao_token_seguro":
        return request.args.get('hub.challenge')
    return "Error de validación", 403

# --- RECIBIR MENSAJES ---
@app.route('/webhook', methods=['POST'])
def recibir():
    try:
        data = request.get_json()
        entry = data['entry'][0]['changes'][0]['value']

        if 'messages' in entry:
            mensaje = entry['messages'][0]

            # Solo responder texto
            if mensaje.get('type') != 'text':
                return "OK", 200

            texto_cliente = mensaje['text']['body']
            numero_cliente = mensaje['from']

            print(f"Mensaje de {numero_cliente}: {texto_cliente}")

            # --- GEMINI RESPUESTA (MODELO CORREGIDO) ---
            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=[
                    {
                        "role": "user",
                        "parts": [
                            {"text": f"{SYSTEM_PROMPT}\nCliente: {texto_cliente}"}
                        ]
                    }
                ]
            )

            respuesta_texto = response.text if hasattr(response, "text") else "No pude responder en este momento."

            print(f"Respuesta IA: {respuesta_texto}")

            # --- ENVIAR RESPUESTA A WHATSAPP ---
            url = f"https://graph.facebook.com/v18.0/{PHONE_NUMBER_ID}/messages"

            headers = {
                "Authorization": f"Bearer {ACCESS_TOKEN}",
                "Content-Type": "application/json"
            }

            payload = {
                "messaging_product": "whatsapp",
                "to": numero_cliente,
                "type": "text",
                "text": {
                    "body": respuesta_texto
                }
            }

            res = requests.post(url, json=payload, headers=headers)

            print(f"Estado Meta: {res.status_code}")
            print(res.text)

        return "OK", 200

    except Exception:
        print("ERROR:")
        print(traceback.format_exc())
        return "OK", 200

# --- INICIAR SERVIDOR ---
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
