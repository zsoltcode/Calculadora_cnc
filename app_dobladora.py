import streamlit as st
import math

# ==========================================
# PIEZA 7: APP MULTI-PESTAÑA (CNC + Desarrollos)
# ==========================================

st.set_page_config(page_title="Calculadora CNC", layout="centered")
st.title("🛠️ Calculadora CNC - Taller Pro")

# --- CREACIÓN DE PESTAÑAS ---
tab1, tab2 = st.tabs(["⚙️ Parámetros Máquina", "📏 Calculadora de Desarrollos"])

# ==========================================
# PESTAÑA 1: LO QUE YA TENÍAMOS
# ==========================================
with tab1:
    st.header("1. Datos del Material")
    material = st.selectbox("Tipo de Material:", ["Acero Estándar (Comercial)", "Acero Inoxidable", "Aluminio"], key="mat_tab1")

    col_input1, col_input2 = st.columns(2)
    with col_input1:
        espesor = st.number_input("Espesor de la lámina (mm):", min_value=0.1, value=12.7, step=0.1, key="esp_tab1")
    with col_input2:
        ancho_mm = st.number_input("Ancho a doblar (mm):", min_value=10.0, value=500.0, step=10.0)

    st.header("2. Datos de la Pieza")
    col_input3, col_input4 = st.columns(2)
    with col_input3:
        grados = st.number_input("Ángulo final deseado (grados):", min_value=10, max_value=180, value=90)
    with col_input4:
        ala_deseada = st.number_input("Longitud del ala deseada (mm):", min_value=5.0, value=250.0)

    if st.button("Calcular Parámetros de Máquina"):
        
        # Propiedades
        if material == "Acero Estándar (Comercial)":
            factor_fuerza = 1.0
            retorno_elastico = 1.5  
        elif material == "Acero Inoxidable":
            factor_fuerza = 1.5
            retorno_elastico = 3.0  
        else: 
            factor_fuerza = 0.5
            retorno_elastico = 1.0  
            
        # Matrices y Lógica
        matrices_disponibles = [10, 25, 35, 55]
        apertura_v_ideal = espesor * 8
        
        if apertura_v_ideal >= 55:
            v_real = 55
            alerta_sobreesfuerzo = True
        else:
            v_real = min(matrices_disponibles, key=lambda x: abs(x - apertura_v_ideal))
            alerta_sobreesfuerzo = False
            
        ancho_metros = ancho_mm / 1000.0
        tonelaje_requerido = ((68 * (espesor ** 2)) / v_real) * ancho_metros * factor_fuerza
        deduccion_simple = espesor * 1.5 
        eje_x = ala_deseada - (deduccion_simple / 2)
        angulo_maquina = grados - retorno_elastico
        ala_minima = v_real * 0.7
        radio_interior = v_real / 6

        # Mostrar Resultados
        st.subheader("📊 Resultados para el CNC")
        res_col1, res_col2 = st.columns(2)
        with res_col1:
            st.success(f"🔽 **Matriz a usar (V):** {v_real} mm")
            st.error(f"⚖️ **Tonelaje Estimado:** {tonelaje_requerido:.1f} Toneladas")
            st.success(f"📏 **Posición Eje X (Tope):** {eje_x:.2f} mm")
        with res_col2:
            st.warning(f"📐 **Ángulo a programar (Y):** {angulo_maquina:.1f}°")
            st.success(f"🔄 **Radio Interior Nat.:** {radio_interior:.2f} mm") 
            st.info(f"🛑 **Ala Mín. seguridad:** {ala_minima:.1f} mm")

        # Alertas
        if ala_deseada < ala_minima:
            st.error(f"⚠️ **¡CUIDADO!** El ala de {ala_deseada} mm es muy corta para la matriz de {v_real} mm.")
        if alerta_sobreesfuerzo:
            st.warning(f"🔥 **NOTA DE TALLER:** Placa gruesa detectada. Se asignó la matriz máxima (55mm).")

# ==========================================
# PESTAÑA 2: NUEVA CALCULADORA DE DESARROLLOS
# ==========================================
with tab2:
    st.header("Cálculo de Blank (Material a cortar)")
    st.write("Calcula la longitud total de la lámina antes de doblar, incluyendo el material que consumen las costillas.")
    
    col_d1, col_d2 = st.columns(2)
    with col_d1:
        espesor_d = st.number_input("Espesor de la lámina (mm):", min_value=0.1, value=3.0, step=0.1, key="esp_tab2")
        tramos_rectos = st.number_input("Suma de tramos rectos (mm):", min_value=1.0, value=270.0, step=10.0, help="Ejemplo plano 1: 25 + 80 + 100 + 65 = 270")
    with col_d2:
        cant_dobleces = st.number_input("Cantidad de dobleces (90°):", min_value=0, value=1, step=1)
        
    st.markdown("---")
    st.subheader("Estriado / Costillas")
    col_c1, col_c2 = st.columns(2)
    with col_c1:
        cant_costillas = st.number_input("Cantidad de costillas:", min_value=0, value=2, step=1)
    with col_c2:
        radio_costilla = st.number_input("Radio interior de costilla (mm):", min_value=1.0, value=12.7, step=0.1, help="En tu plano marca R12.7")

    if st.button("Calcular Desarrollo Total"):
        
        # 1. Material base (Los tramos rectos)
        desarrollo = tramos_rectos
        
        # 2. Restar las deducciones de los dobleces
        # Asumimos una deducción empírica de 1.5 veces el espesor por cada doblez a 90°
        deduccion_total = (espesor_d * 1.5) * cant_dobleces
        desarrollo -= deduccion_total
        
        # 3. Sumar el material de las costillas (Arcos de medio círculo)
        if cant_costillas > 0:
            # Eje neutro = radio interior + mitad del espesor
            radio_neutro = radio_costilla + (espesor_d / 2)
            # Longitud del arco (Perímetro de medio círculo = pi * r)
            longitud_una_costilla = math.pi * radio_neutro
            material_costillas = longitud_una_costilla * cant_costillas
            desarrollo += material_costillas
        else:
            material_costillas = 0
            
        # Mostrar el resultado maestro
        st.success(f"✂️ **Medida total de corte (Blank):** {desarrollo:.2f} mm")
        
        # Desglose para que el operador entienda qué sumó y qué restó
        with st.expander("Ver desglose del cálculo"):
            st.write(f"➕ Tramos rectos: {tramos_rectos} mm")
            st.write(f"➖ Deducción por dobleces: -{deduccion_total:.2f} mm")
            if cant_costillas > 0:
                st.write(f"➕ Material para costillas: +{material_costillas:.2f} mm (Aprox {longitud_una_costilla:.1f}mm cada una)")
