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
    # 1 мм ΔH розведення = 0.6 пікселя зміни кожного коліна вгору/вниз
    left_knee_y = 280 + (animated_dH * 0.6)
    right_knee_y = 280 - (animated_dH * 0.6)
    
    # Визначення стану крана та крапель
    is_dripping = is_running and valve_pos > 0
    drop_y = 310 + ((sim_time * 60) % 50) if is_dripping else 0
    
    # Поворот ручки крана залежно від відсотка відкриття
    valve_angle = (valve_pos / 100.0) * 90.0

    svg = f"""
    <svg width="100%" height="450" viewBox="0 0 800 450" xmlns="http://w3.org" style="background-color: #f8f9fa; border: 1px solid #dee2e6; border-radius: 8px;">
        
        <!-- ОБОЗНАЧЕННЯ / ШРИФТИ -->
        <style>
            .label {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; font-size: 14px; fill: #333; font-weight: bold; }}
            .sub-label {{ font-family: 'Segoe UI', sans-serif; font-size: 11px; fill: #666; }}
            .title {{ font-family: 'Segoe UI', sans-serif; font-size: 16px; fill: #111; font-weight: bold; text-anchor: middle; }}
            .scale-text {{ font-family: monospace; font-size: 9px; fill: #555; }}
        </style>
        
        <text x="400" y="30" class="title">Схема експериментальної установки</text>

        <!-- 1. СУДИНА А (АСПІРАТОР З ВОДОЮ) -->
        <!-- Корпус судини -->
        <rect x="250" y="80" width="140" height="220" rx="10" fill="none" stroke="#555" stroke-width="3" />
        <!-- Кришка судини герметична -->
        <rect x="290" y="70" width="60" height="10" fill="#333" rx="2" />
        <!-- Вода всередині судини А -->
        <path d="M 251.5,150 Q 320,152 388.5,150 L 388.5,298.5 L 251.5,298.5 Z" fill="rgba(0, 123, 255, 0.25)" />
        <text x="320" y="210" class="label" fill="#0056b3" text-anchor="middle">Судина А</text>
        
        <!-- 2. БЛОК З КАПІЛЯРОМ К (КОРОБОЧКА) -->
        <rect x="470" y="70" width="160" height="110" rx="6" fill="#f1f3f5" stroke="#adb5bd" stroke-width="2" />
        <text x="550" y="90" class="label" text-anchor="middle">Капіляр К</text>
        
        <!-- Скручений змійкою капіляр всередині коробочки -->
        <path d="M 450,110 L 490,110 Q 500,110 500,120 L 500,135 Q 500,145 510,145 L 590,145 Q 600,145 600,130 L 600,115 Q 600,105 610,105 L 650,105" 
              fill="none" stroke="#17a2b8" stroke-width="3" stroke-linecap="round" />

        <!-- 3. З'ЄДНУВАЛЬНІ ТРУБКИ -->
        <!-- Трубка від атмосфери до капіляра -->
        <path d="M 630,105 L 670,105 L 670,50 L 430,50 L 430,110 L 470,110" fill="none" stroke="#6c757d" stroke-width="2" />
        <!-- Трубка від капіляра до судини А -->
        <path d="M 320,70 L 320,50 M 430,110 L 390,110" fill="none" stroke="#6c757d" stroke-width="2" />
        <!-- Трубка від судини А до манометра -->
        <path d="M 360,80 L 360,110 L 140,110 L 140,200" fill="none" stroke="#6c757d" stroke-width="2" />

        <!-- 4. КРАН В ТА СТАКАН -->
        <!-- Трубка зливу знизу судини А -->
        <path d="M 320,300 L 320,330" fill="none" stroke="#555" stroke-width="3" />
        <!-- Корпус крана B -->
        <circle cx="320" cy="330" r="10" fill="#6c757d" stroke="#333" stroke-width="1.5" />
        <!-- Ручка крана (повертається) -->
        <g transform="translate(320,330) rotate({valve_angle})">
            <rect x="-4" y="-18" width="8" height="36" fill="#dc3545" rx="2" />
            <circle cx="0" cy="0" r="5" fill="#fff" />
        </g>
        <text x="340" y="335" class="label">Кран B</text>
        
        <!-- Стакан хімічний -->
        <path d="M 295,380 L 300,430 Q 320,433 340,430 L 345,380" fill="none" stroke="#555" stroke-width="2.5" />
        <!-- Вода, що набралася в стакан -->
        {" " if not is_running else f'<path d="M 299,415 Q 320,417 341,415 L 343,430 Q 320,433 301,430 Z" fill="rgba(0, 123, 255, 0.4)" />' }
        <text x="360" y="415" class="sub-label">Стакан</text>

        <!-- Анімація падаючої краплі води -->
        {" " if not is_dripping or drop_y > 380 else f'<circle cx="320" cy="{drop_y}" r="3" fill="#007bff" />'}

        <!-- 5. U-ПОДІБНИЙ МАНОМЕТР М -->
        <!-- Шкала манометра (плашка) -->
        <rect x="115" y="180" width="50" height="200" fill="#fff" stroke="#ced4da" />
        <!-- Поділки шкали манометра -->
        <line x1="140" y1="200" x2="140" y2="360" stroke="#aaa" stroke-width="1" />
        <line x1="130" y1="280" x2="150" y2="280" stroke="#333" stroke-width="1.5" /> <!-- Нуль -->
        <text x="154" y="283" class="scale-text" style="font-weight:bold;">0</text>
        
        <line x1="133" y1="220" x2="147" y2="220" stroke="#777" stroke-width="1" />
        <text x="154" y="223" class="scale-text">+100</text>
        
        <line x1="133" y1="340" x2="147" y2="340" stroke="#777" stroke-width="1" />
        <text x="154" y="343" class="scale-text">-100</text>

        <!-- Скляна U-подібна трубка манометра -->
        <path d="M 110,200 L 110,350 Q 110,370 140,370 Q 170,370 170,350 L 170,200" 
              fill="none" stroke="rgba(200,200,200,0.5)" stroke-width="14" stroke-linecap="round" />
        <path d="M 110,200 L 110,350 Q 110,370 140,370 Q 170,370 170,350 L 170,200" 
              fill="none" stroke="#555" stroke-width="16" stroke-linecap="round" style="opacity: 0.15;" />

        <!-- Вода всередині манометра (динамічна) -->
        <!-- Рівні розраховуються через змінні left_knee_y та right_knee_y -->
        <path d="M 110,{left_knee_y} L 110,350 Q 110,370 140,370 Q 170,370 170,350 L 170,{right_knee_y}" 
              fill="none" stroke="royalblue" stroke-width="10" stroke-linecap="round" />
              
        <text x="140" y="400" class="label" fill="royalblue" text-anchor="middle">Манометр М</text>

    </svg>
    """
    return svg

