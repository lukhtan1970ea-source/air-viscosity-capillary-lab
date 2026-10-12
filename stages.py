import streamlit as st
import streamlit.components.v1 as components
import time
import physics
import render

def handle_laboratory_stages(valve_pos, target_dH_mm, flow_rate_air, is_turbulent, t_celsius, p_kpa):
    """
    Керує етапами досліду. Фаза струменя збільшена для реалістичності, 
    а замір часу синхронізовано з кнопкою активації.
    """
    installation_placeholder = st.empty()
    instruction_placeholder = st.empty()

    if st.session_state.step == 0:
        # Крок 0: Готовність (Манометр на нулі)
        html_code = render.get_html_installation(valve_pos, 0.0, 'none', 'vspom', is_turbulent)
        with installation_placeholder:
            components.html(html_code, height=430, scrolling=False)
        instruction_placeholder.info("📌 **Крок 1:** Налаштуйте параметри середовища та відкриття крана. Натисніть **'Відкрити кран B'**.")

    elif st.session_state.step == 1:
        # Крок 1: ТРИВАЛА фаза струменя та нарастання тиску (Збільшено до ~8 секунд)
        instruction_placeholder.warning("⏳ **Перехідний режим:** Вода тече струменем. Нагнітання тиску в манометрі та витіснення повітря. Будь ласка, зачекайте...")
        
        total_frames = 40
        for i in range(1, total_frames + 1):
            # Асимптотичне уповільнення підйому стовпчика рідини для реалістичності
            progress = 1.0 - (0.1 ** (i / (total_frames / 2.0)))
            animated_dH = progress * target_dH_mm
            
            html_code = render.get_html_installation(valve_pos, animated_dH, 'stream', 'vspom', is_turbulent)
            with installation_placeholder:
                components.html(html_code, height=430, scrolling=False)
            time.sleep(0.18)  # Сумарно фаза займає близько 7.2 секунд
            
        st.session_state.step = 2
        st.rerun()

    elif st.session_state.step == 2:
        # Крок 2: Стаціонарний режим (Перехід на краплі)
        html_code = render.get_html_installation(valve_pos, target_dH_mm, 'drops', 'vspom', is_turbulent)
        with installation_placeholder:
            components.html(html_code, height=430, scrolling=False)
        instruction_placeholder.success("✅ **Тиск повністю стабілізовано!** Перехідний процес завершено, вода витікає краплинами. Натисніть кнопку **'Підставити робочий стакан'**, щоб почати замір часу.")
        
        if is_turbulent:
            st.warning("⚠️ **Увага!** Потік повітря став турбулентним. Закон Пуазейля не виконується!")

    elif st.session_state.step == 3:
        # Крок 3: Робочий замір часу з примусовим автооновленням для точного зняття блокування
        if "start_time" not in st.session_state:
            st.session_state.start_time = time.time()

        elapsed = int(time.time() - st.session_state.start_time)
        st.session_state.measured_time = elapsed

        html_code = render.get_html_installation(valve_pos, target_dH_mm, 'drops', 'work', is_turbulent)
        with installation_placeholder:
            components.html(html_code, height=430, scrolling=False)

        if elapsed < 60:
            instruction_placeholder.markdown(f"""
            🔴 **ТРИВАЄ ВИМІРЮВАННЯ (Секундомір працює автоматично на схемі):**
            * **Пройшло часу на сервері:** `{elapsed} / 60 c`
            * *Вказівка:* Кнопка вище заблокована. Чекайте виконання нормативу (не менше 60 секунд). Сигнал розблокування подається автоматично.
            """)
            time.sleep(0.8)
            st.rerun()
        else:
            instruction_placeholder.markdown(f"""
            🟢 **НОРМАТИВ ЧАСУ ВИКОНАНО!**
            * **Загальний зафіксований час досліду:** `{elapsed} c`
            * *Вказівка:* Вимірювання можна завершувати. Натисніть кнопку **'Прибрати робочий стакан'** на панелі керування.
            """)

    elif st.session_state.step == 4:
        # Крок 4: Фіксація результатів
        if "start_time" in st.session_state:
            del st.session_state["start_time"]

        html_code = render.get_html_installation(valve_pos, target_dH_mm, 'drops', 'none', is_turbulent)
        with installation_placeholder:
            components.html(html_code, height=430, scrolling=False)
        
        instruction_placeholder.markdown(f"⏱️ **Час досліду зафіксовано:** `{st.session_state.measured_time} с`. Робочий стакан знято. Натисніть кнопку нижче для запису результату.")
        
        if st.button("⚖️ 4. Зважити робочий стакан та записати результат", use_container_width=True):
            res = physics.generate_experiment_result(flow_rate_air, target_dH_mm/1000.0, is_turbulent, t_celsius, p_kpa, st.session_state.measured_time)
            res = {**{"№ Досліду": len(st.session_state.history) + 1}, **res}
            st.session_state.history.append(res)
            st.session_state.step = 5
            st.rerun()

    elif st.session_state.step == 5:
        # Крок 5: Закриття крана B та плавне скидання тиску
        instruction_placeholder.info("🔄 Закриття крана B... Вирівнювання рівнів манометра з атмосферним тиском.")
        
        # Плавне повернення рівнів манометра на нуль при закритті
        for i in range(12, -1, -1):
            animated_dH = (i / 12.0) * target_dH_mm
            html_code = render.get_html_installation(valve_pos, animated_dH, 'none', 'vspom', is_turbulent)
            with installation_placeholder:
                components.html(html_code, height=430, scrolling=False)
            time.sleep(0.08)
            
        st.session_state.step = 0
        st.session_state.measured_time = 0.0
        st.rerun()
