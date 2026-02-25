import streamlit as st

# ==========================================
# PIEZA 6: VERSIÓN PULIDA (Sin números fantasma)
# ==========================================

st.title("🛠️ Calculadora CNC - Dobladora Pro")

st.header("1. Datos del Material")
material = st.selectbox("Tipo de Material:", ["Acero Estándar (Comercial)", "Acero Inoxidable", "Aluminio"])

col_input1, col_input2 = st.columns(2)
with col_input1:
    espesor = st.number_input("Espesor de la lámina (mm):", min_value=0.1, value=12.7,
                              step=0.1)  # Por defecto 1/2 pulgada
with col_input2:
    ancho_mm = st.number_input("Ancho a doblar (mm):", min_value=10.0, value=500.0, step=10.0)

st.header("2. Datos de la Pieza")
col_input3, col_input4 = st.columns(2)
with col_input3:
    grados = st.number_input("Ángulo final deseado (grados):", min_value=10, max_value=180, value=90)
with col_input4:
    ala_deseada = st.number_input("Longitud del ala deseada (mm):", min_value=5.0, value=250.0)

if st.button("Calcular Parámetros de Máquina"):

    # --- 1. PROPIEDADES ---
    if material == "Acero Estándar (Comercial)":
        factor_fuerza = 1.0
        retorno_elastico = 1.5
    elif material == "Acero Inoxidable":
        factor_fuerza = 1.5
        retorno_elastico = 3.0
    else:
        factor_fuerza = 0.5
        retorno_elastico = 1.0

        # --- 2. INVENTARIO DE MATRICES ---
    matrices_disponibles = [10, 25, 35, 55]
    apertura_v_ideal = espesor * 8

    # Lógica de taller: Si la teoría pide más de 55, usamos 55 directo.
    if apertura_v_ideal >= 55:
        v_real = 55
        alerta_sobreesfuerzo = True
    else:
        # Busca la más cercana a la ideal
        v_real = min(matrices_disponibles, key=lambda x: abs(x - apertura_v_ideal))
        alerta_sobreesfuerzo = False

    # --- 3. MATEMÁTICAS (Usando la matriz real) ---
    ancho_metros = ancho_mm / 1000.0
    tonelaje_requerido = ((68 * (espesor ** 2)) / v_real) * ancho_metros * factor_fuerza

    deduccion_simple = espesor * 1.5
    eje_x = ala_deseada - (deduccion_simple / 2)
    angulo_maquina = grados - retorno_elastico
    ala_minima = v_real * 0.7
    radio_interior = v_real / 6

    # --- 4. MOSTRAR RESULTADOS ---
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

    # --- 5. ALERTAS ---
    if ala_deseada < ala_minima:
        st.error(
            f"⚠️ **¡CUIDADO!** El ala de {ala_deseada} mm es muy corta para la matriz de {v_real} mm. Riesgo de resbalón.")

    if alerta_sobreesfuerzo:
        st.warning(
            f"🔥 **NOTA DE TALLER:** Placa gruesa detectada. Se asignó la matriz máxima (55mm). El tonelaje será alto, asegúrate de no exceder el límite de la máquina.")