import random

def get_svg_installation(valve_pos, dH_mm, is_running, sim_time, is_turbulent):
    """
    Генерує чистий SVG-код лабораторної установки.
    Розмір полотна: 800x450 пікселів.
    """
    # Ефект тремтіння рівнів манометра при турбулентності
    jitter = random.uniform(-2.5, 2.5) if (is_running and is_turbulent) else 0.0
    animated_dH = dH_mm + jitter
    
    # Розрахунок рівнів води в манометрі (базовий рівень Y = 280)
    left_knee_y = 280 + (animated_dH * 0.6)
    right_knee_y = 280 - (animated_dH * 0.6)
    
    # Визначення стану крана та крапель
    is_dripping = is_running and valve_pos > 0
    drop_y = 310 + ((sim_time * 120) % 65) if is_dripping else 0
    
    # Поворот ручки крана залежно від відсотка відкриття
    valve_angle = (valve_pos / 100.0) * 90.0

    # Окремо форми стакана для динамічного відображення води всередині
    water_in_cup = ""
    if is_running:
        water_in_cup = '<path d="M 299,415 Q 320,417 341,415 L 343,430 Q 320,433 301,430 Z" fill="rgba(0, 123, 255, 0.4)" />'

    # Перевірка падаючої краплі
    drop_element = ""
    if is_dripping and drop_y < 380:
        drop_element = f'<circle cx="320" cy="{drop_y}" r="3" fill="#007bff" />'

    # Рендеринг SVG з екранованими стилями (стилі вставляємо окремим блоком без f-форматування)
    svg = f"""
    <svg width="100%" height="450" viewBox="0 0 800 450" xmlns="http://w3.org" style="background-color: #f8f9fa; border: 1px solid #dee2e6; border-radius: 8px;">
        
        <defs>
            <style>
                .lbl-txt {{ font-family: sans-serif; font-size: 14px; fill: #333; font-weight: bold; }}
                .sub-lbl {{ font-family: sans-serif; font-size: 11px; fill: #666; }}
                .main-title {{ font-family: sans-serif; font-size: 16px; fill: #111; font-weight: bold; text-anchor: middle; }}
                .sc-txt {{ font-family: monospace; font-size: 9px; fill: #555; }}
            </style>
        </defs>
        
        <text x="400" y="30" class="main-title">Схема експериментальної установки</text>

        <!-- 1. СУДИНА А (АСПІРАТОР З ВОДОЮ) -->
        <rect x="250" y="80" width="140" height="220" rx="10" fill="none" stroke="#555" stroke-width="3" />
        <rect x="290" y="70" width="60" height="10" fill="#333" rx="2" />
        <path d="M 251.5,150 Q 320,152 388.5,150 L 388.5,298.5 L 251.5,298.5 Z" fill="rgba(0, 123, 255, 0.25)" />
        <text x="320" y="210" class="lbl-txt" fill="#0056b3" text-anchor="middle">Судина А</text>
        
        <!-- 2. БЛОК З КАПІЛЯРОМ К (КОРОБОЧКА) -->
        <rect x="470" y="70" width="160" height="110" rx="6" fill="#f1f3f5" stroke="#adb5bd" stroke-width="2" />
        <text x="550" y="92" class="lbl-txt" text-anchor="middle">Капіляр К</text>
        
        <!-- Скручений змійкою капіляр -->
        <path d="M 480,120 Q 510,95 540,120 T 600,120" fill="none" stroke="#17a2b8" stroke-width="3" stroke-linecap="round" />
        <path d="M 480,140 Q 510,115 540,140 T 600,140" fill="none" stroke="#17a2b8" stroke-width="3" stroke-linecap="round" />

        <!-- 3. З'ЄДНУВАЛЬНІ ТРУБКИ -->
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
        
        <!-- Стакан -->
        <path d="M 295,380 L 300,430 Q 320,433 340,430 L 345,380" fill="none" stroke="#555" stroke-width="2.5" />
        {water_in_cup}
        <text x="360" y="415" class="sub-lbl">Стакан</text>
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
              fill="none" stroke="royalblue" stroke-width="10" stroke-linecap="round" />
              
        <text x="140" y="405" class="lbl-txt" fill="royalblue" text-anchor="middle">Манометр М</text>

    </svg>
    """
    return svg
