import streamlit as st
import pandas as pd
import os

# Importar vistas
from Modules.panel_general import render_panel_general
from Modules.zona_cnc import render_zona_cnc
from Modules.thru_tubing import render_thru_tubing
from Modules.torno_convencional import render_torno_convencional

# Configuración de la página
st.set_page_config(
    page_title="MSH-Operation Center | Mendoza Servicios e Herramientas",
    page_icon="⚙️",
    layout="wide"
)

# --- INICIALIZACIÓN DE ARCHIVOS Y DIRECTORIOS ---
DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)

INSERTS_FILE = os.path.join(DATA_DIR, "inventario_insertos.csv")
CONSUMO_FILE = os.path.join(DATA_DIR, "historial_consumo_cnc.csv")
THRUTUBING_FILE = os.path.join(DATA_DIR, "inventario_thrutubing.csv")
MOVIMIENTOS_FILE = os.path.join(DATA_DIR, "historial_movimientos_tt.csv")
TIEMPOS_FILE = os.path.join(DATA_DIR, "reporte_tiempos_tt.csv")
MOTORES_FILE = os.path.join(DATA_DIR, "trazabilidad_motores_tt.csv")
MANTENIMIENTO_FILE = os.path.join(DATA_DIR, "mantenimiento_fondo_tt.csv")

# Archivos Torno Convencional
TORNO_FILE = os.path.join(DATA_DIR, "inventario_torno_convencional.csv")
CONSUMO_TORNO_FILE = os.path.join(DATA_DIR, "historial_consumo_torno.csv")

COLUMNAS_CNC = ["Código ISO", "Tipo / Operación", "Material Compatible", "Marca y Grado", "Stock Actual", "Stock Mínimo", "Portaherramientas"]
COLUMNAS_TT = ["PDA", "No. SERIE", "TIPO", "DESCRIPCION", "OD", "ID", "LARGO", "CONEXION", "DESTINO", "ESTADO"]
COLUMNAS_TORNO = ["Código / Identificador", "Tipo de Herramienta", "Medida / Dimensión", "Material / Grado", "Stock Actual", "Stock Mínimo", "Ubicación / Gaveta"]

# Inicializar CSVs si no existen
if not os.path.exists(INSERTS_FILE):
    pd.DataFrame(columns=COLUMNAS_CNC).to_csv(INSERTS_FILE, index=False)
if not os.path.exists(CONSUMO_FILE):
    pd.DataFrame(columns=["Fecha", "Código ISO", "Cantidad", "Máquina", "Operador", "OT / Proyecto"]).to_csv(CONSUMO_FILE, index=False)
if not os.path.exists(THRUTUBING_FILE):
    pd.DataFrame(columns=COLUMNAS_TT).to_csv(THRUTUBING_FILE, index=False)
if not os.path.exists(MOVIMIENTOS_FILE):
    pd.DataFrame(columns=["Folio", "Fecha", "Tipo_Mov", "Cliente", "Pozo", "Solicito", "Reviso", "Autorizo", "Herramientas_IDs"]).to_csv(MOVIMIENTOS_FILE, index=False)
if not os.path.exists(TIEMPOS_FILE):
    pd.DataFrame(columns=["Fecha", "Pozo", "Operador", "Hora_Inicio", "Hora_Fin", "Clasificacion", "Descripcion"]).to_csv(TIEMPOS_FILE, index=False)
if not os.path.exists(MOTORES_FILE):
    pd.DataFrame(columns=["No_Serie", "Motor", "Hrs_Acumuladas", "Hrs_Limite", "Estado_Salud", "Ultima_Corrida_Pozo"]).to_csv(MOTORES_FILE, index=False)
if not os.path.exists(MANTENIMIENTO_FILE):
    pd.DataFrame(columns=["Fecha_Operacion", "Fecha_Mantenimiento", "No_Serie", "Tipo_Herramienta", "Pozo", "Tipo_Operacion", "Fluido_Usado", "Operador_Campo", "Tecnico_Taller", "Dictamen_NDT", "Hrs_Viaje", "Hrs_Circulacion", "Hrs_Carga", "Hrs_Estatico", "Diagnostico_Tecnico"]).to_csv(MANTENIMIENTO_FILE, index=False)

if not os.path.exists(TORNO_FILE):
    pd.DataFrame(columns=COLUMNAS_TORNO).to_csv(TORNO_FILE, index=False)
if not os.path.exists(CONSUMO_TORNO_FILE):
    pd.DataFrame(columns=["Fecha", "Código / Identificador", "Cantidad", "Tornero", "Torno", "OT / Proyecto"]).to_csv(CONSUMO_TORNO_FILE, index=False)

# --- MENÚ DE NAVEGACIÓN ---
st.sidebar.title("⚙️ MSH - Operation Center")
st.sidebar.markdown("---")

menu_zona = st.sidebar.radio(
    "Selecciona la Zona u Operación:",
    [
        "📊 Panel Administrativo (General)",
        "🖥️ Zona CNC",
        "🛢️ Zona Thru-Tubing (Mendoza)",
        "🪚 Torno Convencional",
        "⚡ Soldadura y Pailería",
        "🔧 Mecánica e Hidráulica",
        "💨 Sandblasting y Recubrimientos",
        "📦 Almacén Central / Pañol"
    ]
)
st.sidebar.markdown("---")
st.sidebar.info("💡 **Sistema MSH Activo:** Mendoza Servicios e Herramientas S.A. de C.V.")

# --- ENRUTADOR PRINCIPAL ---
if menu_zona == "📊 Panel Administrativo (General)":
    render_panel_general()
elif menu_zona == "🖥️ Zona CNC":
    render_zona_cnc()
elif menu_zona == "🛢️ Zona Thru-Tubing (Mendoza)":
    render_thru_tubing()
elif menu_zona == "🪚 Torno Convencional":
    render_torno_convencional()
else:
    st.title(menu_zona)
    st.info("Módulo en desarrollo para operaciones de taller.")