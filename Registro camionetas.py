import streamlit as st
import pandas as pd
import os
from datetime import date
from PIL import Image

st.set_page_config(page_title="Registro uso camionetas - SAC", layout="centered")
archivo_excel = 'uso_camionetas.xlsx'

if os.path.exists(archivo_excel):
    df_existente = pd.read_excel(archivo_excel)
    if not df_existente.empty and 'Fecha' in df_existente.columns:
        df_existente['Fecha'] = pd.to_datetime(df_existente['Fecha'], errors='coerce')
else:
    df_existente = pd.DataFrame(columns=["Fecha", "Gestor", "Patente", "Sitio", "Región", "Proyecto", "Actividad"])

st.image("logo.jpg", use_container_width=True)
st.markdown("<h2 style='text-align: center;'>Registro uso camionetas - SAC</h2>", unsafe_allow_html=True)

#LISTAS
gestores = [
    "Rodrigo Chávez", "Hernán Aguilera", "Juan Molina", "Francisco Barrios",
    "Francisco Parra", "Rodrigo Araneda", "Marilin López", "Rodrigo Escandón",
    "Felipe Camus", "Ignacio Basaure"
]

patentes = [
    "PBFW28", "PTFP12", "PTFP13", "PTFP21", "PTWB64",
    "PTWB72", "RSVD89", "RVGV85", "RVGV87"
]

#REGISTROS
st.markdown("#### 📝 Nuevo Registro")

with st.form("registro_formulario"):
    fecha = st.date_input("Fecha del registro", value=date.today(), min_value=date(2025, 6, 1))
    gestor = st.selectbox("Gestor", gestores)
    patente = st.selectbox("Patente", patentes)
    sitio = st.text_input("Sitio")
    region = st.number_input("Región (solo número)", min_value=1, step=1)
    proyecto = st.text_input("Proyecto")
    actividad = st.text_area("Actividad realizada")

    enviar = st.form_submit_button("Enviar Registro")

    if enviar:
        if not df_existente.empty:
            existe = (
                (df_existente['Fecha'].dt.date == fecha) &
                (df_existente['Gestor'] == gestor) &
                (df_existente['Patente'] == patente)
            ).any()
        else:
            existe = False

        if existe:
            st.error("❌ Ya existe un registro para este día asociado al Gestor y Patente.")
        else:
            nuevo = pd.DataFrame({
                "Fecha": [fecha],
                "Gestor": [gestor],
                "Patente": [patente],
                "Sitio": [sitio],
                "Región": [int(region)],
                "Proyecto": [proyecto],
                "Actividad": [actividad]
            })
            df_existente = pd.concat([df_existente, nuevo], ignore_index=True)
            df_existente.to_excel(archivo_excel, index=False)
            st.success("✅ Registro guardado correctamente.")

#CONSULTAS
st.markdown("---")
st.markdown("#### 📊 Consulta o edita tus registros")

gestor_consulta = st.selectbox("Selecciona tu nombre", gestores, key="gestor_consulta")
df_gestor = df_existente[df_existente["Gestor"] == gestor_consulta].copy()

if not df_gestor.empty:
    st.success(f"Tienes {len(df_gestor)} registro(s).")

    for idx, fila in df_gestor.iterrows():
        with st.expander(f"{fila['Fecha'].date()} | {fila['Patente']} | {fila['Sitio']}", expanded=False):
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Proyecto:** {fila['Proyecto']}")
                st.write(f"**Región:** {fila['Región']}")
                st.write(f"**Actividad:** {fila['Actividad']}")
            with col2:
                if st.button("✏️ Editar", key=f"edit_{idx}"):
                    with st.form(f"form_edit_{idx}"):
                        nueva_fecha = st.date_input("Fecha", value=fila["Fecha"].date(), min_value=date(2025, 6, 1), key=f"f_fecha_{idx}")
                        nueva_patente = st.selectbox("Patente", patentes, index=patentes.index(fila["Patente"]), key=f"f_patente_{idx}")
                        nuevo_sitio = st.text_input("Sitio", value=fila["Sitio"], key=f"f_sitio_{idx}")
                        nueva_region = st.number_input("Región", min_value=1, step=1, value=int(fila["Región"]), key=f"f_region_{idx}")
                        nuevo_proyecto = st.text_input("Proyecto", value=fila["Proyecto"], key=f"f_proyecto_{idx}")
                        nueva_actividad = st.text_area("Actividad", value=fila["Actividad"], key=f"f_actividad_{idx}")
                        guardar = st.form_submit_button("Guardar cambios")

                        if guardar:
                            df_existente.loc[idx, "Fecha"] = nueva_fecha
                            df_existente.loc[idx, "Patente"] = nueva_patente
                            df_existente.loc[idx, "Sitio"] = nuevo_sitio
                            df_existente.loc[idx, "Región"] = int(nueva_region)
                            df_existente.loc[idx, "Proyecto"] = nuevo_proyecto
                            df_existente.loc[idx, "Actividad"] = nueva_actividad
                            df_existente.to_excel(archivo_excel, index=False)
                            st.success("✅ Registro actualizado. Refresca la página para ver los cambios.")

                if st.button("🗑️ Eliminar", key=f"del_{idx}"):
                    df_existente.drop(index=idx, inplace=True)
                    df_existente.to_excel(archivo_excel, index=False)
                    st.warning("🗑️ Registro eliminado. Refresca la página.")
else:
    st.info("No hay registros para mostrar aún.")

#DESCARGA
st.markdown("---")
st.markdown("#### 🔒 Acceso Restringido")
codigo = st.text_input("Ingresa el código para descargar consolidado", type="password")
if codigo == "mlq2025":
    if os.path.exists(archivo_excel):
        with open(archivo_excel, "rb") as file:
            st.download_button("📅 Descargar Excel consolidado", data=file, file_name="uso_camionetas.xlsx")
else:
    st.warning("⚠️ Ingresa el código para habilitar la descarga.")

st.markdown("""
<div style='text-align: center; font-size: 12px; color: gray; margin-top: 30px;'>
    <em>By MLOPEZQ</em>
</div>
""", unsafe_allow_html=True)
