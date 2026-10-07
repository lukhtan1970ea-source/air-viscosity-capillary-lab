import random

def get_html_installation(valve_pos, target_dH_mm, current_dH_mm, flow_mode, sim_time, cup_type, is_turbulent):
    """
    Генерує чистий HTML/SVG-код лабораторної установки.
    flow_mode: 'none' (закрито), 'stream' (струмінь), 'drops' (краплі)
    cup_type: 'none' (немає стакана), 'vspom' (допоміжний), 'work' (робочий)
    """
    # Ефект тремтіння рівнів манометра при турбулентності (тільки якщо тече потік)
    jitter = random.uniform(-2.5, 2.5) if (flow_mode != 'none' and is_turbulent) else 0.0
    animated_dH = current_dH_mm + jitter
    
    # Рівні рідини в манометрі (базовий Y = 280)
    left_knee_y = 280 + (animated_dH * 0.6)
    right_knee_y = 280 - (animated_dH * 0.6)
    
    # Розрахунок кута ручки крана (0 - закрито, ручка горизонтально; 90 - відкрито на макс)
    valve_angle = (valve_pos / 100.0) * 90.0 if flow_mode != 'none' else 0.0
    
    # Розрахунок рівнів води в судинах залежно від часу досвіду (символічно опускаємо/піднімаємо)
    water_lost_pixels = min(sim_time * 0.4, 25.0) if flow_mode != 'none' else 0.0
    vessel_water_y = 150 + water_lost_pixels
    
    # Візуалізація води під краном
    water_flow_element = ""
    if flow_mode == 'stream':
        # Стумінь води
        water_flow_element = '<line x1="320" y1="330" x2="320" y2="385" stroke="#007bff" stroke-width="4" />'
    elif flow_mode == 'drops':
        # Падаюча крапля
        drop_y = 330 + ((sim_time * 160) % 55)
        if drop_y < 385:
            water_flow_element = f'<circle cx="320" cy="{drop_y}" r="3.5" fill="#007bff" />'

    # Візуалізація бульбашок повітря в судині А
    bubbles = ""
    if flow_mode != 'none':
        for i in range(3):
            b_x = 270 + (i * 35) + (int(sim_time * 10 + i * 5) % 15)
            b_y = 280 - ((sim_time * 40 + i * 60) % int(140 - water_lost_pixels))
            if b_y > vessel_water_y and b_y < 295:
                bubbles += f'<circle cx="{b_x}" cy="{b_y}" r="2.5" fill="none" stroke="rgba(255,255,255,0.7)" stroke-width="1" />'

    # Орієнтація та тип стакана
    cup_element = ""
    if cup_type == 'vspom':
        # Допоміжний стакан (сірий, завжди трохи заповнений)
        cup_element = """
        <path d="M 295,385 L 300,430 Q 320,433 340,430 L 345,385" fill="none" stroke="#777" stroke-width="2.5" />
        <path d="M 299,410 Q 320,412 341,410 L 343,430 Q 320,433 301,430 Z" fill="rgba(108, 117, 125, 0.4)" />
        <text x="320" y="405" font-family="sans-serif" font-size="10" fill="#555" text-anchor="middle">Допоміжний</text>
        """
    elif cup_type == 'work':
        # Робочий стакан (динамічно наповнюється синьою водою)
        fill_height = min(sim_time * 0.4, 25.0)
        water_y = 430 - fill_height
        cup_element = f"""
        <path d="M 295,385 L 300,430 Q 320,433 340,430 L 345,385" fill="none" stroke="#0056b3" stroke-width="2.5" />
        <path d="M {{300 - (fill_height*0.05)}}, {water_y} Q 320, {{water_y+2}} 340, {water_y} L 343,430 Q 320,433 301,430 Z" fill="rgba(0, 123, 255, 0.5)" />
        <text x="320" y="375" font-family="sans-serif" font-size="11" fill="#0056b3" font-weight="bold" text-anchor="middle">РОБОЧИЙ</text>
        """

    # Збірка фінальної сторінки з ізольованими стилями під iframe
    html_src = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ margin: 0; padding: 0; background-color: #f8f9fa; overflow: hidden; display: flex; justify-content: center; }}
            .lbl-txt {{ font-family: sans-serif; font-size: 13px; fill: #333; font-weight: bold; }}
            .main-title {{ font-family: sans-serif; font-size: 15px; fill: #111; font-weight: bold; text-anchor: middle; }}
            .sc-txt {{ font-family: monospace; font-size: 9px; fill: #555; }}
        </style>
    </head>
    <body>
    <svg width="760" height="420" viewBox="0 0 800 440" xmlns="http://w3.org" style="background-color: #ffffff; border: 1px solid #dee2e6; border-radius: 8px;">
        
        <text x="400" y="30" class="main-title">Схема експериментальної установки</text>

        <!-- 1. СУДИНА А (АСПІРАТОР) -->
        <rect x="250" y="80" width="140" height="220" rx="10" fill="none" stroke="#555" stroke-width="3" />
        <rect x="290" y="70" width="60" height="10" fill="#333" rx="2" />
        <!-- Динамічний рівень води всередині судини -->
        <path d="M 251.5,{vessel_water_y} Q 320,{{vessel_water_y+2}} 388.5,{vessel_water_y} L 388.5,298.5 L 251.5,298.5 Z" fill="rgba(0, 123, 255, 0.23)" />
        <text x="320" y="200" class="lbl-txt" fill="#0056b3" text-anchor="middle">Судина А</text>
        {bubbles}
        
        <!-- 2. БЛОК З КАПІЛЯРОМ К (КОРОБОЧКА) -->
        <rect x="470" y="70" width="160" height="110" rx="6" fill="#f1f3f5" stroke="#adb5bd" stroke-width="2" />
        <text x="550" y="92" class="lbl-txt" text-anchor="middle">Капіляр К</text>
        
        <!-- Скручений капіляр -->
        <path d="M 480,120 Q 510,95 540,120 T 600,120" fill="none" stroke="#17a2b8" stroke-width="3" stroke-linecap="round" />
        <path d="M 480,140 Q 510,115 540,140 T 600,140" fill="none" stroke="#17a2b8" stroke-width="3" stroke-linecap="round" />

        <!-- 3. З'ЄДНУВАЛЬНІ ТРУБКИ -->
        <path d="M 630,120 L 670,120 L 670,50 L 430,50 L 430,120 L 470,120" fill="none" stroke="#6c757d" stroke-width="2" />
        <path d="M 320,70 L 320,50" fill="none" stroke="#6c757d" stroke-width="2" />
        <path d="M 360,80 L 360,110 L 140,110 L 140,200" fill="none" stroke="#6c757d" stroke-width="2" />

        <!-- 4. КРАН В ТА СТАКАН -->
        <path d="M 320,300 L 320,330" fill="none" stroke="#555" stroke-width="3" />
        <circle cx="320" cy="330" r="10" fill="#6c757d" stroke="#333" stroke-width="1.5" />
        
        <!-- Поворотний кран -->
        <g transform="translate(320,330) rotate({valve_angle})">
            <rect x="-4" y="-18" width="8" height="36" fill="#dc3545" rx="2" />
            <circle cx="0" cy="0" r="5" fill="#fff" />
        </g>
        <text x="345" y="335" class="lbl-txt">Кран B</text>
        
        {cup_element}
        {water_flow_element}

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
              fill="none" stroke="royalblue" stroke-width="10" stroke-linecap="round" />
              
        <text x="140" y="405" class="lbl-txt" fill="royalblue" text-anchor="middle">Манометр М</text>

    </svg>
    </body>
    </html>
    """
    return html_src
