import os
import requests
from flask import Flask, request, jsonify
import google.generativeai as genai

app = Flask(__name__)

# 1. CONFIGURACIÓN DE IA (Google Gemini)
genai.configure(api_key="AIzaSyCH4POJYJjAICKXR1v9uv69vf8k5HZgNGQ")
model = genai.GenerativeModel('gemini-pro')

# 2. CONFIGURACIÓN DE WHATSAPP (Meta) - TOKEN ACTUALIZADO
ACCESS_TOKEN = "EAAPHywZC06M8BRDVZBJyLMQ0BDyE57vlJ23EUnCAJ517gA9SWNZCM6aVKTy9KclaJaNC0GppNj811XV3QFRlgRBBZAx3GSXp6hTueUE2AJYLWlf8BGomi1SqZBtrUZBYFD6pcRgMqQfuwP4ByhJ1PPpUGEnLOOoPrWlHAhPhd2kT9XvlLoizsOMnPUAcQHPRgZCRrbGtuKZAgbfbZAa36k7jBGATfU7gOvgpij89w0eVXqqGQnGdwonBlqu4G656xwrEm0xSJJPMOpIgazxjzjZAmyb63ZA"
PHONE_NUMBER_ID = "1016082411589978"

# PERSONALIDAD DE RAMA
SYSTEM_PROMPT = """
Eres Rama, el asistente virtual de Vaovao (www.vaovao.com.ar). 
Asesoras sobre madera plástica 100% reciclada para Decks y Pérgolas.
REGLAS: No es PVC ni WPC. Es eterna y no lleva mantenimiento. 
Si piden precio, solicita nombre, zona y proyecto para que un asesor los contacte.
Usa emojis y sé muy amable. ♻️🪵
"""

@app.route('/webhook', methods=['GET'])
def verificar_token():
    token = request.args.get('hub.verify_token')
    challenge = request.args.get('hub.challenge')
    if token == "vaovao_token_seguro":
        return challenge
    return "Error de token", 403

@app.route('/webhook', methods=['POST'])
def recibir_mensajes():
    try:
        body = request.get_json()
        print(f"--- NUEVO MENSAJE RECIBIDO ---")
        
        # Extraer datos del mensaje
        entry = body['entry'][0]['changes'][0]['value']
        if 'messages' in entry:
            mensaje_texto = entry['messages'][0]['text']['body']
            numero_cliente = entry['messages'][0]['from']
            print(f"Cliente ({numero_cliente}) dijo: {mensaje_texto}")

            # 1. Rama genera la respuesta con IA
            prompt_completo = f"{SYSTEM_PROMPT}\nCliente dice: {mensaje_texto}"
            respuesta_ia = model.generate_content(prompt_completo).text

            # 2. Enviar la respuesta a WhatsApp
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
            
            response = requests.post(url, json=data, headers=headers)
            print(f"Estado del envío a Meta: {response.status_code}")
            if response.status_code != 200:
                print(f"Detalle del error de Meta: {response.text}")

        return jsonify({"status": "ok"}), 200
    except Exception as e:
        print(f"ERROR CRÍTICO: {e}")
        return jsonify({"status": "error"}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
