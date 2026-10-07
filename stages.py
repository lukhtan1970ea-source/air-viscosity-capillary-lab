import streamlit as st
import streamlit.components.v1 as components
import time
import physics
import render

def handle_laboratory_stages(valve_pos, target_dH_mm, flow_rate_air, is_turbulent, t_celsius, p_kpa):
    """
    Керує логікою кроків без циклів тремтіння, забезпечуючи плавний рендеринг.
    """
    installation_placeholder = st.empty()
    instruction_placeholder = st.empty()

    if st.session_state.step == 0:
        # Крок 0: Готовність
        html_code = render.get_html_installation(valve_pos, target_dH_mm, 'none', 'vspom', is_turbulent)
        with installation_placeholder:
            components.html(html_code, height=430, scrolling=False)
        instruction_placeholder.info("📌 **Крок 1:** Налаштуйте параметри середовища та відкриття крана. Натисніть **'Відкрити кран B'**.")

    elif st.session_state.step == 1:
        # Крок 1: Плавна стабілізація
        instruction_placeholder.warning("⏳ **Перехідний режим:** Нагнітання тиску в манометрі. Зачекайте 2 секунди...")
        
        html_code = render.get_html_installation(valve_pos, target_dH_mm, 'stream', 'vspom', is_turbulent)
        with installation_placeholder:
            components.html(html_code, height=430, scrolling=False)
        
        time.sleep(2.0)  # Фізичне заповнення
        st.session_state.step = 2
        st.rerun()

    elif st.session_state.step == 2:
        # Крок 2: Стаціонарний режим
        html_code = render.get_html_installation(valve_pos, target_dH_mm, 'drops', 'vspom', is_turbulent)
        with installation_placeholder:
            components.html(html_code, height=430, scrolling=False)
        instruction_placeholder.success("✅ **Тиск стабілізовано!** Вода капає у допоміжний стакан. Натисніть **'Підставити робочий стакан'**.")
        
        if is_turbulent:
            st.warning("⚠️ **Увага!** Потік повітря став турбулентним. Закон Пуазейля не виконується!")

    elif st.session_state.step == 3:
        # Крок 3: Робочий замір
        if "start_time" not in st.session_state:
            st.session_state.start_time = time.time()

        elapsed = int(time.time() - st.session_state.start_time)
        st.session_state.measured_time = elapsed

        html_code = render.get_html_installation(valve_pos, target_dH_mm, 'drops', 'work', is_turbulent)
        with installation_placeholder:
            components.html(html_code, height=430, scrolling=False)

        if elapsed < 60:
            instruction_placeholder.markdown(f"""
            🔴 **ТРИВАЄ ВИМІРЮВАННЯ:**
            * **Пройшло часу:** ` {elapsed} / 60 c `
            * *Вказівка:* Зачекайте 60 секунд. Натисніть **'Оновити секундомір'**, щоб побачити актуальний час.
            """)
            st.button("🔄 Оновити секундомір", use_container_width=True)
        else:
            instruction_placeholder.markdown(f"""
            🟢 **НЕОБХІДНИЙ ЧАС ДОСЯГНУТО!**
            * **Поточний час досліду:** ` {elapsed} c `
            * *Вказівка:* Тепер ви можете натиснути кнопку **'Прибрати робочий стакан'** зверху.
            """)
            st.button("🔄 Оновити стан установки", use_container_width=True)

    elif st.session_state.step == 4:
        # Крок 4: Фіксація та зважування
        if "start_time" in st.session_state:
            del st.session_state["start_time"]

        html_code = render.get_html_installation(valve_pos, target_dH_mm, 'drops', 'none', is_turbulent)
        with installation_placeholder:
            components.html(html_code, height=430, scrolling=False)
        
        instruction_placeholder.markdown(f"⏱️ **Час зафіксовано:** `{st.session_state.measured_time} с`. Натисніть кнопку нижче для запису результату.")
        
        if st.button("⚖️ 4. Зважити робочий стакан та записати результат", use_container_width=True):
            res = physics.generate_experiment_result(flow_rate_air, target_dH_mm/1000.0, is_turbulent, t_celsius, p_kpa, st.session_state.measured_time)
            res = {**{"№ Досліду": len(st.session_state.history) + 1}, **res}
            st.session_state.history.append(res)
            st.session_state.step = 5
            st.rerun()

    elif st.session_state.step == 5:
        # Крок 5: Скидання манометра
        instruction_placeholder.info("🔄 Закриття крана B... Скидання тиску.")
        html_code = render.get_html_installation(valve_pos, 0.0, 'none', 'vspom', is_turbulent)
        with installation_placeholder:
            components.html(html_code, height=430, scrolling=False)
        
        time.sleep(1.0)
        st.session_state.step = 0
        st.session_state.measured_time = 0.0
        st.rerun()
