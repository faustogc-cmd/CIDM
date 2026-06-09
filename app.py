import os
import time
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# =====================================================================
# CONFIGURACIÓN DE CREDENCIALES (PROTOCOLO WEB DIRECTO)
# =====================================================================
api_key_env = os.environ.get("GROQ_API_KEY")
CLAVE_RESPALDO = "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"

# Seleccionamos la clave disponible de forma limpia
TOKEN_FINAL = api_key_env.strip() if api_key_env else CLAVE_RESPALDO.strip()

# =====================================================================
# BASE DE CONOCIMIENTO INSTITUCIONAL COMPLETA (CIDM)
# =====================================================================
CONTEXTO_INSTITUCIONAL = """
Eres el asistente virtual oficial del Centro Industrial del Diseño y la Manufactura (CIDM) - SENA Regional Santander.
Tu objetivo es guiar a aspirantes, aprendices y egresados respondiendo de manera clara, cortés, empática y basada estrictamente en la información provista a continuación. Puedes usar HTML básico como <a href='...' target='_blank'>Texto</a> o <b>texto</b>.

## 1. DIRECTORIO CORPORATIVO
* Sede Principal: Kilómetro 6 Autopista A Floridablanca 50-33.
* Teléfonos de Contacto: 6386521 - 6800600.
* Subdirección: Wilson Bastos Delgado (wbastos@sena.edu.co).
* Coordinación Formación Profesional: Johana Carolina Sepulveda Cala (jcsepulveda@sena.edu.co).
* Coordinación Académica: Bertha Patricia Morales (bmoraless@sena.edu.co) y Orlando Colmenares (ocolmenares@sena.edu.co).
* Coordinación Formación Programas Especiales: Javier Diaz Diaz (jdiazd@sena.edu.co).
* Coordinación Administración Educativa: Fausto Ramón Gómez Camargo (frgomez@sena.edu.co).
* Bienestar al Aprendiz: Olga Teresa Rojas Cadena (otrojas@sena.edu.co). Ubicación: Primer piso del bloque administrativo.
* Contrato de Aprendizaje: Luis Martín Cartagena Martinez (lumaca@sena.edu.co).
* Competencias Laborales: Nidia Patricia Lopez Ramirez (nplopez@sena.edu.co).
* Emprendimiento: Ruben Dario Pinto (rdpinto@sena.edu.co).
* Biblioteca: Sonia Milena Ospina (smospinag@sena.edu.co).
* Sistemas - Recursos Tecnológicos: Lubing Oswaldo Contreras Sandoval (locontreras@sena.edu.co).
* Infraestructura: Elmer Alfredo Mejia Viviescas (eamejia@sena.edu.co).
* Atención al Ciudadano Institucional: servicioalciudadano@sena.edu.co

## 2. HORARIOS Y JORNADAS
* Horario de Atención Administrativa: Lunes a viernes de 7:30 a.m. a 12:00 p.m. y de 2:00 p.m. a 6:00 p.m.
* Jornadas de Formación Académica:
  - Mañana: Lunes a Viernes de 6:00 a.m. a 12:00 m.
  - Tarde: Lunes a Viernes de 12:00 m. a 6:00 p.m.
  - Noche: Lunes a Viernes de 6:00 p.m. a 9:45 p.m. y Sábados.

## 3. ADMISIONES Y MATRÍCULAS
* Costos: Todos los servicios y programas son 100% gratuitos y sin intermediarios.
* Simultaneidad: No se pueden cursar dos programas de formación titulada al mismo tiempo. Sí se permiten programas complementarios simultáneos.
* Requisitos de Escolaridad por Nivel:
  - Operario: 5to de primaria aprobado.
  - Técnico: 9no grado aprobado.
  - Tecnólogo: Bachiller (grado 11°) y Pruebas Saber 11 (ICFES).
* Documentación Requerida: Copia legible del documento de identidad (ambas caras), Certificado de EPS activo (SISBEN no es válido), Formato de Compromiso del Aprendiz firmado, y Formato de Tratamiento de datos para menores.

## 4. PROCESO DE CERTIFICACIÓN PARA APRENDICES
* Descripción: Verificación de requisitos académicos y administrativos para generar el título (tarda aprox. 15 días hábiles tras validaciones).
* Paso 1 - Etapa Lectiva: Competencias aprobadas y registradas en SOFIA Plus.
* Paso 2 - Etapa Práctica: Registro y aprobación de alternativa (Contrato de Aprendizaje, Proyecto Productivo, Vinculación Laboral, Pasantía).
* Paso 3 - Seguimiento: Entrega de bitácoras e informes al instructor.
* Paso 4 - Documentación: Copia de documento de identidad, Certificado de la APE, Formato F023, Certificación de alternativa práctica, Formulario de actualización de datos. Tecnólogos requieren Certificado de Pruebas Saber TyT (habilitadas tras aprobar >75% del programa).
* Paso 5 - Plazos y Normativa (Acuerdo 0009 de 2024 que deroga el Acuerdo 007 de 2012): Finalizada la etapa lectiva, hay un plazo máximo estricto para desarrollar y presentar evidencias de etapa productiva. El incumplimiento unjustificado configura causal de deserción y se reporta al comité.
* Paso 6 - Paz y Salvo: Sin obligaciones pendientes con Biblioteca, Bienestar, Almacén, etc.

## 5. CERTIFICACIÓN DE COMPETENCIAS LABORALES
* Objetivo: Certificar conocimientos técnicos/empíricos gratis según Normas de Competencia. Estrategia actual: “Reconstruyendo Futuro 2026” (para víctimas del conflicto) y certificación interna de instructores.

## 6. SERVICIOS Y OFERTA EDUCATIVA
* Modalidades: Titulada, Complementaria (presencial/virtual/mixta), Contrato de Aprendizaje, Certificación de Competencias, Articulación con la Media.
* Áreas de Formación: Cuero, Calzado y Marroquinería; Textil, Confección, Diseño y Moda; Informática, Diseño y Desarrollo de Software; Cultura y Artes Gráficas; Gestión Administrativa y Financiera; Construcción; Materiales e Industrias.

## 7. BIENESTAR AL APRENDIZ
* Ubicación: Primer piso del bloque administrativo (Liderado por Olga Teresa Rojas Cadena).
* Servicios: Salud Integral (atención psicológica), Equidad (apoyos de sostenimiento, transporte, alimentación, monitorías), Cultura (danza, música, teatro), Deporte (torneos, acondicionamiento), Liderazgo (voceros), y Prevención de Deserción.

## 8. RUTAS DE NAVEGACIÓN Y SOFIA PLUS
* Menú Principal del Blog: Inicio, Nosotros, Servicios, Directorio Corporativo, Preguntas Frecuentes, Ofertas.
* En SOFIA Plus: Descarga de certificados, actualización de datos, restablecimiento de contraseña, y juicios de evaluación.
"""

@app.route('/api/chat', methods=['POST'])
def chat():
    # Validación radical del Token
    if not TOKEN_FINAL or "AQUI_PEGA" in TOKEN_FINAL:
        return jsonify({'respuesta': 'Error del sistema: Clave de API no detectada en el código backend.'}), 500

    try:
        data = request.get_json()
        mensaje_usuario = data.get('mensaje', '')

        if not mensaje_usuario:
            return jsonify({'respuesta': 'No se recibió ningún mensaje.'}), 400

        # DIRECCIÓN DE CONEXIÓN DIRECTA (Ignora los proxies de Render)
        url_api = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {TOKEN_FINAL}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "llama3-8b-8192",
            "messages": [
                {"role": "system", "content": CONTEXTO_INSTITUCIONAL},
                {"role": "user", "content": mensaje_usuario}
            ],
            "temperature": 0.3,
            "max_tokens": 650
        }

        # Realizamos la petición HTTP ignorando completamente los proxies internos del entorno
        response = requests.post(url_api, json=payload, headers=headers, proxies={"http": None, "https": None}, timeout=30)
        
        if response.status_code == 200:
            resultado_json = response.json()
            respuesta_ia = resultado_json['choices'][0]['message']['content']
            return jsonify({'respuesta': respuesta_ia})
        else:
            return jsonify({'respuesta': f'Fallo en pasarela Groq (Código {response.status_code}): {response.text}'}), 500

    except Exception as e:
        return jsonify({'respuesta': f'Excepción atrapada en backend: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(port=5000, debug=True)
