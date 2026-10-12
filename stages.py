import streamlit as st
import streamlit.components.v1 as components
import time
import physics
import render

def handle_laboratory_stages(valve_pos, target_dH_mm, flow_rate_air, is_turbulent, t_celsius, p_kpa):
    """
    Керує логікою кроків без лагів інтерфейсу та забезпечує чесний замір часу.
    """
    installation_placeholder = st.empty()
    instruction_placeholder = st.empty()

    if st.session_state.step == 0:
        # Крок 0: Готовність (Манометр строго на нулі)
        html_code = render.get_html_installation(valve_pos, 0.0, 'none', 'vspom', is_turbulent)
        with installation_placeholder:
            components.html(html_code, height=430, scrolling=False)
        instruction_placeholder.info("📌 **Крок 1:** Налаштуйте параметри середовища та відкриття крана. Натисніть **'Відкрити кран B'**.")

    elif st.session_state.step == 1:
        # Крок 1: Плавна стабілізація тиску (Струмінь води)
        instruction_placeholder.warning("⏳ **Перехідний режим:** Вода тече струменем. Нагнітання тиску в манометрі. Зачекайте 2 секунди...")
        
        html_code = render.get_html_installation(valve_pos, target_dH_mm, 'stream', 'vspom', is_turbulent)
        with installation_placeholder:
            components.html(html_code, height=430, scrolling=False)
        
        time.sleep(2.0)  # Даємо системі увійти в рівновагу
        st.session_state.step = 2
        st.rerun()

    elif st.session_state.step == 2:
        # Крок 2: Стаціонарний режим (Вода капає у допоміжний стакан)
        html_code = render.get_html_installation(valve_pos, target_dH_mm, 'drops', 'vspom', is_turbulent)
        with installation_placeholder:
            components.html(html_code, height=430, scrolling=False)
        instruction_placeholder.success("✅ **Тиск стабілізовано!** Вода тепер витікає краплинами, манометр зафіксувався. Натисніть кнопку **'Підставити робочий стакан'**, щоб почати замір часу.")
        
        if is_turbulent:
            st.warning("⚠️ **Увага!** Потік повітря став турбулентним. Закон Пуазейля не виконується!")

    elif st.session_state.step == 3:
        # Крок 3: Робочий замір (Секундомір працює на JS всередині картинки)
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
            * **Пройшло часу (орієнтовно):** `{elapsed} / 60 c`
            * *Вказівка:* Кнопка 'Прибрати робочий стакан' заблокована. Зачекайте 60 секунд. Сторінка оновиться автоматично після закінчення ліміту часу.
            """)
            time.sleep(1.0)
            st.rerun()
        else:
            instruction_placeholder.markdown(f"""
            🟢 **НЕОБХІДНИЙ ЧАС ДОСЯГНУТО!**
            * **Загальний час досліду:** `{elapsed} c`
            * *Вказівка:* Тепер ви можете натиснути кнопку **'Прибрати робочий стакан'** зверху на панелі керування.
            """)

    elif st.session_state.step == 4:
        # Крок 4: Фіксація та зважування
        if "start_time" in st.session_state:
            del st.session_state["start_time"]

        html_code = render.get_html_installation(valve_pos, target_dH_mm, 'drops', 'none', is_turbulent)
        with installation_placeholder:
            components.html(html_code, height=430, scrolling=False)
        
        instruction_placeholder.markdown(f"⏱️ **Час досліду успішно зафіксовано:** `{st.session_state.measured_time} с`. Натисніть кнопку нижче для зважування стакана.")
        
        if st.button("⚖️ 4. Зважити робочий стакан та записати результат", use_container_width=True):
            res = physics.generate_experiment_result(flow_rate_air, target_dH_mm/1000.0, is_turbulent, t_celsius, p_kpa, st.session_state.measured_time)
            res = {**{"№ Досліду": len(st.session_state.history) + 1}, **res}
            st.session_state.history.append(res)
            st.session_state.step = 5
            st.rerun()

    elif st.session_state.step == 5:
        # Крок 5: Закриття крана B та плавне скидання тиску
        instruction_placeholder.info("🔄 Закриття крана B... Скидання тиску та вирівнювання рівнів манометра.")
        html_code = render.get_html_installation(valve_pos, 0.0, 'none', 'vspom', is_turbulent)
        with installation_placeholder:
            components.html(html_code, height=430, scrolling=False)
        
        time.sleep(1.5)
        st.session_state.step = 0
        st.session_state.measured_time = 0.0
        st.rerun()
