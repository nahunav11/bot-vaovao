import os
import requests
import traceback
from flask import Flask, request
from google import genai

app = Flask(__name__)

# --- PEGÁ TUS CLAVES ACÁ ---
GEMINI_API_KEY = "AIzaSyCH4POJYJjAICKXR1v9uv69vf8k5HZgNGQ"
ACCESS_TOKEN = "EAAPHywZC06M8BRLE0cZCfZBwOIUZBfEPn9T2ctEZB1jS8a1mvUX1SAzFIuuhSJDz2ZCcnnOC22RsGHS6iG76Up2ZCLoQBU7mazAs9ZAbjWtKMJzNrwerUj9ndDpwwavP1vxi5G3wiQ9gnwI6v5fjGJBQo19sSTlk6rfEuWH5DH57B9ntvt9OEKAHShxgbeKdSMGucAZDZD"
PHONE_NUMBER_ID = "1016082411589978"

client = genai.Client(api_key=GEMINI_API_KEY)

SYSTEM_PROMPT = "Eres Rama, asesor de Vaovao. Vendes madera plástica reciclada. Sé amable, claro y breve. ♻️🪵"

@app.route('/webhook', methods=['GET'])
def verificar():
    if request.args.get('hub.verify_token') == "vaovao_token_seguro":
        return request.args.get('hub.challenge')
    return "Error de validación", 403

@app.route('/webhook', methods=['POST'])
def recibir():
    try:
        data = request.get_json()
        entry = data['entry'][0]['changes'][0]['value']

        if 'messages' in entry:
            mensaje = entry['messages'][0]

            if mensaje.get('type') != 'text':
                return "OK", 200

            texto_cliente = mensaje['text']['body']
            numero_cliente = mensaje['from']

            print(f"Mensaje de {numero_cliente}: {texto_cliente}")

            response = client.models.generate_content(
                model="gemini-3-flash",
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
        print(traceback.format_exc())
        return "OK", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
    
    
