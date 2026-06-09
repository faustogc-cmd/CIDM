import os
import time
from flask import Flask, request, jsonify
from flask_cors import CORS
from groq import Groq

app = Flask(__name__)
CORS(app)

# 1. LEER LA CLAVE DE ENTORNO
api_key_env = os.environ.get("GROQ_API_KEY")

# Limpiamos posibles espacios en blanco invisibles si la clave existe
if api_key_env:
    api_key_env = api_key_env.strip()

# 2. INICIALIZACIÓN COMPROBADA Y ULTRACOMPATIBLE DE GROQ
try:
    if api_key_env:
        # Pasamos explícitamente la clave limpia al constructor
        client = Groq(api_key=api_key_env)
    else:
        # Intentamos inicialización por defecto (Groq busca automáticamente GROQ_API_KEY)
        client = Groq()
except Exception as e:
    client = None
    print(f"--> ERROR CRÍTICO EN GROQ: No se pudo crear el cliente. Motivo: {str(e)}")

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
* Horarios: Lunes a Vigilancia/Atención de Lunes a Viernes de 7:30 AM a 12:00 M y de 1:30 PM a 5:30 PM.
"""

@app.route('/api/chat', methods=['POST'])
def chat():
    # Diagnóstico en tiempo real si el cliente falló
    if client is None:
        return jsonify({
            'respuesta': f'Error de inicialización en el servidor. Estado de la variable de entorno: {"Detectada" if api_key_env else "No detectada (Vacía)"}. Por favor revisa los logs de Render.'
        }), 500

    try:
        data = request.get_json()
        mensaje_usuario = data.get('mensaje', '')

        if not mensaje_usuario:
            return jsonify({'respuesta': 'No se recibió ningún mensaje.'}), 400

        # Llamada al modelo Llama 3
        completion = client.chat.completions.create(
            model="llama3-8b-8192",
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
        return jsonify({'respuesta': f'Error al solicitar respuesta a Llama3: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(port=5000, debug=True)
