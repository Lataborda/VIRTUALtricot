import streamlit as st
import random
import os
from datetime import datetime
from supabase import create_client, Client

# Configurar Supabase
SUPABASE_URL = "https://dxgbqtpkjsptwrjdwkpv.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImR4Z2JxdHBranNwdHdyamR3a3B2Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzgyNDcyNzcsImV4cCI6MjA1MzgyMzI3N30.3kpgYBPsBXRZZkNDDa7xIQE5l3ap_hFRZIC1UhGcBv0"
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
tipo_productor = st.radio("🌱 ¿Qué tipo de yuca produce?", ["Dulce", "Amarga"], key="tipo_productor")
variedad_actual = st.text_input("🌾 ¿Qué variedad de yuca siembra actualmente?", key="variedad_actual")

# Directorio donde están los videos (ruta relativa)
VIDEO_DIR = "videos"

# Verificar si la carpeta de videos existe
if not os.path.exists(VIDEO_DIR):
    st.error(f"⚠️ La carpeta {VIDEO_DIR} no existe. Asegúrate de que los videos están en la carpeta correcta.")
    st.stop()

# Obtener la lista de videos
videos = [f for f in os.listdir(VIDEO_DIR) if f.endswith(".mp4")]
if not videos:
    st.error("⚠️ No se encontraron videos en la carpeta. Asegúrate de que los archivos tienen extensión .mp4.")
    st.stop()

# Guardar los videos seleccionados en la sesión para evitar reinicios
if "selected_videos" not in st.session_state:
    st.session_state.selected_videos = random.sample(videos, 3)

selected_videos = st.session_state.selected_videos  # Recuperar los videos guardados en sesión

# Mostrar los 3 videos aleatorios
st.subheader("🎥 Por favor, vea los siguientes videos antes de responder:")
video_labels = {}  # Diccionario para mapear archivos con nombres
for i, video in enumerate(selected_videos, 1):
    video_path = os.path.join(VIDEO_DIR, video)
    st.write(f"Reproduciendo video: {video}")  # Depuración: mostrar el nombre del video
    st.video(video_path)
    video_labels[video] = video.replace(".mp4", "")  # Nombre sin la extensión

# Preguntas sobre preferencia de variedades
st.subheader("📊 Clasificación de Preferencia")

# Guardar la selección en sesión para evitar reinicios
if "fav_video" not in st.session_state:
    st.session_state.fav_video = None

if "least_fav_video" not in st.session_state:
    st.session_state.least_fav_video = None

fav_video = st.radio("✅ ¿Cuál video le gustó más?", list(video_labels.values()), key="fav", index=None)
least_fav_video = st.radio("❌ ¿Cuál video le gustó menos?", list(video_labels.values()), key="least_fav", index=None)

# Validación para evitar que se elijan el mismo video como el favorito y el menos favorito
if fav_video and least_fav_video and fav_video == least_fav_video:
    st.warning("⚠️ La opción que más le gustó y la que menos le gustó no pueden ser la misma. Seleccione opciones diferentes.")

# Función para guardar respuestas en Supabase
def guardar_respuesta():
    data = {
        "fecha_encuesta": fecha_encuesta,
        "nombre": st.session_state.nombre,
        "ubicacion": st.session_state.ubicacion,
        "tipo_productor": st.session_state.tipo_productor,
        "variedad_actual": st.session_state.variedad_actual,
        "video_1": video_labels[selected_videos[0]],
        "video_2": video_labels[selected_videos[1]],
        "video_3": video_labels[selected_videos[2]],
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
