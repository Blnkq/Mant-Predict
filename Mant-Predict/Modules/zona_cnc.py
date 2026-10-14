import streamlit as st
import pandas as pd
import os
import math

DATA_DIR = "data"
INSERTS_FILE = os.path.join(DATA_DIR, "inventario_insertos.csv")
CONSUMO_FILE = os.path.join(DATA_DIR, "historial_consumo_cnc.csv")
COLUMNAS_CNC = [
    "Código ISO", "Tipo / Operación", "Material Compatible", 
    "Marca y Grado", "Stock Actual", "Stock Mínimo", "Portaherramientas"
]

def render_zona_cnc():
    st.title("🖥️ Zona CNC | Maquinado de Alta Precisión")
    st.caption("Control integral de insumos de corte, escaneo e importación de Excel y parámetros operativos.")

    tab1, tab2, tab3, tab4 = st.tabs([
        "📋 Inventario y Stock ISO", 
        "📤 Consumo y Salidas", 
        "📥 Cargar Excel / Registro", 
        "📐 Calculadora de Parámetros"
    ])

    with tab1:
        st.subheader("Catálogo Maestro de Pastillas de Carburo")
        df_inserts = pd.read_csv(INSERTS_FILE)

        c1, c2, c3 = st.columns(3)
        c1.metric("Modelos ISO Registrados", len(df_inserts))
        c2.metric("Total de Pastillas en Pañol", int(df_inserts["Stock Actual"].sum()) if not df_inserts.empty else 0)
        
        criticos = df_inserts[df_inserts["Stock Actual"] <= df_inserts["Stock Mínimo"]] if not df_inserts.empty else pd.DataFrame()
        c3.metric("Alertas de Stock Crítico", len(criticos), delta_color="inverse" if len(criticos) > 0 else "normal")

        st.markdown("---")
        if not df_inserts.empty:
            busqueda = st.text_input("🔍 Buscar por Código ISO, Operación o Marca:")
            if busqueda:
                mask = (
                    df_inserts["Código ISO"].astype(str).str.contains(busqueda, case=False, na=False) |
                    df_inserts["Tipo / Operación"].astype(str).str.contains(busqueda, case=False, na=False) |
                    df_inserts["Marca y Grado"].astype(str).str.contains(busqueda, case=False, na=False)
                )
                df_mostrar = df_inserts[mask]
            else:
                df_mostrar = df_inserts

            st.dataframe(df_mostrar, use_container_width=True)

            if not criticos.empty:
                st.warning("⚠️ **Requisición recomendada:** Los siguientes insertos están en o por debajo del stock mínimo:")
                st.table(criticos[["Código ISO", "Marca y Grado", "Stock Actual", "Stock Mínimo"]])
        else:
            st.info("ℹ️ El inventario está completamente limpio. Dirígete a **'📥 Cargar Excel / Registro'** para importar la información.")

    with tab2:
        st.subheader("Registrar Salida de Herramental a Máquina")
        df_inserts = pd.read_csv(INSERTS_FILE)

        if df_inserts.empty:
            st.warning("⚠️ No hay insertos registrados. Carga un archivo de Excel o registra un modelo primero.")
        else:
            col_form, col_hist = st.columns([1, 1.2])

            with col_form:
                with st.form("form_salida_cnc", clear_on_submit=True):
                    codigo_sel = st.selectbox("Código ISO del Inserto", df_inserts["Código ISO"].values)
                    cant = st.number_input("Cantidad de pastillas", min_value=1, step=1, value=1)
                    maquina = st.text_input("Torno / Centro CNC (Ej. Haas ST-20)")
                    operador = st.text_input("Nombre del Operador")
                    ot = st.text_input("Orden de Trabajo / Folio")

                    if st.form_submit_button("Registrar Entrega"):
                        stock_act = int(df_inserts.loc[df_inserts["Código ISO"] == codigo_sel, "Stock Actual"].values[0])
                        if cant > stock_act:
                            st.error(f"❌ Stock insuficiente. Quedan {stock_act} pzas.")
                        else:
                            df_inserts.loc[df_inserts["Código ISO"] == codigo_sel, "Stock Actual"] = stock_act - cant
                            df_inserts.to_csv(INSERTS_FILE, index=False)

                            df_hist = pd.read_csv(CONSUMO_FILE)
                            nuevo_reg = pd.DataFrame([{
                                "Fecha": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M"),
                                "Código ISO": codigo_sel,
                                "Cantidad": cant,
                                "Máquina": maquina,
                                "Operador": operador,
                                "OT / Proyecto": ot
                            }])
                            pd.concat([df_hist, nuevo_reg], ignore_index=True).to_csv(CONSUMO_FILE, index=False)
                            st.success(f"✅ Se entregaron {cant} pza(s) a {operador}.")
                            st.rerun()

            with col_hist:
                st.subheader("Histórico de Entregas Recientes")
                df_hist = pd.read_csv(CONSUMO_FILE)
                if not df_hist.empty:
                    st.dataframe(df_hist.tail(10), use_container_width=True)
                else:
                    st.info("Sin registros de salidas aún.")

    with tab3:
        st.subheader("📥 Cargar Inventario Automático desde Excel (.xlsx / .csv)")
        uploaded = st.file_uploader("Selecciona tu archivo de Excel o CSV", type=["xlsx", "xls", "csv"])

        if uploaded is not None:
            try:
                df_excel = pd.read_csv(uploaded) if uploaded.name.endswith('.csv') else pd.read_excel(uploaded)
                st.success(f"📄 Archivo `{uploaded.name}` leído ({len(df_excel)} filas encontradas).")
                st.dataframe(df_excel.head(5), use_container_width=True)

                faltantes = [c for c in COLUMNAS_CNC if c not in df_excel.columns]
                if faltantes:
                    st.warning(f"⚠️ El archivo no contiene estas columnas necesarias: `{faltantes}`")
                else:
                    if st.button("🚀 Escanear e Importar al Inventario General", use_container_width=True):
                        df_curr = pd.read_csv(INSERTS_FILE)
                        df_updated = pd.concat([df_curr, df_excel[COLUMNAS_CNC]], ignore_index=True)
                        df_updated.drop_duplicates(subset=["Código ISO"], keep="last", inplace=True)
                        df_updated.to_csv(INSERTS_FILE, index=False)
                        st.success("🎉 ¡Datos importados al inventario exitosamente!")
                        st.rerun()
            except Exception as e:
                st.error(f"Error al leer el archivo: {e}")

        st.markdown("---")
        st.subheader("➕ Registro Manual Individual")
        df_inserts = pd.read_csv(INSERTS_FILE)

        with st.form("form_alta_manual", clear_on_submit=True):
            ca, cb = st.columns(2)
            with ca:
                cod_n = st.text_input("Código ISO (Ej. TNMG 160408)")
                op_n = st.selectbox("Tipo de Operación", ["Desbaste Externo", "Acabado Externo", "Acabado Interno", "Ranurado", "Roscado", "Broca"])
                mat_n = st.text_input("Material Compatible")
                porta_n = st.text_input("Portaherramientas")
            with cb:
                mca_n = st.text_input("Marca y Grado")
                stk_n = st.number_input("Cantidad a Ingresar", min_value=1, step=1, value=10)
                stk_min_n = st.number_input("Stock Mínimo de Alerta", min_value=1, step=1, value=4)

            if st.form_submit_button("Guardar Registro Individual"):
                if cod_n and mca_n:
                    reg = pd.DataFrame([{
                        "Código ISO": cod_n, 
                        "Tipo / Operación": op_n, 
                        "Material Compatible": mat_n,
                        "Marca y Grado": mca_n, 
                        "Stock Actual": stk_n, 
                        "Stock Mínimo": stk_min_n, 
                        "Portaherramientas": porta_n
                    }])
                    pd.concat([df_inserts, reg], ignore_index=True).to_csv(INSERTS_FILE, index=False)
                    st.success(f"Inserto `{cod_n}` guardado.")
                    st.rerun()

    with tab4:
        st.subheader("Cálculo Técnico de RPM y Velocidad de Avance (Torneado)")
        c_a, c_b = st.columns(2)
        with c_a:
            vc = st.number_input("Velocidad de Corte Vc (m/min)", value=180.0, step=10.0)
            d = st.number_input("Diámetro de la Pieza D (mm)", value=50.0, step=5.0)
            fn = st.number_input("Avance por Vuelta fn (mm/rev)", value=0.2, step=0.05, format="%.2f")
        with c_b:
            if d > 0:
                rpm = (vc * 1000) / (math.pi * d)
                vf = rpm * fn
                st.markdown("### Resultados:")
                st.metric("Velocidad del Husillo (RPM)", f"{round(rpm, 1)} RPM")
                st.metric("Velocidad de Avance (Vf)", f"{round(vf, 1)} mm/min")