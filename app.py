import os
import time
from flask import Flask, request, jsonify
from flask_cors import CORS
from groq import Groq

app = Flask(__name__)
CORS(app)

# =====================================================================
# PARCHE DE COMPATIBILIDAD PARA RENDER
# Eliminamos las variables de proxy que confunden a la librería de Groq
# =====================================================================
os.environ.pop('HTTP_PROXY', None)
os.environ.pop('HTTPS_PROXY', None)
os.environ.pop('http_proxy', None)
os.environ.pop('https_proxy', None)

# Leer la clave de entorno limpia de Render
api_key_env = os.environ.get("GROQ_API_KEY")
if api_key_env:
    api_key_env = api_key_env.strip()

# Inicialización segura del cliente
try:
    if api_key_env:
        client = Groq(api_key=api_key_env)
    else:
        client = Groq()
except Exception as e:
    client = None
    print(f"--> ERROR CRÍTICO EN GROQ: No se pudo crear el cliente. Motivo: {str(e)}")

# =====================================================================
# BASE DE CONOCIMIENTO INSTITUCIONAL COMPLETA (CIDM)
# =====================================================================
CONTEXTO_INSTITUCIONAL = """
Eres el asistente virtual oficial del Centro Industrial del Diseño y la Manufactura (CIDM) - SENA Regional Santander.
Tu objetivo es guiar a aspirantes, aprendices y egresados respondiendo de manera clara, cortés, empática y basada estrictamente en la información provista a continuación. Puedes usar etiquetas HTML básicas como enlaces (<a href='...' target='_blank'>Texto</a>) o negritas (<b>texto</b>) para estructurar tus respuestas y hacerlas legibles. Si te preguntan algo que no está aquí, indica amablemente que no dispones de ese dato exacto y sugiéreles contactar a Atención al Ciudadano o revisar el directorio corporativo.

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
* Paso 5 - Plazos y Normativa (Acuerdo 0009 de 2024 que deroga el Acuerdo 007 de 2012): Finalizada la etapa lectiva, hay un plazo máximo estricto para desarrollar y presentar evidencias de etapa productiva. El incumplimiento injustificado configura causal de deserción y se reporta al comité.
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
    if client is None:
        return jsonify({
            'respuesta': 'Error de inicialización: El cliente de Groq no se pudo crear debido al conflicto de red de Render.'
        }), 500

    try:
        data = request.get_json()
        mensaje_usuario = data.get('mensaje', '')

        if not mensaje_usuario:
            return jsonify({'respuesta': 'No se recibió ningún mensaje.'}), 400

        # Petición al modelo Llama 3 con el nuevo contexto expandido
        completion = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[
                {"role": "system", "content": CONTEXTO_INSTITUCIONAL},
                {"role": "user", "content": mensaje_usuario}
            ],
            temperature=0.3,
            max_tokens=650  # Ampliado ligeramente para permitir respuestas detalladas
        )
        
        respuesta_ia = completion.choices[0].message.content
        return jsonify({'respuesta': respuesta_ia})

    except Exception as e:
        return jsonify({'respuesta': f'Error al solicitar respuesta a Llama3: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(port=5000, debug=True)
