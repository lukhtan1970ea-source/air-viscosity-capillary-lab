import streamlit as st
import streamlit.components.v1 as components
import time
import physics
import render

def handle_laboratory_stages(valve_pos, target_dH_mm, flow_rate_air, is_turbulent, t_celsius, p_kpa):
    """
    Керує етапами досліду без циклів перевантаження сервера. 
    Усі кнопки клікаються миттєво.
    """
    installation_placeholder = st.empty()
    instruction_placeholder = st.empty()

    if st.session_state.step == 0:
        # Крок 0: Готовність (Манометр на нулі)
        html_code = render.get_html_installation(valve_pos, 0.0, 'none', 'vspom', is_turbulent)
        with installation_placeholder:
            components.html(html_code, height=430, scrolling=False)
        instruction_placeholder.info("📌 **Крок 1:** Налаштуйте параметри середовища та відкриття крана B. Натисніть **'Відкрити кран B'**.")

    elif st.session_state.step == 1:
        # Крок 1: Перехідний режим (Рендериться один раз, CSS плавно піднімає стовпчик за 8 секунд)
        html_code = render.get_html_installation(valve_pos, target_dH_mm, 'stream', 'vspom', is_turbulent)
        with installation_placeholder:
            components.html(html_code, height=430, scrolling=False)
            
        instruction_placeholder.warning("⏳ **Перехідний режим:** Вода тече струменем. Нагнітання тиску в манометрі. Зачекайте встановлення постійного тиску (очікування ~8 сек)...")
        
        # Чекаємо один раз в Python без миготіння екрана
        time.sleep(8.0)  
        st.session_state.step = 2
        st.rerun()

    elif st.session_state.step == 2:
        # Крок 2: Стаціонарний режим (Перехід на краплі)
        html_code = render.get_html_installation(valve_pos, target_dH_mm, 'drops', 'vspom', is_turbulent)
        with installation_placeholder:
            components.html(html_code, height=430, scrolling=False)
        instruction_placeholder.success("✅ **Тиск стабілізовано!** Вода витікає краплинами. Натисніть кнопку **'Підставити робочий стакан'**, щоб почати замір часу.")
        
        if is_turbulent:
            st.warning("⚠️ **Увага!** Потік повітря став турбулентним. Закон Пуазейля не виконується!")

    elif st.session_state.step == 3:
        # Крок 3: Робочий замір (Кнопки активні, секундомір крутиться на клієнті в JS плавно)
        if "start_time" not in st.session_state:
            st.session_state.start_time = time.time()

        html_code = render.get_html_installation(valve_pos, target_dH_mm, 'drops', 'work', is_turbulent)
        with installation_placeholder:
            components.html(html_code, height=430, scrolling=False)

        instruction_placeholder.markdown("""
        🟢 **ВИМІРЮВАННЯ ТРИВАЄ:**
        * Секундомір автоматично рахує час на табло вище.
        * Вода збирається в робочий стакан.
        * *Вказівка:* Коли на табло буде **більше 60 секунд**, натисніть кнопку **'3. Прибрати робочий стакан'** зверху.
        """)

    elif st.session_state.step == 4:
        # Крок 4: Перевірка ліміту часу при спробі прибрати стакан
        if "start_time" in st.session_state:
            st.session_state.measured_time = int(time.time() - st.session_state.start_time)
            del st.session_state["start_time"]

        # Якщо студент злукавив і прибрав стакан раніше 60 секунд — штрафуємо та скидаємо
        if st.session_state.measured_time < 60:
            st.session_state.step = 2
            st.error(f"❌ **Дослід зіпсовано!** Ви прибрали стакан занадто рано (всього за {st.session_state.measured_time} с). За регламентом методички час має бути не менше 60 секунд для точності! Почніть замір знову.")
            st.button("🔄 Спробувати знову", on_click=st.rerun)
        else:
            html_code = render.get_html_installation(valve_pos, target_dH_mm, 'drops', 'none', is_turbulent)
            with installation_placeholder:
                components.html(html_code, height=430, scrolling=False)
            
            instruction_placeholder.markdown(f"⏱️ **Час досліду зафіксовано:** `{st.session_state.measured_time} с`. Натисніть кнопку нижче для запису результату.")
            
            if st.button("⚖️ 4. Зважити робочий стакан та записати результат", use_container_width=True):
                res = physics.generate_experiment_result(flow_rate_air, target_dH_mm/1000.0, is_turbulent, t_celsius, p_kpa, st.session_state.measured_time)
                res = {**{"№ Досліду": len(st.session_state.history) + 1}, **res}
                st.session_state.history.append(res)
                st.session_state.step = 5
                st.rerun()

    elif st.session_state.step == 5:
        # Крок 5: Закриття крана B та плавне скидання тиску через CSS
        instruction_placeholder.info("🔄 Закриття крана B... Скидання тиску та вирівнювання рівнів манометра.")
        html_code = render.get_html_installation(valve_pos, 0.0, 'none', 'vspom', is_turbulent)
        with installation_placeholder:
            components.html(html_code, height=430, scrolling=False)
        
        time.sleep(2.0)  # Плавний спад
        st.session_state.step = 0
        st.session_state.measured_time = 0.0
        st.rerun()
