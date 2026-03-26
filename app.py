import os
import requests
from flask import Flask, request, jsonify
from google import genai

app = Flask(__name__)

# --- CONFIGURACIÓN ---
# Tu API KEY de Google (Gratis)
GEMINI_API_KEY = "AIzaSyCH4POJYJjAICKXR1v9uv69vf8k5HZgNGQ"
client = genai.Client(api_key=GEMINI_API_KEY)

# Datos de WhatsApp
ACCESS_TOKEN = "EAAPHywZC06M8BRLE0cZCfZBwOIUZBfEPn9T2ctEZB1jS8a1mvUX1SAzFIuuhSJDz2ZCcnnOC22RsGHS6iG76Up2ZCLoQBU7mazAs9ZAbjWtKMJzNrwerUj9ndDpwwavP1vxi5G3wiQ9gnwI6v5fjGJBQo19sSTlk6rfEuWH5DH57B9ntvt9OEKAHShxgbeKdSMGucAZDZD"
PHONE_NUMBER_ID = "1016082411589978"

@app.route('/webhook', methods=['GET'])
def verificar():
    if request.args.get('hub.verify_token') == "vaovao_token_seguro":
        return request.args.get('hub.challenge')
    return "Error", 403

@app.route('/webhook', methods=['POST'])
def recibir():
    try:
        data = request.get_json()
        entry = data['entry'][0]['changes'][0]['value']
        
        if 'messages' in entry:
            texto_cliente = entry['messages'][0]['text']['body']
            numero_cliente = entry['messages'][0]['from']
            
            print(f"Mensaje de {numero_cliente}: {texto_cliente}")

            # USAMOS GEMINI 3 FLASH (El de tu captura)
            response = client.models.generate_content(
                model="gemini-3-flash", 
                contents=f"Eres Rama de Vaovao. Responde breve: {texto_cliente}"
            )
            
            # Enviar a WhatsApp
            url = f"https://graph.facebook.com/v18.0/{PHONE_NUMBER_ID}/messages"
            headers = {"Authorization": f"Bearer {ACCESS_TOKEN}", "Content-Type": "application/json"}
            payload = {
                "messaging_product": "whatsapp",
                "to": numero_cliente,
                "type": "text",
                "text": {"body": response.text}
            }
            res = requests.post(url, json=payload, headers=headers)
            print(f"Estado Meta: {res.status_code}")

        return "OK", 200
    except Exception as e:
        print(f"ERROR: {e}")
        return "OK", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
