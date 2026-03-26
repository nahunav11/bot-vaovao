import os
import requests
import traceback
from flask import Flask, request

app = Flask(__name__)

ACCESS_TOKEN = "EAAPHywZC06M8BRLE0cZCfZBwOIUZBfEPn9T2ctEZB1jS8a1mvUX1SAzFIuuhSJDz2ZCcnnOC22RsGHS6iG76Up2ZCLoQBU7mazAs9ZAbjWtKMJzNrwerUj9ndDpwwavP1vxi5G3wiQ9gnwI6v5fjGJBQo19sSTlk6rfEuWH5DH57B9ntvt9OEKAHShxgbeKdSMGucAZDZD"
PHONE_NUMBER_ID = "1073112645888097"

# --- MOTOR "TIPO IA" ---
def generar_respuesta(texto):
    texto = texto.lower()

    # SALUDO
    if any(p in texto for p in ["hola", "buenas", "buen día", "buenas tardes"]):
        return "Hola 👋 Soy Rama de Vaovao ♻️\n\nTrabajamos con madera plástica reciclada.\n\n¿Estás buscando precios, productos o asesoramiento?"

    # PRODUCTOS
    elif any(p in texto for p in ["producto", "que venden", "que hacen", "madera", "deck"]):
        return "Trabajamos con:\n\n• Decks para exterior\n• Revestimientos\n• Mobiliario\n\nTodo en madera plástica reciclada ♻️\n\n¿Para qué lo querés usar?"

    # PRECIOS
    elif any(p in texto for p in ["precio", "cuanto sale", "cuánto cuesta", "valor"]):
        return "Los precios varían según medida y cantidad 👇\n\nSi querés decime:\n• qué producto buscás\n• medidas aproximadas\n\nY te paso un estimado 👍"

    # USO / NECESIDAD
    elif any(p in texto for p in ["patio", "jardin", "pileta", "balcon", "terraza"]):
        return "Perfecto 👌 para ese uso la madera plástica es ideal porque:\n\n✔️ No se pudre\n✔️ No lleva mantenimiento\n✔️ Resiste agua y sol\n\n¿Querés que te pase opciones y precios?"

    # UBICACIÓN
    elif any(p in texto for p in ["donde estan", "ubicacion", "dónde están"]):
        return "Estamos en Buenos Aires 📍\n\nHacemos envíos a todo el país 🚚"

    # ENVÍOS
    elif any(p in texto for p in ["envio", "envían", "envios"]):
        return "Sí, hacemos envíos 🚚\n\nDecime tu zona y te digo costo y tiempos 👍"

    # COMPRA / INTERÉS
    elif any(p in texto for p in ["quiero", "me interesa", "comprar"]):
        return "Buenísimo 🙌\n\nDecime:\n• qué producto querés\n• medidas aproximadas\n\nY te paso precio y disponibilidad 👍"

    # MEDIDAS
    elif any(p in texto for p in ["metros", "medidas", "m2", "m²"]):
        return "Perfecto 👌 con esas medidas te puedo calcular un estimado.\n\n¿Es para deck o revestimiento?"

    # AGRADECIMIENTO
    elif "gracias" in texto:
        return "Gracias a vos 🙌\n\nCualquier duda estoy para ayudarte."

    # FALLBACK (parece IA)
    else:
        return "Te ayudo con eso 👍\n\n¿Estás buscando precios, productos o asesoramiento sobre madera plástica?"

# --- VERIFICACIÓN META ---
@app.route('/webhook', methods=['GET'])
def verificar():
    if request.args.get('hub.verify_token') == "vaovao_token_seguro":
        return request.args.get('hub.challenge')
    return "Error", 403

# --- MENSAJES ---
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

            print(f"Cliente: {texto_cliente}")

            respuesta_texto = generar_respuesta(texto_cliente)

            url = f"https://graph.facebook.com/v18.0/{PHONE_NUMBER_ID}/messages"

            headers = {
                "Authorization": f"Bearer {ACCESS_TOKEN}",
                "Content-Type": "application/json"
            }

            payload = {
                "messaging_product": "whatsapp",
                "to": numero_cliente,
                "type": "text",
                "text": {"body": respuesta_texto}
            }

            res = requests.post(url, json=payload, headers=headers)

            print(res.status_code, res.text)

        return "OK", 200

    except Exception:
        print(traceback.format_exc())
        return "OK", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
