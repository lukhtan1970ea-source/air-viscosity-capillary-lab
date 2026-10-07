import streamlit as st
import streamlit.components.v1 as components
import time

# Импортируем физику и рендеринг
import physics
import render

def handle_laboratory_stages(valve_pos, target_dH_mm, flow_rate_air, is_turbulent, t_celsius, p_kpa):
    """
    Управляє станами кінцевого автомата лабораторної роботи,
    виводить відповідні візуалізації установки та текстові інструкції для студентів.
    """
    # Слот для анімаційного вікна та текстових інструкцій
    installation_placeholder = st.empty()
    instruction_placeholder = st.empty()

    if st.session_state.step == 0:
        # Крок 0: Готовність до роботи
        st.session_state.current_dH = 0.0
        html_code = render.get_html_installation(valve_pos, target_dH_mm, 0.0, 'none', 0.0, 'vspom', is_turbulent)
        with installation_placeholder:
            components.html(html_code, height=430, scrolling=False)
        instruction_placeholder.info("📌 **Крок 1:** Налаштуйте параметри середовища та ступінь відкриття крана B. Натисніть **'Відкрити кран B'**, щоб почати стабілізацію системи.")

    elif st.session_state.step == 1:
        # Крок 1: Перехідний режим (Вода струменем, тиск росте)
        instruction_placeholder.warning("⏳ **Перехідний режим:** Вода тече струменем. Повітря закачується у судину. Зачекайте, поки різниця рівнів у манометрі стабілізується...")
        
        # Анімація плавного підйому манометра
        for i in range(1, 16):
            st.session_state.current_dH = (i / 15.0) * target_dH_mm
            html_code = render.get_html_installation(valve_pos, target_dH_mm, st.session_state.current_dH, 'stream', i * 0.2, 'vspom', is_turbulent)
            with installation_placeholder:
                components.html(html_code, height=430, scrolling=False)
            time.sleep(0.08)
            
        st.session_state.step = 2
        st.rerun()

    elif st.session_state.step == 2:
        # Крок 2: Стаціонарний режим (Вода капає у допоміжний стакан)
        html_code = render.get_html_installation(valve_pos, target_dH_mm, target_dH_mm, 'drops', time.time(), 'vspom', is_turbulent)
        with installation_placeholder:
            components.html(html_code, height=430, scrolling=False)
        instruction_placeholder.success("✅ **Тиск стабілізовано!** Вода тепер витікає краплинами, манометр зафіксувався. Натисніть кнопку **'Підставити робочий стакан'**, щоб одночасно увімкнути секундомір та почати замір.")
        
        if is_turbulent:
            st.warning("⚠️ **Увага!** Потік повітря турбулентний (\(Re > 1500\)). Манометр тремтить. Закон Пуазейля не виконується! Закрийте кран та прикрийте його менше.")

    elif st.session_state.step == 3:
        # Крок 3: Замір часу (Активний секундомір, вода в робочий стакан)
        sim_loop_time = 0.0
        
        while st.session_state.step == 3:
            st.session_state.measured_time += 1.0
            sim_loop_time += 1.0
            
            html_code = render.get_html_installation(valve_pos, target_dH_mm, target_dH_mm, 'drops', sim_loop_time, 'work', is_turbulent)
            with installation_placeholder:
                components.html(html_code, height=430, scrolling=False)
            
            # Підсвічування таймера: червоний до 60с, зелений після
            if st.session_state.measured_time < 60.0:
                instruction_placeholder.markdown(f"""
                🔴 **ТРИВАЄ ВИМІРЮВАННЯ (Секундомір увімкнено):**
                * **Пройшло часу:** ` {st.session_state.measured_time} / 60 c ` (Кнопка фіксації заблокована)
                * *Вказівка:* Для точності досліду зачекайте не менше 60 секунд!
                """)
            else:
                instruction_placeholder.markdown(f"""
                🟢 **НЕОБХІДНИЙ ЧАС ДОСЯГНУТО:**
                * **Поточний час досліду:** ` {st.session_state.measured_time} c `
                * *Вказівка:* Ви можете продовжувати дослід для більшої кількості води, або натиснути **'Прибрати робочий стакан'** для завершення заміру.
                """)
                
            if is_turbulent:
                st.warning("⚠️ Потік повітря став турбулентним! Манометр нестабільний.")
                
            time.sleep(0.05)  # Віртуальне прискорення часу
            st.rerun()

    elif st.session_state.step == 4:
        # Крок 4: Фіксація результатів та зважування
        html_code = render.get_html_installation(valve_pos, target_dH_mm, target_dH_mm, 'drops', 0.0, 'none', is_turbulent)
        with installation_placeholder:
            components.html(html_code, height=430, scrolling=False)
            
        instruction_placeholder.markdown(f"⏱️ **Час зафіксовано:** `{st.session_state.measured_time} с`. Робочий стакан з водою знято з установки та відправлено на лабораторні ваги.")
        
        # Кнопка фіксації результату
        if st.button("⚖️ 4. Зважити робочий стакан та записати результат", use_container_width=True):
            res = physics.generate_experiment_result(flow_rate_air, target_dH_mm/1000.0, is_turbulent, t_celsius, p_kpa, st.session_state.measured_time)
            res = {**{"№ Досліду": len(st.session_state.history) + 1}, **res}
            st.session_state.history.append(res)
            st.session_state.step = 5
            st.rerun()

    elif st.session_state.step == 5:
        # Крок 5: Скидання манометра на нуль
        instruction_placeholder.info("🔄 Закриття крана B... Тиск у системи вирівнюється з атмосферним.")
        
        for i in range(15, -1, -1):
            st.session_state.current_dH = (i / 15.0) * target_dH_mm
            html_code = render.get_html_installation(valve_pos, target_dH_mm, st.session_state.current_dH, 'none', 0.0, 'vspom', is_turbulent)
            with installation_placeholder:
                components.html(html_code, height=430, scrolling=False)
            time.sleep(0.05)
            
        st.session_state.step = 0
        st.session_state.measured_time = 0.0
        st.rerun()

