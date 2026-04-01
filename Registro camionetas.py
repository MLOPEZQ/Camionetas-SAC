import streamlit as st
import pandas as pd
from datetime import date
from PIL import Image
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json

# CONFIGURACIÓN GOOGLE SHEETS
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
credenciales_dict = json.loads(st.secrets["GOOGLE_SHEETS_JSON"])
creds = ServiceAccountCredentials.from_json_keyfile_dict(credenciales_dict, scope)
client = gspread.authorize(creds)
sheet = client.open("Uso_Camionetas").sheet1

#GOOGLE SHEETS
data = sheet.get_all_records()
df_existente = pd.DataFrame(data)

if not df_existente.empty and "Fecha" in df_existente.columns:
    df_existente["Fecha"] = pd.to_datetime(df_existente["Fecha"], errors="coerce")

st.set_page_config(page_title="Registro uso camionetas - SAC", layout="centered")
st.markdown(
    """
    <style>
    .stApp {background-color: #f9f5ff;}
    h1, h2, h3 {text-align: center; color: #2d004d;}
    </style>
    """,
    unsafe_allow_html=True
)
#####desde aqui

###hasta aqui

st.markdown("<h2 style='text-align: center;'>Registro uso camionetas - SAC</h2>", unsafe_allow_html=True)

gestores = [
    "Hernán Aguilera", "Ignacio Basaure", "Francisco Barrios", "Felipe Camus", "Rodrigo Escandón", "Juan Pablo Molina",
    "Marilin López", "Francisco Parra", "Roberto Severino", "Manuel Araus", "Christian Cifuentes", "Germán Villegas", "Andrea Collao"
]
patentes = [
    "VTTT79", "VTVC71", "VTVC81", "VTYX22", "VTYX37",
    "VTYX44", "VTYX91"
]

# REGISTRO
st.markdown("#### 📝 Nuevo Registro")

with st.form("registro_formulario"):
    fecha = st.date_input("Fecha del registro", value=date.today(), min_value=date(2025, 6, 1))
    gestor = st.selectbox("Gestor", gestores)
    patente = st.selectbox("Patente", patentes)
    sitio = st.text_input("Código Subtel")
    region = st.number_input("Región (solo número)", min_value=1, step=1)
    actividad = st.text_area("Actividad realizada")
    enviar = st.form_submit_button("Enviar Registro")

    if enviar:
        if not sitio.strip() or not actividad.strip():
            st.error("❌ Todos los campos deben estar completos.")
        else:
            existe = (
                (df_existente["Fecha"].dt.date == fecha) &
                (df_existente["Gestor"] == gestor) &
                (df_existente["Patente"] == patente)
            ).any() if not df_existente.empty else False

            if existe:
                st.error("❌ Ya existe un registro para este día asociado al Gestor y Patente.")
            else:
                nueva_fila = [str(fecha), gestor, patente, sitio, int(region), actividad]
                sheet.append_row(nueva_fila)
                st.success("✅ Registro guardado en Google Sheets correctamente. Recarga para ver reflejado.")

# CONSULTAS
st.markdown("---")
st.markdown("#### 📊 Consulta tus registros")

gestor_consulta = st.selectbox("Selecciona tu nombre", gestores, key="gestor_consulta")

if not df_existente.empty and "Gestor" in df_existente.columns:
    df_gestor = df_existente[df_existente["Gestor"] == gestor_consulta].copy()

    if not df_gestor.empty:
        st.success(f"Tienes {len(df_gestor)} registro(s).")

        for idx, fila in df_gestor.iterrows():
            fecha_str = fila["Fecha"].strftime("%Y-%m-%d") if pd.notnull(fila["Fecha"]) else "Sin fecha"
            with st.expander(f"{fecha_str} | {fila['Patente']} | {fila['Código Subtel']}", expanded=False):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Región:** {fila['Región']}")
                    st.write(f"**Actividad:** {fila['Actividad']}")
    else:
        st.info("No hay registros para mostrar aún.")
else:
    st.info("No hay registros disponibles para este gestor aún.")

# DESCARGA
st.markdown("---")
st.markdown("#### 🔒 Acceso Restringido")
codigo = st.text_input("Ingresa el código para descargar consolidado", type="password")
if codigo == "mlq2025":
    if not df_existente.empty:
        excel = df_existente.to_excel(index=False, engine="openpyxl")
        st.download_button("📅 Descargar Excel consolidado", data=excel, file_name="uso_camionetas.xlsx")
else:
    st.warning("⚠️ Ingresa el código para habilitar la descarga.")
