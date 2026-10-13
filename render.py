# render.py
import layout

def get_html_installation(valve_pos, target_dH_mm, flow_mode, cup_type, is_turbulent, current_time_sec=0.0):
    """
    Збирає лабораторну установку, динамічно підставляючи змінні у шаблон layout.
    """
    valve_angle = (valve_pos / 100.0) * 90.0 if flow_mode != 'none' else 0.0
    delta_px = (target_dH_mm * 0.6) if flow_mode != 'none' else 0.0
    
    timer_display = "block" if cup_type == 'work' else "none"
    js_mode = 1 if flow_mode in ['stream', 'drops'] else 0
    js_initial_shift = 0.0 if flow_mode == 'stream' else delta_px

    # Динамічний JS двигун клієнта
    js_engine = f"""
    <script>
        let currentShift = {js_initial_shift}; 
        const targetShift = {delta_px};
        const mode = {js_mode};
        
        let startTime = Date.now() - ({current_time_sec} * 1000);
        let flowMode = "{flow_mode}";

        function animateSetup() {{
            // 1. АНІМАЦІЯ МАНОМЕТРА
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
            
            let safeShift = Math.min(currentShift, 72.0);
            let leftY = (280 + safeShift).toFixed(1);
            let rightY = (280 - safeShift).toFixed(1);
            
            let newManoPath = `M 110,${{leftY}} L 110,350 Q 110,370 140,370 Q 170,370 170,350 L 170,${{rightY}}`;
            document.getElementById('v-water-contour').setAttribute('d', newManoPath);
            
            // 2. АНІМАЦІЯ ОПУСКАННЯ ВОДИ В СУДИНІ А (Дно фіксоване на 298.5)
            if (flowMode !== 'none') {{
                let elapsedSec = (Date.now() - startTime) / 1000;
                if (flowMode === 'stream') elapsedSec = 4.0;
                
                let dropPixels = Math.min(elapsedSec * 0.25, 45.0);
                let currentTopY = 150.0 + dropPixels;
                
                let newVesselPath = `M 251.5,${{currentTopY}} Q 320,${{currentTopY + 2}} 388.5,${{currentTopY}} L 388.5,298.5 L 251.5,298.5 Z`;
                document.getElementById('vessel-water-path').setAttribute('d', newVesselPath);
            }}

            requestAnimationFrame(animateSetup);
        }}
        
        if ("{cup_type}" === "work") {{
            setInterval(() => {{
                let diff = (Date.now() - startTime) / 1000;
                document.getElementById('js-timer').textContent = diff.toFixed(1) + ' c';
            }}, 100);
        }}
        
        window.onload = () => {{
            requestAnimationFrame(animateSetup);
        }};
    </script>
    """

    css_animation = ""
    water_flow_element = ""
    bubbles = ""

    if flow_mode == 'stream':
        css_animation += """
        @keyframes flow_speed {
            from { stroke-dashoffset: 0; }
            to { stroke-dashoffset: -24; }
        }
        .water-stream-core {
            stroke-dasharray: 10, 5;
            animation: flow_speed 0.2s infinite linear;
        }
        """
        water_flow_element = """
        <defs>
            <linearGradient id="streamGrad" x1="0%" y1="0%" x2="100%" y2="0%">
                <stop offset="0%" stop-color="#0056b3" />
                <stop offset="30%" stop-color="#3b99ff" />
                <stop offset="70%" stop-color="#b3d7ff" />
                <stop offset="100%" stop-color="#0056b3" />
            </linearGradient>
        </defs>
        <line x1="320" y1="330" x2="320" y2="395" stroke="url(#streamGrad)" stroke-width="4.5" stroke-linecap="round" />
        <line x1="320" y1="330" x2="320" y2="395" stroke="#ffffff" stroke-width="1.5" stroke-opacity="0.65" class="water-stream-core" />
        """
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

    if flow_mode != 'none' and is_turbulent:
        css_animation += """
        @keyframes jitter {
            0% { transform: translateY(0px); }
            100% { transform: translateY(1.5px); }
        }
        .mano-group { animation: jitter 0.05s infinite alternate ease-in-out; }
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

    # Безпечна покрокова заміна токенів без конфліктів форматування рядків
    src = layout.HTML_TEMPLATE
    src = src.replace("TIMER_DISPLAY_VAR", str(timer_display))
    src = src.replace("CSS_ANIMATION_VAR", str(css_animation))
    src = src.replace("VALVE_ANGLE_VAR", str(round(valve_angle, 1)))
    src = src.replace("BUBBLES_VAR", str(bubbles))
    src = src.replace("CUP_ELEMENT_VAR", str(cup_element))
    src = src.replace("WATER_FLOW_ELEMENT_VAR", str(water_flow_element))
    src = src.replace("JS_ENGINE_VAR", str(js_engine))
    
    return src
