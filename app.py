import os
import time
from flask import Flask, request, jsonify
from flask_cors import CORS
from google import genai
from google.genai import types

app = Flask(__name__)
CORS(app)

# La clave ahora se lee de las variables de entorno de Render de forma segura
clave_api = os.environ.get("GEMINI_API_KEY")
client = genai.Client()

# BASE DE CONOCIMIENTO INSTITUCIONAL (Reemplace con la información final que generó)
CONTEXTO_INSTITUCIONAL = """
Eres el asistente virtual oficial del Centro Industrial del Diseño y la Manufactura (CIDM).
Tu objetivo es guiar a los usuarios (aspirantes, aprendices y egresados) respondiendo de manera clara, cortés y basada estrictamente en la información provista a continuación. Si te preguntan algo que no está en este documento, sugiere escribir al correo de soporte oficial.

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
    try:
        data = request.get_json()
        mensaje_usuario = data.get('mensaje', '')

        if not mensaje_usuario:
            return jsonify({'respuesta': 'No se recibió ningún mensaje.'}), 400

        max_reintentos = 3
        
        for intento in range(max_reintentos):
            try:
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
        return jsonify({'respuesta': 'En este momento nuestros servidores están experimentando una alta demanda. Por favor, intenta tu consulta nuevamente en unos minutos.'}), 500

if __name__ == '__main__':
    app.run(port=5000, debug=True)