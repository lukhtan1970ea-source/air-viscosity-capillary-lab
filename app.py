import streamlit as st
import numpy as np
import time

# Імпортуємо наші модулі фізики та графіки
import physics
import render

# Настройка сторінки Streamlit
st.set_page_config(page_title="Лабораторна робота: В'язкість повітря", layout="wide")

st.title("🔬 Віртуальна開放 лабораторна робота")
st.subheader("Визначення коефіцієнта в'язкості, середньої довжини вільного пробігу та ефективного діаметра молекул повітря")

col_sidebar, col_main = st.columns([1, 2])


with col_sidebar:
    st.header("⚙️ Параметри середовища")
    t_celsius = st.slider("Кімнатна температура t, °C", min_value=15.0, max_value=30.0, value=21.0, step=0.5)
    p_kpa = st.slider("Атмосферний тиск Pa, кПа", min_value=95.0, max_value=105.0, value=100.5, step=0.05)

    st.header("🚰 Управління установкою")
    valve_pos = st.slider("Ступінь відкриття крана B, %", min_value=0, max_value=100, value=50, step=5)
    
    st.markdown("---")
    st.markdown(f"""
    **Довідкові дані установки:**
    * Довжина капіляра \(L = {physics.L}\) м
    * Радіус капіляра \(R = {physics.R_cap}\) м
    * Рідина в манометрі: Вода (\(\rho = 1000\) кг/м³)
    """)

# --- ФІЗИЧНИЙ РОЗРАХУНОК ---
delta_H_nominal, flow_rate_air, Re, is_turbulent = physics.calculate_flow_and_reynolds(
    valve_pos, t_celsius, p_kpa
)
dH_mm_nominal = delta_H_nominal * 1000.0

if "experiment_running" not in st.session_state:
    st.session_state.experiment_running = False
if "history" not in st.session_state:
    st.session_state.history = []

with col_main:
    st.header("📊 Вимірювальна установка та анімація")
    
    col_btn1, col_btn2, col_btn3 = st.columns(3)
    with col_btn1:
        start_disabled = st.session_state.experiment_running or valve_pos == 0
        if st.button("▶️ Відкрити кран / Старт", use_container_width=True, disabled=start_disabled):
            st.session_state.experiment_running = True
            st.rerun()
            
    with col_btn2:
        if st.button("⏹️ Закрити кран / Стоп", use_container_width=True, disabled=not st.session_state.experiment_running):
            st.session_state.experiment_running = False
            
            res = physics.generate_experiment_result(
                flow_rate_air, delta_H_nominal, is_turbulent, t_celsius, p_kpa
            )
            res = {**{"№ Досліду": len(st.session_state.history) + 1}, **res}
            st.session_state.history.append(res)
            st.rerun()
            
    with col_btn3:
        if st.button("🗑️ Очистити таблицю", use_container_width=True):
            st.session_state.history = []
            st.rerun()

    # Слот контейнера
    installation_placeholder = st.empty()
    status_placeholder = st.empty()
    
    # --- ЕКРАН ПРОЦЕСУ ВИМІРЮВАННЯ (АНІМАЦІЯ) ---
    if st.session_state.experiment_running:
        sim_time = 0.0
        v_collected_cm3 = 0.0
        m0 = 62.44
        
        for step in range(60):
            if not st.session_state.experiment_running:
                break
                
            sim_time += 0.25
            v_collected_cm3 += (flow_rate_air * 0.25) * 1e6 
            current_mass = m0 + v_collected_cm3
            
            svg_code = render.get_svg_installation(
                valve_pos=valve_pos,
                dH_mm=dH_mm_nominal,
                is_running=True,
                sim_time=sim_time,
                is_turbulent=is_turbulent
            )
            
            # Пряме нативне оновлення через .html() без використання iframe
            installation_placeholder.html(svg_code)
            
            water_drops = "💧 " * (int(sim_time * 2) % 4 + 1)
            status_placeholder.markdown(f"""
            ### ⏳ Триває вимірювання...
            * **Поточний час (секундомір):** `{round(sim_time, 1)} с`
            * **Маса стакана з водою (поточна вага):** `{round(current_mass, 1)} г`
            * **Статус крана:** Вода витікає краплинами... {water_drops}
            """)
            
            if is_turbulent:
                st.warning("⚠️ УВАГА! Потік повітря став турбулентним (Число Re > 1500). Закон Пуазейля БІЛЬШЕ НЕ ВИКОНУЄТЬСЯ! Манометр нестабільний (тремтить). Терміново прикрийте кран B.")
            
            time.sleep(0.05)
            
    else:
        # Статичний стан установки
        svg_code = render.get_svg_installation(
            valve_pos=valve_pos,
            dH_mm=0.0,
            is_running=False,
            sim_time=0.0,
            is_turbulent=is_turbulent
        )
        # Виводимо графіку нативно
        installation_placeholder.html(svg_code)
        status_placeholder.info("Установка готова до роботи. Налаштуйте ступінь відкриття крана та натисніть 'Старт'.")
        
        if is_turbulent and valve_pos > 0:
            st.warning("⚠️ УВАГА! При такому ступені відкриття крана потік буде турбулентним. Закон Пуазейля не виконується! Перед запуском прикрийте кран B.")

    # --- ТАБЛИЦЯ РЕЗУЛЬТАТІВ ---
    st.header("📋 Протокол вимірювань (Дані для обробки студентом)")
    if st.session_state.history:
        st.dataframe(st.session_state.history, use_container_width=True)
    else:
        st.write("Таблиця порожня. Проведіть вимірювання, щоб отримати експериментальні дані.")

    # --- МЕТОДИЧНІ ВКАЗІВКИ ---
    with st.expander("📚 Розрахункові формули та хід роботи"):
        st.markdown(r"""
        ### Порядок виконання розрахунків:
        
        1. **Визначення маси витеклої води:**
           \[m_{\text{води}} = m - m_0\]
           Оскільки густина води \(\rho_ж = 1.0 \text{ г/см}^3\), отримане значение маси в грамах чисельно дорівнює об'єму витеклої води (а отже, і об'єму повітря V, що пройшло крізь капіляр) у кубічних сантиметрах (см³). **Переведіть об'єм V у метри кубічні (m³) для подальших розрахунків!**
        
        2. **Розрахунок різниці тисків на кінцях капіляра:**
           \[\Delta P = \rho_ж \cdot g \cdot \Delta H\]
           де \(\rho_ж = 1000 \text{ кг/м}^3\), g = 9.81 м/с², Δ H — перевести з міліметрів у метри.
        
        3. **Розрахунок коефіцієнта динамічної в'язкості повітря η (Формула Пуазейля):**
           \[\eta = \frac{\pi \cdot R^4 \cdot \Delta P \cdot \tau}{8 \cdot L \cdot V}\]
           де R = 0.00035 м, L = 2.14 м, τ — час досліду в секундах.
        
        4. **Розрахунок густини повітря ρ:**
           \[\rho = \frac{P_a \cdot \mu}{R_{\text{gas}} \cdot T}\]
           де μ = 0.029 кг/моль, \(R_{\text{gas}} = 8.314 \text{ Дж/(моль}\cdot\text{К)}\), T = t(°C) + 273.15, \(P_a\) — атмосферний тиск у Паскалях.
        
        5. **Розрахунок середньої арифметичної швидкості молекул \(V_{\text{cp}}\):**
           \[V_{\text{cp}} = \sqrt{\frac{8 \cdot R_{\text{gas}} \cdot T}{\pi \cdot \mu}}\]
        
        6. **Розрахунок середньої довжини вільного пробігу λ:**
           \[\lambda = \frac{3\eta}{\rho V_{\text{cp}}}\]
        
        7. **Розрахунок ефективного діаметра молекули повітря G:**
           \[G = \sqrt{\frac{k_B \cdot T}{\sqrt{2} \cdot \pi \cdot \lambda \cdot P_a}}\]
           де \(k_B = 1.38 \cdot 10^{-23} \text{ Дж/К}\).
        """)
