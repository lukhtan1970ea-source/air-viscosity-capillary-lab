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
        # Кнопка тепер активна ЗАВЖДИ на кроці 3. Перевірка 60 секунд робиться чесно при її натисканні!
        if st.button("📤 3. Прибрати робочий стакан", use_container_width=True, disabled=st.session_state.step != 3):
            st.session_state.step = 4
            st.rerun()
