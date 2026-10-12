import layout

def get_html_installation(valve_pos, target_dH_mm, flow_mode, cup_type, is_turbulent):
    """
    Модуль збірки інтерфейсу лабораторної роботи. 
    Імпортує контур сцени з layout і нативно підставляє змінні.
    """
    valve_angle = (valve_pos / 100.0) * 90.0 if flow_mode != 'none' else 0.0
    delta_px = (target_dH_mm * 0.6) if flow_mode != 'none' else 0.0
    js_mode = 1 if flow_mode in ['stream', 'drops'] else 0

    # Нативний JS-двигун
    js_engine = f"""
    <script>
        let currentShift = 0;
        const targetShift = {delta_px};
        const mode = {js_mode};
        
        function animateManometer() {{
            if (mode === 1) {{
                if (currentShift < targetShift) {{
                    currentShift += (targetShift - currentShift) * 0.05 + 0.1;
                    if (currentShift > targetShift) currentShift = targetShift;
                }}
            }} else {{
                if (currentShift > 0) {{
                    currentShift -= currentShift * 0.1 + 0.2;
                    if (currentShift < 0) currentShift = 0;
                }}
            }}
            document.getElementById('left-knee').setAttribute('y2', (280 + currentShift).toFixed(1));
            document.getElementById('right-knee').setAttribute('y2', (280 - currentShift).toFixed(1));
            requestAnimationFrame(animateManometer);
        }}
        
        if ("{cup_type}" === "work") {{
            let start = Date.now();
            setInterval(() => {{
                let diff = (Date.now() - start) / 1000;
                document.getElementById('js-timer').textContent = diff.toFixed(1) + ' c';
            }}, 100);
        }}
        
        window.onload = () => {{
            requestAnimationFrame(animateManometer);
        }};
    </script>
    """

    css_animation = ""
    water_flow_element = ""
    bubbles = ""

    if flow_mode != 'none' and is_turbulent:
        css_animation += """
        @keyframes jitter {
            0% { transform: translateY(0px); }
            100% { transform: translateY(1.5px); }
        }
        .mano-group { animation: jitter 0.05s infinite alternate ease-in-out; }
        """

    if flow_mode == 'stream':
        water_flow_element = '<polygon points="318.5,330 321.5,330 321,395 319,395" fill="#007bff" opacity="0.8"/>'
    elif flow_mode == 'drops':
        css_animation += """
        @keyframes drop_fall {
            0% { transform: translateY(0px); opacity: 1; }
            100% { transform: translateY(65px); opacity: 0; }
        }
        .fluid-drop { animation: drop_fall 0.3s infinite linear; }
        """
        water_flow_element = '<circle cx="320" cy="335" r="3.5" fill="#007bff" class="fluid-drop" />'

    if flow_mode != 'none':
        css_animation += """
        @keyframes bubble_up {
            0% { transform: translateY(0px); opacity: 0; }
            50% { opacity: 0.8; }
            100% { transform: translateY(-90px); opacity: 0; }
        }
        .b1 { animation: bubble_up 2s infinite linear; }
        .b2 { animation: bubble_up 1.6s infinite linear 0.4s; }
        """
        bubbles = """
        <circle cx="290" cy="260" r="2" fill="none" stroke="rgba(255,255,255,0.8)" class="b1" />
        <circle cx="340" cy="270" r="2" fill="none" stroke="rgba(255,255,255,0.8)" class="b2" />
        """

    timer_display = "block" if cup_type == 'work' else "none"
    cup_element = ""
    if cup_type == 'vspom':
        cup_element = """
        <path d="M 295,385 L 300,428 Q 320,431 340,428 L 345,385" fill="none" stroke="#6c757d" stroke-width="2.5" />
        <path d="M 299,412 Q 320,414 341,412 L 342,427 Q 320,430 301,427 Z" fill="rgba(108, 117, 125, 0.35)" />
        <text x="320" y="405" font-family="sans-serif" font-size="10" fill="#555" text-anchor="middle">Допоміжний</text>
        """
    elif cup_type == 'work':
        css_animation += """
        @keyframes fill_cup {
            from { transform: scaleY(0); transform-origin: 320px 427px; }
            to { transform: scaleY(1); transform-origin: 320px 427px; }
        }
        .cup-water-grow { animation: fill_cup 60s linear forwards; }
        """
        cup_element = f"""
        <path d="M 295,385 L 300,428 Q 320,431 340,428 L 345,385" fill="none" stroke="#0056b3" stroke-width="2.5" />
        <path d="M 298.5,400 Q 320,402 341.5,400 L 342,427 Q 320,430 301,427 Z" fill="rgba(0, 123, 255, 0.5)" class="cup-water-grow" />
        <text x="320" y="375" font-family="sans-serif" font-size="11" fill="#0056b3" font-weight="bold" text-anchor="middle">РОБОЧИЙ</text>
        """

    # Формируем финальный код путем подстановки в шаблон из layout
    return layout.SVG_TEMPLATE.format(
        timer_display=timer_display,
        css_animation=css_animation,
        valve_angle=valve_angle,
        bubbles=bubbles,
        cup_element=cup_element,
        water_flow_element=water_flow_element,
        js_engine=js_engine
    )
