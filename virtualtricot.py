import streamlit as st
import random
import pandas as pd
import os
from datetime import datetime
from supabase import create_client, Client


# Configurar Supabase
SUPABASE_URL = "https://dxgbqtpkjsptwrjdwkpv.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImR4Z2JxdHBranNwdHdyamR3a3B2Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzgyNDcyNzcsImV4cCI6MjA1MzgyMzI3N30.3kpgYBPsBXRZZkNDDa7xIQE5l3ap_hFRZIC1UhGcBv0"  # Usa una clave actualizada
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Configuración inicial de la app
st.set_page_config(page_title="Encuesta de Preferencia de Yuca", layout="wide")

# Título y descripción
st.title("ENCUESTA DE PREFERENCIA SOBRE NUEVAS VARIEDADES DE YUCA PARA EL CARIBE")
st.write("""
**Estimado productor,**
El propósito de esta encuesta es conocer su interés en algunos de los nuevos conceptos de productos de semillas de yuca mejoradas para el Caribe. 
A lo largo de esta breve actividad, le mostraremos videos que describen 3 o 4 productos de yuca, y le pedimos que escuche con atención las explicaciones detalladas de cada uno.

Después de ver estos videos, le solicitaremos que clasifique los productos en orden de preferencia, comenzando por el que más le gustaría adquirir en el futuro. 
Su opinión es fundamental para ayudarnos a mejorar y adaptar nuestras variedades a las necesidades de los productores como usted.
""")

# Capturar la fecha de la encuesta
fecha_encuesta = datetime.today().strftime('%Y-%m-%d %H:%M:%S')

# Preguntas sobre el encuestado
nombre = st.text_input("📝 Nombre del encuestado", key="nombre")
ubicacion = st.text_input("📍 Ubicación (Departamento, Municipio, Vereda)", key="ubicacion")
tipo_productor = st.radio("🍠 ¿Qué tipo de yuca produce?", ["Dulce", "Amarga"], key="tipo_productor")
variedad_actual = st.text_input("🌱 ¿Qué variedad de yuca siembra actualmente?", key="variedad_actual")

# Lista de videos en YouTube con títulos descriptivos
video_links = {
    "INGLES DOBLE PROPÓSITO": "https://www.youtube.com/watch?v=eXtC8unIYSc",
    "INGLES LA AMARILLA": "https://www.youtube.com/watch?v=fw9ixpas2wo",
    "INGLES LA DURADERA": "https://www.youtube.com/watch?v=fc0Sdb21OJY",
    "INGLES LA PREMATURA": "https://www.youtube.com/watch?v=cMQwb8CRP2A",
    "INGLES LA RAPIDITA": "https://www.youtube.com/watch?v=Wybqmn-7wq4",
    "INGLES LA RENDIDORA": "https://www.youtube.com/watch?v=7SJzezYYWms",
    "INGLES SUPER INDUSTRIAL": "https://www.youtube.com/watch?v=79fuHech2dI"
}

# Seleccionar 3 videos aleatorios
if "selected_videos" not in st.session_state:
    st.session_state.selected_videos = random.sample(list(video_links.items()), 3)  # Seleccionar 3 al azar

selected_videos = st.session_state.selected_videos  # Recuperar videos aleatorios en la sesión

# Mostrar los 3 videos desde YouTube con nombres formateados
st.subheader("🎥 Por favor, vea los siguientes videos antes de responder:")
video_labels = {}  # Diccionario para mapear enlaces con nombres limpios

for title, url in selected_videos:
    clean_title = title.replace("INGLES ", "")  # Quitar la palabra 'INGLES'
    st.video(url)
    video_labels[url] = clean_title  # Guardar el título limpio asociado al URL

# Preguntas sobre preferencia de variedades usando los nombres limpios
st.subheader("📊 Clasificación de Preferencia")

fav_video = st.radio("✅ ¿Cuál concepto de variedad le gustó más?", list(video_labels.values()), key="fav", index=None)
least_fav_video = st.radio("👎🏼 ¿Cuál concepto de variedad le gustó menos?", list(video_labels.values()), key="least_fav", index=None)

# Validación para evitar que elijan el mismo video como el favorito y el menos favorito
if fav_video and least_fav_video and fav_video == least_fav_video:
    st.warning("⚠️ La opción que más le gustó y la que menos le gustó no pueden ser la misma. Seleccione opciones diferentes.")

# Función para guardar respuestas en Supabase
def guardar_respuesta():
    # Extraer solo las URLs de los videos seleccionados
    video_urls = [video[1] for video in selected_videos]  # Extrae solo las URLs
    
    data = {
        "fecha_encuesta": fecha_encuesta,
        "nombre": st.session_state.nombre,
        "ubicacion": st.session_state.ubicacion,
        "tipo_productor": st.session_state.tipo_productor,
        "variedad_actual": st.session_state.variedad_actual,
        "video_1": video_labels[video_urls[0]],  # Usa la URL como clave
        "video_2": video_labels[video_urls[1]],  
        "video_3": video_labels[video_urls[2]],  
        "me_gusto_mas": fav_video,
        "me_gusto_menos": least_fav_video
    }
    
    response = supabase.table("encuesta_yuca").insert(data).execute()

    if response.data:
        st.success("✅ ¡Gracias por participar! Su respuesta ha sido guardada en Supabase.")
    else:
        st.error("⚠️ Hubo un problema guardando su respuesta en la base de datos.")

# Botón para enviar respuestas
if st.button("Enviar respuestas"):
    if fav_video and least_fav_video and nombre and ubicacion and tipo_productor and variedad_actual:
        if fav_video != least_fav_video:
            guardar_respuesta()
            st.session_state.clear()  # Limpiar la sesión después de enviar la respuesta
        else:
            st.warning("⚠️ La opción que más le gustó y la que menos le gustó no pueden ser la misma.")
    else:
        st.warning("⚠️ Por favor, complete todos los campos antes de enviar.")
