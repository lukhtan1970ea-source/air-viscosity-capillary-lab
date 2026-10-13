# render.py
import layout

def get_html_installation(valve_pos, target_dH_mm, flow_mode, cup_type, is_turbulent, current_time_sec=0.0):
    """
    Збирає лабораторну установку, підставляючи змінні у стабільний шаблон.
    Додано захист (Math.min) від виходу рідини за межі трубок манометра на великих значеннях.
    """
    valve_angle = (valve_pos / 100.0) * 90.0 if flow_mode != 'none' else 0.0
    
    # Перекладаємо мм у пікселі (1 мм = 0.6 пікселя)
    raw_delta_px = (target_dH_mm * 0.6) if flow_mode != 'none' else 0.0
    
    # ЖОРСТКИЙ ЛІМІТАТОР: манометр на схемі закінчується на висоті 75 пікселів (відмітка 120 мм).
    # Обмежуємо максимальний зсув, щоб рідина фізично не могла вилізти з трубки.
    delta_px = min(raw_delta_px, 72.0)
    
    timer_display = "block" if cup_type == 'work' else "none"
    js_mode = 1 if flow_mode in ['stream', 'drops'] else 0
    js_initial_shift = 0.0 if flow_mode == 'stream' else delta_px

    # Нативний клієнтський скрипт із захистом від кракозябр (Math.min)
    js_engine = f"""
    <script>
        let currentShift = {js_initial_shift}; 
        const targetShift = {delta_px};
        const mode = {js_mode};
        
        function animateManometer() {{
            if (mode === 1) {{
                if (currentShift < targetShift) {{
                    currentShift += (targetShift - currentShift) * 0.015 + 0.02;
                    if (currentShift > targetShift) currentShift = targetShift;
                }}
            }} else {{
                if (currentShift > 0) {{
                    currentShift -= currentShift * 0.08 + 0.1;
                    if (currentShift < 0) currentShift = 0;
                }}
            }}
            
            // Додатковий ультра-захист у браузері: обмежуємо зсув на рівні 72 пікселів
            let safeShift = Math.min(currentShift, 72.0);
            
            let leftY = (280 + safeShift).toFixed(1);
            let rightY = (280 - safeShift).toFixed(1);
            
            let newPath = `M 110,${{leftY}} L 110,350 Q 110,370 140,370 Q 170,370 170,350 L 170,${{rightY}}`;
            document.getElementById('v-water-contour').setAttribute('d', newPath);
            
            requestAnimationFrame(animateManometer);
        }}
        
        if ("{cup_type}" === "work") {{
            let start = Date.now() - ({current_time_sec} * 1000);
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
        @keyframes fill_vessel {
            0% { transform: translateY(0px); }
            100% { transform: translateY(15px); }
        }
        .vessel-water { animation: fill_vessel 60s linear forwards; }
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

    cup_element = ""
    if cup_type == 'vspom':
        cup_element = """
        <path d="M 300,385 L 303,425 Q 320,428 337,425 L 340,385" fill="none" stroke="#6c757d" stroke-width="2.5" />
        <path d="M 299,412 Q 320,414 341,412 L 342,427 Q 320,430 301,427 Z" fill="rgba(108, 117, 125, 0.35)" />
        <text x="320" y="405" font-family="sans-serif" font-size="10" fill="#555" text-anchor="middle">Допоміжний</text>
        """
    elif cup_type == 'work':
        css_animation += """
        @keyframes fill_cup {
            from { transform: scaleY(0); transform-origin: 320px 425px; }
            to { transform: scaleY(1); transform-origin: 320px 425px; }
        }
        .cup-water-grow { animation: fill_cup 60s linear forwards; }
        """
        cup_element = f"""
        <path d="M 300,385 L 303,425 Q 320,428 337,425 L 340,385" fill="none" stroke="#0056b3" stroke-width="2.5" />
        <path d="M 301.5,400 Q 320,402 338.5,400 L 339.5,424 Q 320,427 302.5,424 Z" fill="rgba(0, 123, 255, 0.5)" class="cup-water-grow" />
        <text x="320" y="375" font-family="sans-serif" font-size="11" fill="#0056b3" font-weight="bold" text-anchor="middle">РОБОЧИЙ</text>
        """

    # Фіксуємо початковий безпечний кадр для запобігання мікро-стрибкам
    safe_initial_shift = min(js_initial_shift, 72.0)
    init_left_y = 280.0 + safe_initial_shift
    init_right_y = 280.0 - safe_initial_shift

    return layout.BASE_TEMPLATE.format(
        timer_display=timer_display,
        css_animation=css_animation,
        init_left_y=init_left_y,
        init_right_y=init_right_y,
        valve_angle=valve_angle,
        bubbles=bubbles,
        cup_element=cup_element,
        water_flow_element=water_flow_element,
        js_engine=js_engine
    )
