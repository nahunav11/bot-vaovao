import os
import requests
from flask import Flask, request, jsonify
import google.generativeai as genai

app = Flask(__name__)

# CONFIGURACIÓN DE IA (Tu llave de Google)
genai.configure(api_key="AIzaSyCH4POJYJjAICKXR1v9uv69vf8k5HZgNGQ")
model = genai.GenerativeModel('gemini-1.5-flash')

# PERSONALIDAD DE RAMA
SYSTEM_PROMPT = """
Eres Rama, el asistente virtual de Vaovao (www.vaovao.com.ar). 
Tu objetivo es asesorar sobre madera plástica 100% reciclada para Decks, Revestimientos, Mobiliarios y Pérgolas.

REGLAS DE ORO:
1. MATERIAL: Aclara siempre que NO es PVC ni WPC. Es madera plástica premium, no se pudre, no se deforma y es eterna.
2. CALOR: Explica que tiene una temperatura intermedia entre hormigón y madera. No quema al caminar descalzo y si se moja con agua baja la temperatura al toque.
3. PRECIOS: No des presupuestos. Dile: "Para darte un presupuesto exacto, pasame tu nombre, qué proyecto tenés en mente y en qué zona estás. Un asesor te contactará en menos de 24hs".
4. INSTALACIÓN: Se trabaja igual que la madera (mismas herramientas). Tenemos manual y video instructivo.
5. ENVÍOS: Hacemos envíos a todo el país.
6. TONO: Profesional, amigable, humano y usa algún emoji como ♻️ o 🪵.
"""

# CONFIGURACIÓN DE WHATSAPP (Meta)
# Estos datos los sacarás de Meta Developers más adelante
ACCESS_TOKEN = "TU_TOKEN_DE_META_VA_AQUI"
PHONE_NUMBER_ID = "TU_ID_DE_TELEFONO_VA_AQUI"

@app.route('/webhook', methods=['GET'])
def verificar_token():
    # Esto es para que Meta verifique que tu servidor funciona
    token = request.args.get('hub.verify_token')
    challenge = request.args.get('hub.challenge')
    if token == "vaovao_token_seguro": # Este nombre lo inventamos nosotros
        return challenge
    return "Error de token", 403

@app.route('/webhook', methods=['POST'])
def recibir_mensajes():
    try:
        body = request.get_json()
        entry = body['entry'][0]
        changes = entry['changes'][0]
        value = changes['value']
        
        if 'messages' in value:
            mensaje_texto = value['messages'][0]['text']['body']
            numero_destino = value['messages'][0]['from']

            # 1. Rama genera la respuesta
            prompt_completo = f"{SYSTEM_PROMPT}\nCliente dice: {mensaje_texto}"
            respuesta_ia = model.generate_content(prompt_completo).text

            # 2. Enviar la respuesta a WhatsApp
            url = f"https://graph.facebook.com/v18.0/{PHONE_NUMBER_ID}/messages"
            headers = {"Authorization": f"Bearer {ACCESS_TOKEN}", "Content-Type": "application/json"}
            data = {
                "messaging_product": "whatsapp",
                "to": numero_destino,
                "type": "text",
                "text": {"body": respuesta_ia}
            }
            requests.post(url, json=data, headers=headers)

        return jsonify({"status": "ok"}), 200
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"status": "error"}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
