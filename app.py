import os
import time
from flask import Flask, request, jsonify
from flask_cors import CORS
from groq import Groq

app = Flask(__name__)
CORS(app)

# Leemos la nueva clave desde las variables de entorno de Render
api_key_env = os.environ.get("GROQ_API_KEY")

try:
    if api_key_env:
        # Inicializamos el cliente de Groq para usar Llama 3
        client = Groq(api_key=api_key_env)
    else:
        client = None
except Exception as e:
    client = None

# BASE DE CONOCIMIENTO INSTITUCIONAL
CONTEXTO_INSTITUCIONAL = """
Eres el asistente virtual oficial del Centro Industrial del Diseño y la Manufactura (CIDM).
Tu objetivo es guiar a los usuarios respondiendo de manera clara y cortés basada estrictamente en la información provista.

--- 1. IDENTIDAD INSTITUCIONAL ---
* Nombre oficial: Centro Industrial del Diseño y la Manufactura.
* Ubicación física: Floridablanca, Santander.

--- 2. PROCESOS DE CERTIFICACIÓN ---
* Certificación de Competencias Laborales: Proceso gratuito que reconoce la experiencia.
* Requisitos básicos: Fotocopia del documento de identidad y constancia laboral de mínimo 6 meses.
* Ubicación web: Pestaña superior "Certificación".

--- 3. ADMISIONES E INSCRIPCIONES ---
* Requisitos de ingreso: Técnico (Noveno grado), Tecnólogo (Once grado y pruebas ICFES).
* Ubicación web: Pestaña "Admisiones".

--- 4. DIRECTORIO ---
* Coordinador de Administración Educativa: Ingeniero Fausto Ramón Gómez Camargo.
* Horarios: Lunes a Viernes de 7:30 AM a 12:00 M y de 1:30 PM a 5:30 PM.
"""

@app.route('/api/chat', methods=['POST'])
def chat():
    if not api_key_env:
        return jsonify({'respuesta': 'Error: La variable GROQ_API_KEY no está configurada en Render.'}), 500

    if client is None:
        return jsonify({'respuesta': 'Error: No se pudo inicializar el cliente de Groq.'}), 500

    try:
        data = request.get_json()
        mensaje_usuario = data.get('mensaje', '')

        if not mensaje_usuario:
            return jsonify({'respuesta': 'No se recibió ningún mensaje.'}), 400

        # Llamada al modelo Llama 3 inyectando el rol del sistema y el mensaje del usuario
        completion = client.chat.completions.create(
            model="llama3-8b-8192",  # Modelo ultra rápido y eficiente de Meta
            messages=[
                {"role": "system", "content": CONTEXTO_INSTITUCIONAL},
                {"role": "user", "content": mensaje_usuario}
            ],
            temperature=0.3,
            max_tokens=500
        )
        
        respuesta_ia = completion.choices[0].message.content
        return jsonify({'respuesta': respuesta_ia})

    except Exception as e:
        return jsonify({'respuesta': f'Error en procesamiento interno con Llama3: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(port=5000, debug=True)
