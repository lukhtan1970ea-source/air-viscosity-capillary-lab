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
    
    col_b1, col_b2, col_b3 = st.columns(3)
    with col_b1:
        if st.button("▶️ 1. Відкрити кран B", use_container_width=True, disabled=st.session_state.step != 0 or valve_pos == 0):
            st.session_state.step = 1
            st.rerun()
            
    with col_b2:
        if st.button("📥 2. Підставити робочий стакан", use_container_width=True, disabled=st.session_state.step != 2):
            st.session_state.step = 3
            st.session_state.measured_time = 0.0
            st.rerun()
            
    with col_b3:
        time_lock = st.session_state.measured_time < 60.0 if st.session_state.step == 3 else True
        if st.button("📤 3. Прибрати робочий стакан", use_container_width=True, disabled=time_lock):
            st.session_state.step = 4
            st.rerun()

    # Передаємо керування у stages
    stages.handle_laboratory_stages(valve_pos, target_dH_mm, flow_rate_air, is_turbulent, t_celsius, p_kpa)

    # --- ТАБЛИЦЯ РЕЗУЛЬТАТІВ ---
    st.header("📋 Прокотол вимірювань (Дані для обробки студентом)")
    if st.session_state.history:
        st.dataframe(st.session_state.history, use_container_width=True)
        if st.button("🗑️ Очистити таблицю дослідів", disabled=st.session_state.step != 0):
            st.session_state.history = []
            st.rerun()
    else:
        st.write("Таблиця порожня. Проведіть повний цикл вимірювань за кроками 1-4.")

    # --- МЕТОДИЧНИЙ ПРОВІДНИК ---
    with st.expander("📚 Розрахункові формули та хід роботи"):
        st.markdown(r"""
        ### Порядок виконання розрахунків:
        
        1. **Визначення маси витеклої води:**
           $$m_{\text{води}} = m - m_0$$
           Оскільки густина води $\rho_ж = 1.0 \text{ г/см}^3$, отримане значення маси в грамах чисельно дорівнює об'єму витеклої води (а отже, і об'єму повітря $V$, що пройшло крізь капіляр) у кубічних сантиметрах ($\text{см}^3$). **Переведіть об'єм $V$ у метри кубічні ($m^3$) для подальших розрахунків!**
        
        2. **Розрахунок різниці тисків на кінцях капіляра:**
           $$\Delta P = \rho_ж \cdot g \cdot \Delta H$$
           де $\rho_ж = 1000 \text{ кг/м}^3$, $g = 9.81 \text{ м/с}^2$, $\Delta H$ — перевести з міліметрів у метри.
        
        3. **Розрахунок коефіцієнта динамічної в'язкості повітря $\eta$ (Формула Пуазейля):**
           $$\eta = \frac{\pi \cdot R^4 \cdot \Delta P \cdot \tau}{8 \cdot L \cdot V}$$
           де $R = 0.00035 \text{ м}$, $L = 2.14 \text{ м}$, $\tau$ — час досліду в секундах.
        
        4. **Розрахунок густини повітря $\rho$:**
           $$\rho = \frac{P_a \cdot \mu}{R_{\text{gas}} \cdot T}$$
           де $\mu = 0.029 \text{ кг/моль}$, $R_{\text{gas}} = 8.314 \text{ Дж/(моль}\cdot\text{К)}$, $T = t(^\circ\text{C}) + 273.15$, $P_a$ — атмосферний тиск у Паскалях.
        
        5. **Розрахунок середньої арифметичної швидкості молекул $V_{cp}$:**
           $$V_{cp} = \sqrt{\frac{8 \cdot R_{\text{gas}} \cdot T}{\pi \cdot \mu}}$$
        
        6. **Розрахунок середньої довжини вільного пробігу $\lambda$:**
           $$\lambda = \frac{3\eta}{\rho V_{cp}}$$
        
        7. **Розрахунок ефективного діаметра молекули повітря $G$:**
           $$G = \sqrt{\frac{k_B \cdot T}{\sqrt{2} \cdot \pi \cdot \lambda \cdot P_a}}$$
           де $k_B = 1.38 \cdot 10^{-23} \text{ Дж/К}$.
        """)
