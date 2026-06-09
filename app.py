import os
import time
from flask import Flask, request, jsonify
from flask_cors import CORS
from google import genai
from google.genai import types

app = Flask(__name__)
CORS(app)

# 1. LEER LA CLAVE DE FORMA DIRECTA Y PRECISA
api_key_env = os.environ.get("GEMINI_API_KEY")

# Nos aseguramos de limpiar posibles espacios o saltos de línea invisibles si existe la clave
if api_key_env:
    api_key_env = api_key_env.strip()

try:
    # Inicialización estándar según la última documentación de google-genai
    if api_key_env:
        client = genai.Client(api_key=api_key_env)
    else:
        client = None
except Exception as e:
    client = None
    print(f"ERROR CRÍTICO AL INICIALIZAR EL CLIENTE DE GOOGLE: {str(e)}")

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
    # Si la clave de API no se cargó correctamente en el panel de Render
    if not api_key_env:
        return jsonify({'respuesta': 'Error técnico: La variable de entorno GEMINI_API_KEY no está configurada o está vacía en el panel de Render.'}), 500

    if client is None:
        return jsonify({'respuesta': 'Error técnico: No se pudo inicializar el cliente de Google GenAI. Verifica la validez de tu API Key.'}), 500

    try:
        data = request.get_json()
        mensaje_usuario = data.get('mensaje', '')

        if not mensaje_usuario:
            return jsonify({'respuesta': 'No se recibió ningún mensaje.'}), 400

        max_reintentos = 3
        
        for intento in range(max_reintentos):
            try:
                # Usamos el método de generación estándar de contenido
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
        # Esto enviará el mensaje exacto del error de vuelta a Blogger para que lo leas en pantalla
        return jsonify({'respuesta': f'Error en procesamiento interno: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(port=5000, debug=True)
