import os
import time
from flask import Flask, request, jsonify
from flask_cors import CORS
from google import genai
from google.genai import types

app = Flask(__name__)
CORS(app)

# Intentamos leer la API Key desde el entorno del servidor
api_key_env = os.environ.get("GEMINI_API_KEY")

# Verificación de seguridad en la inicialización del cliente
try:
    if api_key_env:
        client = genai.Client(api_key=api_key_env)
    else:
        # Si no encuentra la variable en Render, busca una configuración local por defecto
        client = genai.Client()
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
    # Verificamos si el cliente de IA se inicializó correctamente
    if client is None:
        return jsonify({'respuesta': 'Error de configuración: La clave de API no está disponible en el servidor.'}), 500

    try:
        data = request.get_json()
        mensaje_usuario = data.get('mensaje', '')

        if not mensaje_usuario:
            return jsonify({'respuesta': 'No se recibió ningún mensaje.'}), 400

        max_reintentos = 3
        
        for intento in range(max_reintentos):
            try:
                # Forzamos el uso del modelo estable de producción gemini-2.5-flash
                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=mensaje_usuario,
                    config=types.GenerateContentConfig(
                        system_instruction=CONTEXTO_INSTITUCIONAL,
                        temperature=0.3 
                    )
                )
                return jsonify({'respuesta': response.text})
            
            except Exception as error_api:
                if '503' in str(error_api) and intento < (max_reintentos - 1):
                    time.sleep(2)
                    continue
                else:
                    raise error_api

    except Exception as e:
        # Añadimos el error técnico detallado al mensaje para saber exactamente qué falla
        return jsonify({'respuesta': f'Error en el procesamiento de la IA. Detalle técnico: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(port=5000, debug=True)
