import streamlit as st
import physics
import stages

# Налаштування сторінки Streamlit
st.set_page_config(page_title="Лабораторна робота: В'язкість повітря", layout="wide")

st.title("🔬 Віртуальна лабораторна робота")
st.subheader("Визначення коефіцієнта в'язкості, середньої довжини вільного пробігу та ефективного діаметра молекул повітря")

if "step" not in st.session_state:
    st.session_state.step = 0
if "current_dH" not in st.session_state:
    st.session_state.current_dH = 0.0
if "measured_time" not in st.session_state:
    st.session_state.measured_time = 0.0
if "history" not in st.session_state:
    st.session_state.history = []

col_sidebar, col_main = st.columns([1, 2])

with col_sidebar:
    st.header("⚙️ Параметри середовища")
    disabled_inputs = st.session_state.step != 0
    t_celsius = st.slider("Кімнатна температура t, °C", min_value=15.0, max_value=30.0, value=21.0, step=0.5, disabled=disabled_inputs)
    p_kpa = st.slider("Атмосферний тиск Pa, кПа", min_value=95.0, max_value=105.0, value=100.5, step=0.05, disabled=disabled_inputs)

    st.header("🚰 Управління установкою")
    valve_pos = st.slider("Ступінь відкриття крана B, %", min_value=0, max_value=100, value=50, step=5, disabled=disabled_inputs)
    
    st.markdown("---")
    st.markdown(f"""
    **Довідкові дані установки:**
    * Довжина капіляра $L = {physics.L}$ м
    * Радіус капіляра $R = {physics.R_cap}$ м
    * Рідина в манометрі: Вода ($\rho = 1000$ кг/м³)
    """)

# Фізичні розрахунки
delta_H_nominal, flow_rate_air, Re, is_turbulent = physics.calculate_flow_and_reynolds(valve_pos, t_celsius, p_kpa)
target_dH_mm = delta_H_nominal * 1000.0

with col_main:
    st.header("📊 Вимірювальна установка та анімація")
    
    # Кнопки керування кроками вимірювання (з правильними відступами)
    col_b1, col_b2, col_b3 = st.columns(3)
    with col_b1:
        if st.button("▶️ 1. Відкрити кран B", use_container_width=True, disabled=st.session_state.step != 0 or valve_pos == 0):
            st.session_state.step = 1
            st.rerun()
            
    with col_b2:
        if st.button("📥 2. Підставити робочий стакан", use_container_width=True, disabled=st.session_state.step != 2):
            st.session_state.step = 3
            st.rerun()
            
    with col_b3:
        if st.button("📤 3. Прибрати робочий стакан", use_container_width=True, disabled=st.session_state.step != 3):
            st.session_state.step = 4
            st.rerun()

    # Передаємо керування у stages
    stages.handle_laboratory_stages(valve_pos, target_dH_mm, flow_rate_air, is_turbulent, t_celsius, p_kpa)

    # --- ТАБЛИЦЯ РЕЗУЛЬТАТІВ ---
    st.header("📋 Протокол вимірювань (Дані для обробки студентом)")
    if st.session_state.history:
        st.dataframe(st.session_state.history, use_container_width=True)
        if st.button("🗑️ Очистити таблицю дослідів", disabled=st.session_state.step != 0):
            st.session_state.history = []
            st.rerun()
    else:
        st.write("Таблиця порожня. Проведіть повний цикл вимірювань за кроками 1-4.")

   
