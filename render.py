import random

def get_html_installation(valve_pos, target_dH_mm, flow_mode, cup_type, is_turbulent):
    """
    Генерує плавну HTML/CSS/SVG-анімацію установки. 
    Управління рухом передано браузеру через CSS Keyframes без циклів Python.
    """
    # Рівні рідини в манометрі (базовий Y = 280)
    left_knee_y = 280 + (target_dH_mm * 0.6)
    right_knee_y = 280 - (target_dH_mm * 0.6)
    
    # Поворот ручки крана
    valve_angle = (valve_pos / 100.0) * 90.0 if flow_mode != 'none' else 0.0
    
    # Налаштування стилів та ключових кадрів для плавності 60 FPS
    css_animation = ""
    drop_element = ""
    water_in_cup = ""
    bubbles = ""
    manometer_style = ""

    # Ефект турбулентного тремтіння манометра засобами CSS (якщо ввімкнено)
    if flow_mode != 'none' and is_turbulent:
        css_animation += """
        @keyframes jitter {
            0% { transform: translateY(0px); }
            25% { transform: translateY(-1.5px); }
            50% { transform: translateY(1.5px); }
            75% { transform: translateY(-0.8px); }
            100% { transform: translateY(0.8px); }
        }
        .v-water { animation: jitter 0.08s infinite alternate ease-in-out; }
        """
    elif flow_mode == 'stream':
        # Плавний вхід манометра в режим при першому відкритті крана
        css_animation += f"""
        @keyframes fill_mano {{
            from {{ stroke-dashoffset: 300; }}
            to {{ stroke-dashoffset: 0; }}
        }}
        """

    # Режими витікання води
    if flow_mode == 'stream':
        # Струмінь води (статичний красивий елемент)
        drop_element = '<line x1="320" y1="330" x2="320" y2="385" stroke="#007bff" stroke-width="4" />'
    elif flow_mode == 'drops':
        # Нескінченна плавна крапля через CSS
        css_animation += """
        @keyframes falling_drop {
            0% { translateY(0px); opacity: 1; }
            80% { opacity: 1; }
            100% { transform: translateY(55px); opacity: 0; }
        }
        .water-drop { animation: falling_drop 0.4s infinite linear; }
        """
        drop_element = '<circle cx="320" cy="330" r="3.5" fill="#007bff" class="water-drop" />'

    # Анімація бульбашок повітря через CSS
    if flow_mode != 'none':
        css_animation += """
        @keyframes bubble_up {
            0% { transform: translateY(0px); opacity: 0; }
            10% { opacity: 0.8; }
            90% { opacity: 0.8; }
            100% { transform: translateY(-100px); opacity: 0; }
        }
        .b1 { animation: bubble_up 2s infinite linear; }
        .b2 { animation: bubble_up 2.5s infinite linear 0.7s; }
        .b3 { animation: bubble_up 1.8s infinite linear 1.3s; }
        """
        bubbles = """
        <circle cx="280" cy="270" r="2.5" fill="none" stroke="rgba(255,255,255,0.7)" class="b1" />
        <circle cx="320" cy="280" r="2.5" fill="none" stroke="rgba(255,255,255,0.7)" class="b2" />
        <circle cx="350" cy="265" r="2.5" fill="none" stroke="rgba(255,255,255,0.7)" class="b3" />
        """

    # Наповнення робочого стакана (анімація на 60 секунд)
    if cup_type == 'vspom':
        cup_element = """
        <path d="M 295,385 L 300,430 Q 320,433 340,430 L 345,385" fill="none" stroke="#777" stroke-width="2.5" />
        <path d="M 299,410 Q 320,412 341,410 L 343,430 Q 320,433 301,430 Z" fill="rgba(108, 117, 125, 0.4)" />
        <text x="320" y="405" font-family="sans-serif" font-size="10" fill="#555" text-anchor="middle">Допоміжний</text>
        """
    elif cup_type == 'work':
        # Поступове підняття рівня води в стакані за 60 секунд
        css_animation += """
        @keyframes fill_cup {
            from { transform: scaleY(0); transform-origin: bottom; }
            to { transform: scaleY(1); transform-origin: bottom; }
        }
        .cup-water { animation: fill_cup 60s linear forwards; }
        """
        cup_element = f"""
        <path d="M 295,385 L 300,430 Q 320,433 340,430 L 345,385" fill="none" stroke="#0056b3" stroke-width="2.5" />
        <!-- Шар води, що плавно росте -->
        <path d="M 299,405 Q 320,407 341,405 L 343,430 Q 320,433 301,430 Z" fill="rgba(0, 123, 255, 0.5)" class="cup-water" />
        <text x="320" y="375" font-family="sans-serif" font-size="11" fill="#0056b3" font-weight="bold" text-anchor="middle">РОБОЧИЙ</text>
        """
    else:
        cup_element = ""

    html_src = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ margin: 0; padding: 0; background-color: #f8f9fa; overflow: hidden; display: flex; justify-content: center; }}
            .lbl-txt {{ font-family: sans-serif; font-size: 13px; fill: #333; font-weight: bold; }}
            .main-title {{ font-family: sans-serif; font-size: 15px; fill: #111; font-weight: bold; text-anchor: middle; }}
            .sc-txt {{ font-family: monospace; font-size: 9px; fill: #555; }}
            {css_animation}
        </style>
    </head>
    <body>
    <svg width="760" height="420" viewBox="0 0 800 440" xmlns="http://w3.org" style="background-color: #ffffff; border: 1px solid #dee2e6; border-radius: 8px;">
        
        <text x="400" y="30" class="main-title">Схема експериментальної установки</text>

        <!-- 1. СУДИНА А -->
        <rect x="250" y="80" width="140" height="220" rx="10" fill="none" stroke="#555" stroke-width="3" />
        <rect x="290" y="70" width="60" height="10" fill="#333" rx="2" />
        <path d="M 251.5,160 Q 320,162 388.5,160 L 388.5,298.5 L 251.5,298.5 Z" fill="rgba(0, 123, 255, 0.23)" />
        <text x="320" y="200" class="lbl-txt" fill="#0056b3" text-anchor="middle">Судина А</text>
        {bubbles}
        
        <!-- 2. БЛОК З КАПІЛЯРОМ К -->
        <rect x="470" y="70" width="160" height="110" rx="6" fill="#f1f3f5" stroke="#adb5bd" stroke-width="2" />
        <text x="550" y="92" class="lbl-txt" text-anchor="middle">Капіляр К</text>
        <path d="M 480,120 Q 510,95 540,120 T 600,120" fill="none" stroke="#17a2b8" stroke-width="3" stroke-linecap="round" />
        <path d="M 480,140 Q 510,115 540,140 T 600,140" fill="none" stroke="#17a2b8" stroke-width="3" stroke-linecap="round" />

        <!-- 3. ТРУБКИ -->
        <path d="M 630,120 L 670,120 L 670,50 L 430,50 L 430,120 L 470,120" fill="none" stroke="#6c757d" stroke-width="2" />
        <path d="M 320,70 L 320,50" fill="none" stroke="#6c757d" stroke-width="2" />
        <path d="M 360,80 L 360,110 L 140,110 L 140,200" fill="none" stroke="#6c757d" stroke-width="2" />

        <!-- 4. КРАН В ТА СТАКАН -->
        <path d="M 320,300 L 320,330" fill="none" stroke="#555" stroke-width="3" />
        <circle cx="320" cy="330" r="10" fill="#6c757d" stroke="#333" stroke-width="1.5" />
        <g transform="translate(320,330) rotate({valve_angle})">
            <rect x="-4" y="-18" width="8" height="36" fill="#dc3545" rx="2" />
            <circle cx="0" cy="0" r="5" fill="#fff" />
        </g>
        <text x="345" y="335" class="lbl-txt">Кран B</text>
        
        {cup_element}
        {drop_element}

        <!-- 5. U-ПОДІБНИЙ МАНОМЕТР М -->
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

        <path d="M 110,{left_knee_y} L 110,350 Q 110,370 140,370 Q 170,370 170,350 L 170,{right_knee_y}" 
              fill="none" stroke="royalblue" stroke-width="10" stroke-linecap="round" class="v-water" />
              
        <text x="140" y="405" class="lbl-txt" fill="royalblue" text-anchor="middle">Манометр М</text>

    </svg>
    </body>
    </html>
    """
    return html_src
