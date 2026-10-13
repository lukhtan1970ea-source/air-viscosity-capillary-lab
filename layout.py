# layout.py
# Статичний контур сцени лабораторної установки. Повністю ізольований від f-рядків Python.

BASE_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <style>
        body { margin: 0; padding: 0; background-color: #f8f9fa; overflow: hidden; display: flex; flex-direction: column; align-items: center; }
        .lbl-txt { font-family: sans-serif; font-size: 13px; fill: #333; font-weight: bold; }
        .main-title { font-family: sans-serif; font-size: 15px; fill: #111; font-weight: bold; text-anchor: middle; }
        .sc-txt { font-family: monospace; font-size: 9px; fill: #555; }
        .timer-box {
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
        }
        CSS_ANIMATION_VAR
    </style>
</head>
<body>

<div class="timer-box" style="display: TIMER_DISPLAY_VAR;">&#9201; Секундомір: <span id="js-timer">0.0 с</span></div>

<svg width="760" height="420" viewBox="0 0 800 440" xmlns="http://w3.org" style="background-color: #ffffff; border: 1px solid #dee2e6; border-radius: 8px;">
    
    <text x="400" y="30" class="main-title">Схема експериментальної установки</text>

    <!-- 1. СУДИНА А -->
    <rect x="250" y="80" width="140" height="220" rx="10" fill="none" stroke="#555" stroke-width="3" />
    <rect x="290" y="70" width="60" height="10" fill="#333" rx="2" />
    
    <!-- Контур води з унікальним ID для динамічного керування через JS -->
    <path id="vessel-water-path" d="M 251.5,150 Q 320,152 388.5,150 L 388.5,298.5 L 251.5,298.5 Z" fill="rgba(0, 123, 255, 0.23)" />
    
    <text x="320" y="190" class="lbl-txt" fill="#0056b3" text-anchor="middle">Судина А</text>
    BUBBLES_VAR
    
    <!-- 2. БЛОК З КАПІЛЯРОМ К (КОРОБОЧКА) -->
    <!-- Сам корпус приборного блока -->
    <rect x="490" y="90" width="160" height="90" rx="6" fill="#f1f3f5" stroke="#adb5bd" stroke-width="2" />
    <text x="570" y="112" class="lbl-txt" text-anchor="middle">Капіляр К</text>
    
    <!-- Рясна і щільна синусоїда капіляра (5 повних хвиль), що з'єднана з трубами -->
    <path d="M 490,140 L 505,140 Q 515,115 525,140 T 545,140 T 565,140 T 585,140 T 605,140 T 625,140 L 650,140" 
          fill="none" stroke="#17a2b8" stroke-width="3" stroke-linecap="round" />




    <!-- 3. ГЕРМЕТИЧНІ ТРУБКИ ПО МЕТОДИЦІ -->
    <path d="M 490,140 L 320,140 L 320,80" fill="none" stroke="#555" stroke-width="2.5" />
    <path d="M 650,140 L 690,140 L 690,60" fill="none" stroke="#555" stroke-width="2.5" />
    <path d="M 350,80 L 350,60 L 140,60 L 140,200" fill="none" stroke="#555" stroke-width="2.5" />

    <!-- 4. КРАН В ТА СТАКАН -->
    <path d="M 320,300 L 320,330" fill="none" stroke="#555" stroke-width="3" />
    <circle cx="320" cy="330" r="10" fill="#6c757d" stroke="#333" stroke-width="1.5" />
    <g transform="translate(320,330) rotate(VALVE_ANGLE_VAR)">
        <rect x="-4" y="-18" width="8" height="36" fill="#dc3545" rx="2" />
        <circle cx="0" cy="0" r="5" fill="#fff" />
    </g>
    <text x="345" y="335" class="lbl-txt">Кран B</text>
    
    CUP_ELEMENT_VAR
    WATER_FLOW_ELEMENT_VAR

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
        <!-- Ограничительные маски в форме вогнутых стаканчиков для левого и правого колена -->
        <defs>
            <!-- Левое колено (ширина от 105 до 115). Верхняя линия дуги провисает вниз -->
            <clipPath id="left-meniscus-clip">
                <path id="left-clip-path" d="M 105,0 L 115,0 L 115,280 Q 110,283.5 105,280 Z" />
            </clipPath>
            <!-- Правое колено (ширина от 165 до 175). Верхняя линия дуги провисает вниз -->
            <clipPath id="right-meniscus-clip">
                <path id="right-clip-path" d="M 165,0 L 175,0 L 175,280 Q 170,283.5 165,280 Z" />
            </clipPath>
        </defs>

        <!-- Синее тело манометра, разделенное по маскам обрезки -->
        <g class="mano-fluid-group">
            <!-- Нижняя статичная дуга (всегда на месте) -->
            <path d="M 110,278 A 30,30 0 0,0 170,278" fill="none" stroke="royalblue" stroke-width="10" />

            <!-- Левый столбик, обрезаемый вогнутой маской -->
            <g clip-path="url(#left-meniscus-clip)">
                <line id="left-knee" x1="110" y1="280" x2="110" y2="280" stroke="royalblue" stroke-width="10" stroke-linecap="round" />
            </g>

            <!-- Правый столбик, обрезаемый вогнутой маской -->
            <g clip-path="url(#right-meniscus-clip)">
                <line id="right-knee" x1="170" y1="280" x2="170" y2="280" stroke="royalblue" stroke-width="10" stroke-linecap="round" />
            </g>
        </g>


    </g>
          
    <text x="140" y="405" class="lbl-txt" fill="royalblue" text-anchor="middle">Манометр М</text>

</svg>

JS_ENGINE_VAR
</body>
</html>
"""
