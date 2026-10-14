import streamlit as st
import pandas as pd
import os

DATA_DIR = "data"
THRUTUBING_FILE = os.path.join(DATA_DIR, "inventario_thrutubing.csv")
MOVIMIENTOS_FILE = os.path.join(DATA_DIR, "historial_movimientos_tt.csv")
TIEMPOS_FILE = os.path.join(DATA_DIR, "reporte_tiempos_tt.csv")
MANTENIMIENTO_FILE = os.path.join(DATA_DIR, "mantenimiento_fondo_tt.csv")

COLUMNAS_TT_OFICIALES = [
    "PDA", "No. SERIE", "TIPO", "DESCRIPCION", "OD", "ID", "LARGO", "CONEXION", "DESTINO", "ESTADO"
]

def render_thru_tubing():
    st.title("Mendoza Servicios e Herramientas")
    st.caption("Sistema ERP Integrado — Departamento de Thru-Tubing / Tubería Flexible")

    menu_tt = st.sidebar.radio(
        "📌 Módulos Thru-Tubing:",
        [
            "🔄 Movimientos (MSH-TT-FOR-001)",
            "📐 Diagrama BHA (MSH-TT-FOR-004)",
            "↩️ Retorno (MSH-TT-FOR-002)",
            "⏱️ Reporte de Tiempos (FOR-007)",
            "⚙️ Trazabilidad Motores",
            "🔧 Mantenimiento de Fondo (FOR-009)",
            "📋 Bitácora de Movimientos",
            "🛡️ Administración / Carga Masiva"
        ]
    )

    df_tt = pd.read_csv(THRUTUBING_FILE)

    if menu_tt == "🔄 Movimientos (MSH-TT-FOR-001)":
        st.header("Formato: MSH-TT-FOR-001 — Salida de Herramientas (Despacho a Pozo)")
        
        st.subheader("📄 Encabezado del Formato Oficial Mendoza")
        c1, c2, c3 = st.columns(3)
        with c1:
            folio = st.text_input("NÚMERO DE FOLIO:", value=f"MSH-TT-FOR-001-{pd.Timestamp.now().strftime('%Y%m%d-%H%M')}")
            cliente = st.text_input("CLIENTE:", value="SEPEC")
            campo = st.text_input("CAMPO:", value="5 PRESIDENTES")
            solicita_salida = st.text_input("SOLICITA SALIDA (NOMBRE):", value="Arcenio Jimenez Morgan")
        with c2:
            dept = st.text_input("DEPARTAMENTO SOLICITANTE:", value="TUBERIA FLEXIBLE")
            num_pozo = st.text_input("NUM. DE POZO:", value="910")
            distrito = st.text_input("DISTRITO:", value="5 PRESIDENTES")
            revisa_herramienta = st.text_input("REVISA HERRAMIENTA (NOMBRE):", value="Alfredo Mosqueda Torres")
        with c3:
            realiza_sol = st.text_input("REALIZA SOLICITUD:", value="DAVID REYES URESTI")
            cotizacion = st.text_input("NO. DE COTIZACIÓN:", value="N/A")
            lugar_salida = st.text_input("LUGAR DE SALIDA:", value="BASE MENDOZA")
            autoriza_salida = st.text_input("AUTORIZA SALIDA (NOMBRE):", value="Olimpia Roque Priego")

        st.text_input("FECHA DE EMISIÓN:", value=pd.Timestamp.now().strftime("%Y / %m / %d"), disabled=True)

        st.markdown("---")
        st.subheader("🛠️ Selección de Herramientas para la Sarta")

        if df_tt.empty:
            st.warning("⚠️ El catálogo está vacío. Ve al módulo '🛡️ Administración / Carga Masiva' para importar el Excel oficial de Mendoza.")
        else:
            herramientas_disponibles = df_tt[df_tt["ESTADO"] == "TALLER"] if "ESTADO" in df_tt.columns else df_tt
            
            pzas_sel = st.multiselect(
                "Buscar y agregar herramientas por No. de Serie / Tipo:",
                options=herramientas_disponibles["No. SERIE"].dropna().tolist(),
                format_func=lambda x: f"{x} - {df_tt.loc[df_tt['No. SERIE'] == x, 'TIPO'].values[0]} ({df_tt.loc[df_tt['No. SERIE'] == x, 'DESCRIPCION'].values[0]})"
            )

            if pzas_sel:
                st.write("### Componentes Seleccionados para el Despacho:")
                df_sub = df_tt[df_tt["No. SERIE"].isin(pzas_sel)]
                st.dataframe(df_sub[["PDA", "No. SERIE", "TIPO", "DESCRIPCION", "OD", "CONEXION", "DESTINO"]], use_container_width=True)

                if st.button("🚀 Generar Folio y Despachar A Pozo", use_container_width=True):
                    df_tt.loc[df_tt["No. SERIE"].isin(pzas_sel), "ESTADO"] = "EN POZO"
                    df_tt.to_csv(THRUTUBING_FILE, index=False)

                    df_mov = pd.read_csv(MOVIMIENTOS_FILE)
                    reg_mov = pd.DataFrame([{
                        "Folio": folio,
                        "Fecha": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M"),
                        "Tipo_Mov": "SALIDA_POZO",
                        "Cliente": cliente,
                        "Pozo": num_pozo,
                        "Solicito": solicita_salida,
                        "Reviso": revisa_herramienta,
                        "Autorizo": autoriza_salida,
                        "Herramientas_IDs": ", ".join(pzas_sel)
                    }])
                    pd.concat([df_mov, reg_mov], ignore_index=True).to_csv(MOVIMIENTOS_FILE, index=False)
                    st.success(f"✅ Se despachó con éxito el Folio `{folio}` para el Pozo {num_pozo}.")
                    st.rerun()

    elif menu_tt == "📐 Diagrama BHA (MSH-TT-FOR-004)":
        st.header("Formato: MSH-TT-FOR-004 — Diagrama de Herramientas BHA")

        st.subheader("📄 Encabezado de Operaciones Thru Tubing")
        c1, c2, c3 = st.columns(3)
        with c1:
            st.text_input("CLIENTE:", value="SEPEC")
            st.text_input("REALIZA SOLICITUD:", value="ING. DAVID REYES")
        with c2:
            st.text_input("DEPARTAMENTO:", value="TUBERIA FLEXIBLE")
            st.text_input("SUPERVISOR DE CAMPO:", value="SAID RIVERA RICHA")
        with c3:
            st.text_input("CAMPO:", value="RIO NUEVO")
            st.text_input("NÚM. DE POZO:", value="1051")

        st.text_input("OPERACIÓN:", value="LIMPIEZA DE APAREJO CON MOTOR HPHT DE 2 1/8 IN Y MOLINO SEMICONICO DE 2 1/4 IN")

        st.markdown("---")
        st.subheader("🖼️ Imagen del Diagrama Técnico del BHA")
        st.file_uploader("Subir imagen del render / croquis del BHA (JPG o PNG):", type=["png", "jpg", "jpeg"])

        st.markdown("---")
        st.subheader("🧩 Componentes de la Sarta BHA")
        df_en_pozo = df_tt[df_tt["ESTADO"] == "EN POZO"] if "ESTADO" in df_tt.columns else pd.DataFrame()

        if df_en_pozo.empty:
            st.warning("⚠️ No hay herramientas registradas en pozo. Primero debes registrar una salida desde el módulo Movimientos (MSH-TT-FOR-001).")
        else:
            st.dataframe(df_en_pozo[["PDA", "No. SERIE", "TIPO", "DESCRIPCION", "OD", "LARGO", "CONEXION"]], use_container_width=True)

    elif menu_tt == "↩️ Retorno (MSH-TT-FOR-002)":
        st.header("Formato: MSH-TT-FOR-002 — Retorno de Herramientas (Entrada al Taller)")
        df_en_pozo = df_tt[df_tt["ESTADO"] == "EN POZO"] if "ESTADO" in df_tt.columns else pd.DataFrame()

        if df_en_pozo.empty:
            st.success("🟢 Actualmente no hay herramientas operando en pozo. Todo el catálogo se encuentra disponible en el Taller Principal.")
        else:
            st.write("### Herramientas Actualmente en Campo:")
            ret_sel = st.multiselect("Seleccionar herramientas que retornan al taller:", options=df_en_pozo["No. SERIE"].tolist())

            if ret_sel:
                if st.button("📥 Registrar Entrada al Taller", use_container_width=True):
                    df_tt.loc[df_tt["No. SERIE"].isin(ret_sel), "ESTADO"] = "TALLER"
                    df_tt.to_csv(THRUTUBING_FILE, index=False)

                    df_mov = pd.read_csv(MOVIMIENTOS_FILE)
                    reg_ret = pd.DataFrame([{
                        "Folio": f"MSH-TT-FOR-002-{pd.Timestamp.now().strftime('%Y%m%d-%H%M')}",
                        "Fecha": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M"),
                        "Tipo_Mov": "RETORNO_TALLER",
                        "Herramientas_IDs": ", ".join(ret_sel)
                    }])
                    pd.concat([df_mov, reg_ret], ignore_index=True).to_csv(MOVIMIENTOS_FILE, index=False)
                    st.success("✅ Herramientas reingresadas al inventario de Taller correctamente.")
                    st.rerun()

    elif menu_tt == "⏱️ Reporte de Tiempos (FOR-007)":
        st.header("Formato: MSH-TT-FOR-007 — Reporte de Tiempos Operativos Diario")
        c1, c2, c3 = st.columns(3)
        with c1:
            st.date_input("FECHA DEL REPORTE:")
        with c2:
            pozo_t = st.text_input("NUM. DE POZO:", value="910")
        with c3:
            st.text_input("OPERADOR / INGENIERO DE CAMPO:", value="ARCENIO JIMENEZ MORGAN")

        st.subheader("⏱️ Registrar Tramo de Actividad (24 Horas)")
        ca, cb, cc = st.columns(3)
        with ca:
            h_ini = st.time_input("Hora de Inicio:")
        with cb:
            h_fin = st.time_input("Hora de Fin:")
        with cc:
            clasif = st.selectbox("Clasificación del Tiempo:", ["Tiempo Operativo (Actividad Normal)", "Tiempo Imprevisto / Falla", "Mantenimiento Preventivo en Pozo", "Viaje de Tubería"])

        desc_act = st.text_area("Descripción detallada de la actividad en pozo:")

        if st.button("➕ Agregar Actividad al Día"):
            df_t = pd.read_csv(TIEMPOS_FILE)
            reg_t = pd.DataFrame([{
                "Fecha": pd.Timestamp.now().strftime("%Y-%m-%d"),
                "Pozo": pozo_t,
                "Hora_Inicio": str(h_ini),
                "Hora_Fin": str(h_fin),
                "Clasificacion": clasif,
                "Descripcion": desc_act
            }])
            pd.concat([df_t, reg_t], ignore_index=True).to_csv(TIEMPOS_FILE, index=False)
            st.success("Actividad registrada en la bitácora de tiempos.")
            st.rerun()

    elif menu_tt == "⚙️ Trazabilidad Motores":
        st.header("Módulo de Trazabilidad, Salud Operativa e Inspecciones NDT para Motores")
        df_motores = df_tt[df_tt["TIPO"].astype(str).str.contains("MOTOR", case=False, na=False)] if not df_tt.empty else pd.DataFrame()

        if df_motores.empty:
            st.info("ℹ️ Carga el inventario oficial desde Administración para habilitar el seguimiento de Motores de Fondo.")
        else:
            st.subheader("⚙️ Control de Horas de Operación y Vida Útil (Motores)")
            st.dataframe(df_motores[["No. SERIE", "TIPO", "DESCRIPCION", "OD", "CONEXION", "ESTADO"]], use_container_width=True)

    elif menu_tt == "🔧 Mantenimiento de Fondo (FOR-009)":
        st.header("Formato: MSH-TT-FOR-009 — Control de Mantenimiento a Herramienta de Fondo")
        
        if df_tt.empty:
            st.warning("⚠️ No hay herramientas en la base de datos. Carga el inventario en '🛡️ Administración / Carga Masiva'.")
        else:
            st.subheader("🔍 1. Identificación del Equipo en Taller")
            
            opciones_herramientas = df_tt["No. SERIE"].dropna().tolist()
            serie_sel = st.selectbox(
                "Seleccione el No. de Serie de la herramienta que entró a taller:",
                options=opciones_herramientas,
                format_func=lambda x: f"{x} - {df_tt.loc[df_tt['No. SERIE'] == x, 'DESCRIPCION'].values[0]}" if not df_tt.loc[df_tt['No. SERIE'] == x].empty else x
            )

            if serie_sel:
                info_tool = df_tt[df_tt["No. SERIE"] == serie_sel].iloc[0]
                
                st.markdown("---")
                st.markdown("### 📋 Ficha Técnica y Especificaciones Geométricas")
                
                m1, m2, m3, m4, m5, m6 = st.columns(6)
                m1.metric("Categoría / Tipo", str(info_tool.get("TIPO", "N/A")))
                m2.metric("Diámetro Ext. (OD)", str(info_tool.get("OD", "N/A")))
                m3.metric("Diámetro Int. (ID)", str(info_tool.get("ID", "N/A")))
                m4.metric("Longitud (m)", str(info_tool.get("LARGO", "N/A")))
                m5.metric("Tipo Conexión", str(info_tool.get("CONEXION", "N/A")))
                m6.metric("Estado Actual", str(info_tool.get("ESTADO", "TALLER")))

                st.info(f"📌 **Descripción:** {info_tool.get('DESCRIPCION', 'Sin descripción')} | **Ubicación / Destino:** {info_tool.get('DESTINO', 'TALLER PRINCIPAL')}")
                st.markdown("---")

            st.subheader("🔧 2. Registro de Inspección y Servicio Realizado")
            
            col_a, col_b, col_c = st.columns(3)
            with col_a:
                f_op = st.date_input("Fecha de la Operación / Corrida:")
                f_mtto = st.date_input("Fecha de Mantenimiento en Taller:")
                pozo_op = st.text_input("Pozo donde operó:", value="Puerto Celba 157")
                tipo_op = st.text_input("Tipo de operación:", value="Limpieza de Aparejo")

            with col_b:
                fluido_u = st.text_input("Tipo de fluido usado:", value="Agua, Solvente")
                op_campo = st.text_input("Operador de Herramientas (Campo):", value="Arcenio Jimenez Morgan")
                tec_resp = st.text_input("Técnico / Mecánico responsable (Taller):", value="David Reyes Uresti")
                dictamen = st.selectbox("Dictamen Inspección NDT (Partículas Magnéticas):", ["ACEPTADO", "RECHAZADO", "REQUIERE REPARACION"])

            with col_c:
                hrs_viaje = st.number_input("Horas de viaje:", value=18.0, step=0.5)
                hrs_circ = st.number_input("Horas de circulación:", value=15.0, step=0.5)
                hrs_carga = st.number_input("Horas de carga (Trabajando):", value=0.0, step=0.5)
                hrs_estatico = st.number_input("Horas en estático:", value=0.0, step=0.5)

            diag_tec = st.text_area("Mantenimiento realizado / Diagnóstico técnico:", placeholder="Describa limpieza, inspección de roscas, cambio de elastómeros, apriete de conexiones...")

            if st.button("📝 Registrar Mantenimiento Oficial", use_container_width=True):
                df_mtto = pd.read_csv(MANTENIMIENTO_FILE)
                
                nuevo_mantenimiento = pd.DataFrame([{
                    "Fecha_Operacion": str(f_op),
                    "Fecha_Mantenimiento": str(f_mtto),
                    "No_Serie": serie_sel,
                    "Tipo_Herramienta": str(info_tool.get("TIPO", "N/A")),
                    "Pozo": pozo_op,
                    "Tipo_Operacion": tipo_op,
                    "Fluido_Usado": fluido_u,
                    "Operador_Campo": op_campo,
                    "Tecnico_Taller": tec_resp,
                    "Dictamen_NDT": dictamen,
                    "Hrs_Viaje": hrs_viaje,
                    "Hrs_Circulacion": hrs_circ,
                    "Hrs_Carga": hrs_carga,
                    "Hrs_Estatico": hrs_estatico,
                    "Diagnostico_Tecnico": diag_tec
                }])

                pd.concat([df_mtto, nuevo_mantenimiento], ignore_index=True).to_csv(MANTENIMIENTO_FILE, index=False)
                st.success(f"✅ Mantenimiento registrado correctamente para la pieza `{serie_sel}` con dictamen **{dictamen}**.")
                st.rerun()

            st.markdown("---")
            st.subheader(f"📜 Historial Clínico de Mantenimiento (No. Serie: {serie_sel})")
            
            df_mtto = pd.read_csv(MANTENIMIENTO_FILE)
            if not df_mtto.empty and serie_sel in df_mtto["No_Serie"].values:
                historial_herramienta = df_mtto[df_mtto["No_Serie"] == serie_sel]
                st.dataframe(historial_herramienta, use_container_width=True)
            else:
                st.info(f"Esta herramienta ({serie_sel}) no cuenta con registros de mantenimiento previos en el sistema.")

    elif menu_tt == "📋 Bitácora de Movimientos":
        st.header("📋 Auditoría e Historial Analítico de Movimientos (Taller y Pozo)")
        df_m = pd.read_csv(MOVIMIENTOS_FILE)
        if df_m.empty:
            st.info("No se registran movimientos (entradas o salidas) en el sistema actualmente.")
        else:
            st.dataframe(df_m, use_container_width=True)

    elif menu_tt == "🛡️ Administración / Carga Masiva":
        st.header("⚙️ Panel de Administración y Control de Base de Datos")
        pwd = st.text_input("Contraseña del Administrador:", type="password")

        if pwd == "MENDOZA2026":
            st.success("🔒 Acceso Autorizado.")
            st.subheader("📥 Cargar Catálogo de Inventario (Soporta .xlsx y .xlsm)")

            uploaded_mendoza = st.file_uploader("Subir Archivo Excel Mendoza (.xlsx / .xlsm):", type=["xlsx", "xlsm", "xls"])

            if uploaded_mendoza is not None:
                try:
                    xls = pd.ExcelFile(uploaded_mendoza)
                    
                    if len(xls.sheet_names) > 1:
                        hojas_validas = [
                            'Conectores', 'Trompos difusores', 'Combinaciones', 'Herramientas varias',
                            'Herramientas de pesca', 'Molinos y zapatas', 'Centradores y cortatubos',
                            'Motores', 'Martillos de pesca'
                        ]
                        
                        lista_dfs = []
                        for hoja in hojas_validas:
                            if hoja in xls.sheet_names:
                                df_h = pd.read_excel(xls, sheet_name=hoja)
                                data = df_h.iloc[3:].copy()
                                valid_data = data[data.iloc[:, 0].notna() & (data.iloc[:, 0].astype(str).str.strip() != "")].copy()
                                
                                def get_col_segura(df_in, col_idx):
                                    return df_in.iloc[:, col_idx].values if col_idx < df_in.shape[1] else ["N/A"] * len(df_in)
                                
                                df_clean_h = pd.DataFrame({
                                    'PDA': range(1, len(valid_data) + 1),
                                    'No. SERIE': get_col_segura(valid_data, 0),
                                    'TIPO': hoja.upper(),
                                    'DESCRIPCION': get_col_segura(valid_data, 1),
                                    'OD': get_col_segura(valid_data, 4),
                                    'ID': get_col_segura(valid_data, 3),
                                    'LARGO': get_col_segura(valid_data, 5),
                                    'CONEXION': get_col_segura(valid_data, 8),
                                    'DESTINO': 'TALLER PRINCIPAL',
                                    'ESTADO': 'TALLER'
                                })
                                lista_dfs.append(df_clean_h)
                        
                        clean_df = pd.concat(lista_dfs, ignore_index=True)
                        clean_df['PDA'] = range(1, len(clean_df) + 1)
                        st.info("📦 Formato Detectado: **Catálogo Maestro General Mendoza (1,374 piezas)**")

                    else:
                        df_raw = pd.read_excel(uploaded_mendoza)
                        data_df = df_raw.iloc[18:].copy()
                        
                        cols_pos = [0, 4, 9, 14, 19, 24, 29, 34, 39]
                        cols_names = ['PDA', 'No. SERIE', 'TIPO', 'DESCRIPCION', 'OD', 'ID', 'LARGO', 'CONEXION', 'DESTINO']
                        
                        clean_df = data_df.iloc[:, cols_pos].copy()
                        clean_df.columns = cols_names
                        clean_df = clean_df[pd.to_numeric(clean_df['PDA'], errors='coerce').notna()].copy()
                        clean_df["ESTADO"] = "TALLER"
                        st.info("📄 Formato Detectado: **Remito / Salida Poza Rica (123 piezas)**")

                    st.success(f"🎉 ¡Procesamiento exitoso! Se procesaron **{len(clean_df)} herramientas**.")
                    st.dataframe(clean_df, use_container_width=True)

                    if st.button("🚀 Sobrescribir Base de Datos del Sistema", use_container_width=True):
                        clean_df.to_csv(THRUTUBING_FILE, index=False)
                        st.success("✅ Base de datos reescrita exitosamente.")
                        st.rerun()

                except Exception as e:
                    st.error(f"Error al procesar el archivo oficial: {e}")

            st.markdown("---")
            if st.button("🗑️ Vaciar Base de Datos Thru-Tubing"):
                pd.DataFrame(columns=COLUMNAS_TT_OFICIALES).to_csv(THRUTUBING_FILE, index=False)
                st.warning("Base de datos borrada.")
                st.rerun()
        elif pwd != "":
            st.error("❌ Contraseña incorrecta. (Clave por defecto: MENDOZA2026)")