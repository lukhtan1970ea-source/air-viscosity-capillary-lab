# stages.py
import streamlit as st
import streamlit.components.v1 as components
import time
import physics
import render

def handle_laboratory_stages(valve_pos, target_dH_mm, flow_rate_air, is_turbulent, t_celsius, p_kpa):
    """
    Керує етапами досліду за допомогою нативної JS анімації на клієнті.
    Адаптовано під мобільні екрани (Responsive Viewport).
    """
    installation_placeholder = st.empty()
    instruction_placeholder = st.empty()

    # Передаємо половину повної дельти для графічного зсуву одного коліна (0.5 * target)
    visual_dH = target_dH_mm * 0.5

    # Вбудована CSS-функція для безпечного рендерингу компонента на мобільних пристроях
    def render_responsive_html(html_markup):
        with installation_placeholder:
            components.html(
                f"<div style='width:100%; overflow:hidden;'>{html_markup}</div>", 
                height=430, 
                scrolling=False
            )


    if st.session_state.step == 0:
        # Крок 0: Готовність
        html_code = render.get_html_installation(valve_pos, visual_dH, 'none', 'vspom', is_turbulent)
        render_responsive_html(html_code)
        instruction_placeholder.info("📌 **Крок 1:** Налаштуйте параметри середовища та відкриття крана B. Натисніть **'Відкрити кран B'**.")

    elif st.session_state.step == 1:
        # Крок 1: Перехідний режим
        html_code = render.get_html_installation(valve_pos, visual_dH, 'stream', 'vspom', is_turbulent)
        render_responsive_html(html_code)
            
        instruction_placeholder.warning("⏳ **Перехідний режим:** Вода тече струменем. Нагнітання тиску в манометрі. Зачекайте стабілізації системи (~6 секунд)...")
        
        time.sleep(6.0)
        st.session_state.step = 2
        st.rerun()

    elif st.session_state.step == 2:
        # Крок 2: Стаціонарний режим
        html_code = render.get_html_installation(valve_pos, visual_dH, 'drops', 'vspom', is_turbulent)
        render_responsive_html(html_code)
        instruction_placeholder.success("✅ **Тиск стабілізовано!** Вода витікає краплинами. Натисніть кнопку **'Підставити робочий стакан'**.")
        
        if is_turbulent:
            st.warning("⚠️ **Увага!** Потік повітря став турбулентним. Закон Пуазейля не виконується!")

    elif st.session_state.step == 3:
        # Крок 3: Робочий замір часу
        if "start_time" not in st.session_state:
            st.session_state.start_time = time.time()

        elapsed = int(time.time() - st.session_state.start_time)
        st.session_state.measured_time = elapsed

        html_code = render.get_html_installation(valve_pos, visual_dH, 'drops', 'work', is_turbulent, current_time_sec=elapsed)
        render_responsive_html(html_code)

        if elapsed < 60:
            instruction_placeholder.markdown(f"""
            🔴 **ТРИВАЄ ВИМІРЮВАННЯ (Секундомір працює автоматично на схемі):**
            * **Пройшло часу на сервері:** `{elapsed} / 60 c`
            * *Вказівка:* Чекайте виконання нормативу (не менше 60 секунд). Для оновлення натисніть кнопку 'Оновити таймер' нижче.
            """)
            st.button("🔄 Оновити таймер", use_container_width=True)
        else:
            instruction_placeholder.markdown(f"""
            🟢 **НОРМАТИВ ЧАСУ ВИКОНАНО!**
            * **Загальний зафіксований час досліду:** `{elapsed} c`
            * *Вказівка:* Натисніть кнопку **'3. Прибрати робочий стакан'** на верхній панелі.
            """)
            st.button("🔄 Оновити стан установки", use_container_width=True)

    elif st.session_state.step == 4:
        # Крок 4: Фіксація результатів
        if "start_time" in st.session_state:
            st.session_state.measured_time = int(time.time() - st.session_state.start_time)
            del st.session_state["start_time"]

        html_code = render.get_html_installation(valve_pos, visual_dH, 'drops', 'vspom', is_turbulent)
        render_responsive_html(html_code)
        
        instruction_placeholder.markdown(f"⏱️ **Час досліду зафіксовано:** `{st.session_state.measured_time} с`. Натисніть кнопку нижче для запису результату.")
        
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
        render_responsive_html(html_code)
        
        time.sleep(2.0)
        st.session_state.step = 0
        st.session_state.measured_time = 0.0
        st.rerun()
