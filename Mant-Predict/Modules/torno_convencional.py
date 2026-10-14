import streamlit as st
import pandas as pd
import os
import math

DATA_DIR = "data"
TORNO_FILE = os.path.join(DATA_DIR, "inventario_torno_convencional.csv")
CONSUMO_TORNO_FILE = os.path.join(DATA_DIR, "historial_consumo_torno.csv")

COLUMNAS_TORNO = [
    "Código / Identificador", "Tipo de Herramienta", "Medida / Dimensión", 
    "Material / Grado", "Stock Actual", "Stock Mínimo", "Ubicación / Gaveta"
]

def render_torno_convencional():
    st.title("🪚 Torno Convencional | Maquinado Mecánico Manual")
    st.caption("Control de buriles HSS, insertos soldados, brocas cono morse, mochuelos y accesorios de torneado manual.")

    tab1, tab2, tab3, tab4 = st.tabs([
        "📋 Inventario y Stock de Buriles", 
        "📤 Consumo y Salidas a Tornero", 
        "📥 Cargar / Registrar Herramientas", 
        "📐 Calculadora de Parámetros y Conos"
    ])

    # -------------------------------------------------------------
    # TAB 1: INVENTARIO
    # -------------------------------------------------------------
    with tab1:
        st.subheader("Catálogo Maestro de Herramental para Torno Convencional")
        df_torno = pd.read_csv(TORNO_FILE)

        c1, c2, c3 = st.columns(3)
        c1.metric("Herramientas Registradas", len(df_torno))
        c2.metric("Total de Piezas en Pañol", int(df_torno["Stock Actual"].sum()) if not df_torno.empty else 0)
        
        criticos = df_torno[df_torno["Stock Actual"] <= df_torno["Stock Mínimo"]] if not df_torno.empty else pd.DataFrame()
        c3.metric("Alertas de Stock Mínimo", len(criticos), delta_color="inverse" if len(criticos) > 0 else "normal")

        st.markdown("---")
        if not df_torno.empty:
            busqueda = st.text_input("🔍 Buscar por Código, Tipo de Herramienta o Medida:")
            if busqueda:
                mask = (
                    df_torno["Código / Identificador"].astype(str).str.contains(busqueda, case=False, na=False) |
                    df_torno["Tipo de Herramienta"].astype(str).str.contains(busqueda, case=False, na=False) |
                    df_torno["Medida / Dimensión"].astype(str).str.contains(busqueda, case=False, na=False)
                )
                df_mostrar = df_torno[mask]
            else:
                df_mostrar = df_torno

            st.dataframe(df_mostrar, use_container_width=True)

            if not criticos.empty:
                st.warning("⚠️ **Requisición recomendada:** Las siguientes herramientas están en o por debajo del stock mínimo:")
                st.table(criticos[["Código / Identificador", "Tipo de Herramienta", "Medida / Dimensión", "Stock Actual", "Stock Mínimo"]])
        else:
            st.info("ℹ️ El inventario de Torno Convencional está vacío. Ve a **'📥 Cargar / Registrar Herramientas'** para agregar elementos.")

    # -------------------------------------------------------------
    # TAB 2: CONSUMO Y SALIDAS
    # -------------------------------------------------------------
    with tab2:
        st.subheader("Registrar Salida / Préstamo de Herramental a Tornero")
        df_torno = pd.read_csv(TORNO_FILE)

        if df_torno.empty:
            st.warning("⚠️ No hay herramental registrado. Registra primero las herramientas en el inventario.")
        else:
            col_form, col_hist = st.columns([1, 1.2])

            with col_form:
                with st.form("form_salida_torno", clear_on_submit=True):
                    cod_sel = st.selectbox("Herramienta / Buril", df_torno["Código / Identificador"].values)
                    cant = st.number_input("Cantidad entregada", min_value=1, step=1, value=1)
                    tornero = st.text_input("Nombre del Tornero / Operador")
                    torno_num = st.text_input("Torno Asignado (Ej. Torno Paralelo 1 / Tos Trencin)")
                    ot = st.text_input("Orden de Trabajo / Trabajo a Realizar")

                    if st.form_submit_button("Registrar Entrega a Tornero"):
                        stock_act = int(df_torno.loc[df_torno["Código / Identificador"] == cod_sel, "Stock Actual"].values[0])
                        if cant > stock_act:
                            st.error(f"❌ Stock insuficiente en pañol. Quedan {stock_act} piezas.")
                        else:
                            df_torno.loc[df_torno["Código / Identificador"] == cod_sel, "Stock Actual"] = stock_act - cant
                            df_torno.to_csv(TORNO_FILE, index=False)

                            df_hist = pd.read_csv(CONSUMO_TORNO_FILE)
                            nuevo_reg = pd.DataFrame([{
                                "Fecha": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M"),
                                "Código / Identificador": cod_sel,
                                "Cantidad": cant,
                                "Tornero": tornero,
                                "Torno": torno_num,
                                "OT / Proyecto": ot
                            }])
                            pd.concat([df_hist, nuevo_reg], ignore_index=True).to_csv(CONSUMO_TORNO_FILE, index=False)
                            st.success(f"✅ Se entregaron {cant} pza(s) al tornero {tornero}.")
                            st.rerun()

            with col_hist:
                st.subheader("Histórico de Entregas Recientes")
                df_hist = pd.read_csv(CONSUMO_TORNO_FILE)
                if not df_hist.empty:
                    st.dataframe(df_hist.tail(10), use_container_width=True)
                else:
                    st.info("Sin registros de entregas aún.")

    # -------------------------------------------------------------
    # TAB 3: CARGA Y REGISTRO
    # -------------------------------------------------------------
    with tab3:
        st.subheader("📥 Cargar Inventario desde Archivo Excel / CSV")
        uploaded = st.file_uploader("Selecciona archivo de Excel o CSV de Torno", type=["xlsx", "xls", "csv"], key="file_torno")

        if uploaded is not None:
            try:
                df_excel = pd.read_csv(uploaded) if uploaded.name.endswith('.csv') else pd.read_excel(uploaded)
                st.success(f"📄 Archivo `{uploaded.name}` leído ({len(df_excel)} filas encontradas).")
                st.dataframe(df_excel.head(5), use_container_width=True)

                faltantes = [c for c in COLUMNAS_TORNO if c not in df_excel.columns]
                if faltantes:
                    st.warning(f"⚠️ El archivo no contiene estas columnas requeridas: `{faltantes}`")
                else:
                    if st.button("🚀 Importar al Inventario de Torno Convencional", use_container_width=True):
                        df_curr = pd.read_csv(TORNO_FILE)
                        df_updated = pd.concat([df_curr, df_excel[COLUMNAS_TORNO]], ignore_index=True)
                        df_updated.drop_duplicates(subset=["Código / Identificador"], keep="last", inplace=True)
                        df_updated.to_csv(TORNO_FILE, index=False)
                        st.success("🎉 ¡Herramientas importadas con éxito!")
                        st.rerun()
            except Exception as e:
                st.error(f"Error al leer el archivo: {e}")

        st.markdown("---")
        st.subheader("➕ Registro Manual Individual")
        df_torno = pd.read_csv(TORNO_FILE)

        with st.form("form_alta_torno", clear_on_submit=True):
            ca, cb = st.columns(2)
            with ca:
                cod_n = st.text_input("Código / ID (Ej. BUR-HSS-1/2, BRC-MT3-25MM)")
                tipo_n = st.selectbox("Tipo de Herramienta", [
                    "Buril HSS (Cobalto)", 
                    "Buril Soldado Carburo (Calza)", 
                    "Broca Cono Morse", 
                    "Broca de Centrar", 
                    "Cuchilla de Tronzar / Ranurar", 
                    "Mochuelo / Tarraja", 
                    "Moleteador", 
                    "Punto Giratorio / Chuc"
                ])
                med_n = st.text_input("Medida / Dimensión (Ej. 1/2' x 4', Ø 25mm)")
            with cb:
                mat_n = st.text_input("Material / Calidad (Ej. HSS M2, Co 8%, Carburo P30)")
                stk_n = st.number_input("Cantidad Inicial", min_value=1, step=1, value=5)
                stk_min_n = st.number_input("Stock Mínimo de Alerta", min_value=1, step=1, value=2)
                ubi_n = st.text_input("Ubicación en Pañol / Gaveta", value="Gaveta Torno A-1")

            if st.form_submit_button("Guardar Herramienta en Inventario"):
                if cod_n:
                    reg = pd.DataFrame([{
                        "Código / Identificador": cod_n,
                        "Tipo de Herramienta": tipo_n,
                        "Medida / Dimensión": med_n,
                        "Material / Grado": mat_n,
                        "Stock Actual": stk_n,
                        "Stock Mínimo": stk_min_n,
                        "Ubicación / Gaveta": ubi_n
                    }])
                    pd.concat([df_torno, reg], ignore_index=True).to_csv(TORNO_FILE, index=False)
                    st.success(f"Herramienta `{cod_n}` guardada correctamente.")
                    st.rerun()

    # -------------------------------------------------------------
    # TAB 4: CALCULADORA TÉCNICA
    # -------------------------------------------------------------
    with tab4:
        st.subheader("📐 Cálculos Rápidos para Tornero")
        
        col_m1, col_m2 = st.columns(2)
        
        with col_m1:
            st.markdown("#### 1. Cálculo de RPM según Material y Buril")
            material_mat = st.selectbox("Material a Maquinar", ["Acero 1018 / 1020", "Acero 4140 / 8620", "Inoxidable 304 / 316", "Bronce / Latón", "Aluminio"])
            
            # Sugerencia de Vc aproximada para HSS en m/min
            vc_sug = 25.0
            if "1018" in material_mat: vc_sug = 28.0
            elif "4140" in material_mat: vc_sug = 18.0
            elif "Inoxidable" in material_mat: vc_sug = 12.0
            elif "Bronce" in material_mat: vc_sug = 45.0
            elif "Aluminio" in material_mat: vc_sug = 75.0

            vc_manual = st.number_input("Velocidad de Corte Vc (m/min):", value=vc_sug, step=5.0)
            dia_mm = st.number_input("Diámetro de la pieza (mm):", value=38.1, step=5.0) # 1.5 pulgadas por defecto
            
            if dia_mm > 0:
                rpm_calc = (vc_manual * 1000) / (math.pi * dia_mm)
                st.metric("RPM Sugeridas para la palanca del Torno", f"{round(rpm_calc)} RPM")

        with col_m2:
            st.markdown("#### 2. Tabla Referencial Conos Morse (Soporte / Contrapunto)")
            tabla_cm = pd.DataFrame([
                {"Cono": "MT1", "Diámetro Mayor (mm)": "12.06", "Uso Común": "Broqueres pequeños / Tornos chicos"},
                {"Cono": "MT2", "Diámetro Mayor (mm)": "17.78", "Uso Común": "Contrapunto torno mediano, brocas hasta 23mm"},
                {"Cono": "MT3", "Diámetro Mayor (mm)": "23.82", "Uso Común": "Contrapunto torno industrial, brocas hasta 31.7mm"},
                {"Cono": "MT4", "Diámetro Mayor (mm)": "31.26", "Uso Común": "Tornos pesados / Cañón grande"},
                {"Cono": "MT5", "Diámetro Mayor (mm)": "44.39", "Uso Común": "Husillos pesados e industria petrolera"}
            ])
            st.table(tabla_cm)