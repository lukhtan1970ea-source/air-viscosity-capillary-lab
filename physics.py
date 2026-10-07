import numpy as np
import random

# --- ГЕОМЕТРИЧНІ ТА ФІЗИЧНІ КОНСТАНТИ УСТАНОВКИ ---
L = 2.14          # Довжина капіляра в метрах (214 см)
R_cap = 0.00035   # Радіус капіляра в метрах (0.035 см)
R_gas = 8.314     # Універсальна газова константа (Дж/(моль*К))
M_air = 0.029     # Молярна маса повітря (кг/моль)
rho_w = 1000.0    # Густина води в манометрі та судині (кг/м3)
g = 9.81          # Прискорення вільного падіння (м/с2)
k_B = 1.38e-23    # Постійна Больцмана (Дж/К)

# Базова в'язкість повітря за 20 °C для зворотної моделі
ETA_BASE = 1.82e-5 

def calculate_flow_and_reynolds(valve_pos, t_celsius, p_kpa):
    """
    Розрахунок номінальних параметрів потоку повітря залежно від відкриття крана.
    """
    if valve_pos == 0:
        return 0.0, 0.0, 0.0, False
        
    T_kelvin = t_celsius + 273.15
    P_pascal = p_kpa * 1000.0
    
    # Залежність перепаду тиску від відкриття крана (біля 50% висота біля 84 мм)
    delta_H_nominal = (valve_pos / 50.0) * 0.084 
    delta_P = rho_w * g * delta_H_nominal
    
    # Об'ємна швидкість протікання повітря через капіляр за законом Пуазейля
    flow_rate_air = (np.pi * (R_cap**4) * delta_P) / (8.0 * ETA_BASE * L)
    
    # Швидкість повітря в капілярі для розрахунку числа Рейнольдса
    v_air = flow_rate_air / (np.pi * (R_cap**2))
    rho_air = (P_pascal * M_air) / (R_gas * T_kelvin)
    
    # Число Рейнольдса
    Re = (2.0 * rho_air * v_air * R_cap) / ETA_BASE
    is_turbulent = Re > 1500
    
    return delta_H_nominal, flow_rate_air, Re, is_turbulent

def generate_experiment_result(flow_rate_air, delta_H_nominal, is_turbulent, t_celsius, p_kpa, measured_time):
    """
    Генерація фінального результату вимірювання на основі реального зафіксованого часу.
    """
    # Розраховуємо теоретичний об'єм повітря, що пройшов за цей час (в см3)
    theoretical_volume = (flow_rate_air * measured_time) * 1e6
    
    # Додаємо невеликий випадковий шум до маси води
    water_mass = theoretical_volume * random.uniform(0.985, 1.015)
    water_mass = round(water_mass, 2)
    
    m0 = 62.44  # Маса порожнього стакана з методички
    m_total = round(m0 + water_mass, 2)
    
    # Запис поточної висоти манометра (з шумом при турбулентності)
    final_dH = round(delta_H_nominal * 1000 + (random.uniform(-2, 2) if is_turbulent else 0))
    
    return {
        "t, °C": t_celsius,
        "Pa, кПа": p_kpa,
        "ΔH, мм": final_dH,
        "τ, с": round(measured_time, 1),
        "m0 (порожній), г": m0,
        "m (з водою), г": m_total,
        "m_води, г": water_mass
    }
