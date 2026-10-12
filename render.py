import random

def get_html_installation(valve_pos, current_dH_mm, flow_mode, cup_type, is_turbulent, current_time_sec=0.0):
    """
    Генерує схему установки з монолітним красивим манометром.
    Рівні контролюються виключно через Python, що усуває баг дублирования.
    """
    valve_angle = (valve_pos / 100.0) * 90.0 if flow_mode != 'none' else 0.0
    
    # Додаємо візуальне турбулентне тремтіння до рівня, якщо потік повітря критичний
    jitter = random.uniform(-1.5, 1.5) if (flow_mode != 'none' and is_turbulent) else 0.0
    real_dH = current_dH_mm + jitter
    
    # Розрахунок верхніх точок Y для лівого та правого стовпчиків води (Базовий 280)
    left_y = 280.0 + (real_dH * 0.6)
    right_y = 280.0 - (real_dH * 0.6)

    # Клієнтський секундомір (JS) працює ТІЛЬКИ на кроці заміру часу
    js_timer_script = ""
    timer_display = "none"
    if cup_type == 'work':
        timer_display = "block"
        js_timer_script = f"""
        <script>
            let start = Date.now() - ({current_time_sec} * 1000);
            setInterval(() => {{
                let diff = (Date.now() - start) / 1000;
                document.getElementById('js-timer').textContent = diff.toFixed(1) + ' c';
            }}, 100);
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

    # Візуалізація стаканів (Виправлено положення води, відцентровано під кран)
    cup_element = ""
    if cup_type == 'vspom':
        cup_element = """
        <path d="M 300,385 L 303,425 Q 320,428 337,425 L 340,385" fill="none" stroke="#6c757d" stroke-width="2.5" />
        <path d="M 302,410 Q 320,412 338,410 L 339,424 Q 320,427 302.5,424 Z" fill="rgba(108, 117, 125, 0.35)" />
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

    # Пряма збірка HTML рядка без використання зовнішніх модулів-макетів
    html_src = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ margin: 0; padding: 0; background-color: #f8f9fa; overflow: hidden; display: flex; flex-direction: column; align-items: center; }}
            .lbl-txt {{ font-family: sans-serif; font-size: 13px; fill: #333; font-weight: bold; }}
            .main-title {{ font-family: sans-serif; font-size: 15px; fill: #111; font-weight: bold; text-anchor: middle; }}
            .sc-txt {{ font-family: monospace; font-size: 9px; fill: #555; }}
            .timer-box {{
                display: {timer_display};
                position: absolute;
                top: 75px;
                right: 40px;
                background: #333;
                color: #0f0;
                padding: 6px 12px;
                font-family: monospace;
                font-size: 18px;
                border-radius: 4px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.2);
            }}
            {css_animation}
        </style>
    </head>
    <body>
    
    <div class="timer-box">⏱️ Секундомір: <span id="js-timer">0.0 с</span></div>

    <svg width="760" height="420" viewBox="0 0 800 440" xmlns="http://w3.org" style="background-color: #ffffff; border: 1px solid #dee2e6; border-radius: 8px;">
        
        <text x="400" y="30" class="main-title">Схема експериментальної установки</text>

        <!-- 1. СУДИНА А -->
        <rect x="250" y="80" width="140" height="220" rx="10" fill="none" stroke="#555" stroke-width="3" />
        <rect x="290" y="70" width="60" height="10" fill="#333" rx="2" />
        <path d="M 251.5,150 Q 320,152 388.5,150 L 388.5,298.5 L 251.5,298.5 Z" fill="rgba(0, 123, 255, 0.23)" class="vessel-water" />
        <text x="320" y="190" class="lbl-txt" fill="#0056b3" text-anchor="middle">Судина А</text>
        {bubbles}
        
        <!-- 2. БЛОК З КАПІЛЯРОМ К -->
        <rect x="490" y="90" width="160" height="90" rx="6" fill="#f1f3f5" stroke="#adb5bd" stroke-width="2" />
        <text x="570" y="112" class="lbl-txt" text-anchor="middle">Капіляр К</text>
        <path d="M 500,140 Q 530,120 560,140 T 620,140" fill="none" stroke="#17a2b8" stroke-width="3" stroke-linecap="round" />

        <!-- 3. ГЕРМЕТИЧНІ ТРУБКИ ПО МЕТОДИЦІ -->
        <path d="M 490,140 L 320,140 L 320,80" fill="none" stroke="#555" stroke-width="2.5" />
        <path d="M 650,140 L 690,140 L 690,60" fill="none" stroke="#555" stroke-width="2.5" />
        <path d="M 350,80 L 350,60 L 140,60 L 140,200" fill="none" stroke="#555" stroke-width="2.5" />

        <!-- 4. КРАН В ТА СТАКАН -->
        <path d="M 320,300 L 320,330" fill="none" stroke="#555" stroke-width="3" />
        <circle cx="320" cy="330" r="10" fill="#6c757d" stroke="#333" stroke-width="1.5" />
        <g transform="translate(320,330) rotate({valve_angle})">
            <rect x="-4" y="-18" width="8" height="36" fill="#dc3545" rx="2" />
            <circle cx="0" cy="0" r="5" fill="#fff" />
        </g>
        <text x="345" y="335" class="lbl-txt">Кран B</text>
        
        {cup_element}
        {water_flow_element}

        <!-- 5. U-ПОДІБНИЙ МАНОМЕТР М -->
        <g class="mano-group">
            <rect x="115" y="180" width="50" height="200" fill="#fff" stroke="#ced4da" />
            <line x1="140" y1="200" x2="140" y2="360" stroke="#aaa" stroke-width="1" />
            <line x1="130" y1="280" x2="150" y2="280" stroke="#333" stroke-width="1.5" />
            <text x="154" y="283" class="sc-txt" style="font-weight:bold;">0</text>
            <line x1="133" y1="220" x2="147" y2="220" stroke="#777" stroke-width="1" />
            <text x="154" y="223" class="sc-txt">+100</text>
            <line x1="133" y1="340" x2="147" y2="340" stroke="#777" stroke-width="1" />
            <text x="154" y="343" class="sc-txt">-100</text>

            <path d="M 110,200 L 110,350 Q 110,370 140,370 Q 170,370 170,350 L 170,200" 
                  fill="none" stroke="#555" stroke-width="16" stroke-linecap="round" style="opacity: 0.15;" />

            <!-- === МОНОЛІТНЕ ЦІЛЬНЕ ВОДНЕ ТІЛО МАНОМЕТРА === -->
            <path d="M 110,{left_y} L 110,350 Q 110,370 140,370 Q 170,370 170,350 L 170,{right_y}" 
                  fill="none" stroke="royalblue" stroke-width="10" stroke-linecap="round" />
        </g>
              
        <text x="140" y="405" class="lbl-txt" fill="royalblue" text-anchor="middle">Манометр М</text>

    </svg>
    
    {js_timer_script}
    </body>
    </html>
    """
    return html_src
