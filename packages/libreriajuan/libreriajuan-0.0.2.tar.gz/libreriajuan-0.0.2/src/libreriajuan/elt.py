import math

# Tablas de conductores
tabla_conductores_principal = [
    (20, "AWG 12"), (25, "AWG 10"), (35, "AWG 8"), (50, "AWG 6"),
    (65, "AWG 4"), (85, "AWG 3"), (100, "AWG 2"), (115, "AWG 1"),
    (150, "AWG 1/0"), (170, "AWG 2/0"), (195, "AWG 3/0"), (225, "AWG 4/0"),
    (260, "250 kcmil"), (300, "300 kcmil"), (350, "350 kcmil"),
    (400, "400 kcmil"), (500, "500 kcmil")
]

tabla_conductores_motor = [
    (15, "AWG 14"), (20, "AWG 12"), (25, "AWG 10"), (35, "AWG 8"),
    (50, "AWG 6"), (65, "AWG 4"), (85, "AWG 3"), (100, "AWG 2"),
    (115, "AWG 1"), (150, "AWG 1/0"), (170, "AWG 2/0"),
    (195, "AWG 3/0"), (225, "AWG 4/0"), (260, "250 kcmil"), (300, "300 kcmil")
]

# --- Funciones ---
def factor_utilizacion(potencia):
    if 0.57 <= potencia <= 1.9:
        return 0.70
    elif 2.29 <= potencia <= 11.4:
        return 0.83
    elif 15.26 <= potencia <= 30.5:
        return 0.85
    elif potencia > 30.5:
        return 0.87
    return 1

def demanda_motor(potencia, cosfi=0.87, rendimiento=0.937):
    fu = factor_utilizacion(potencia)
    return (potencia * fu) / (cosfi * rendimiento)

def demanda_total(motores):
    return sum(m["dmax"] for m in motores)

def corriente_transformador(Snt, voltaje):
    return Snt * 1000 / (math.sqrt(3) * voltaje)

def factor_temp_principal(temp):
    if temp <= 10: return 1.11
    if temp <= 20: return 1.05
    if temp <= 30: return 0.97
    if temp <= 40: return 0.86
    if temp <= 50: return 0.79
    if temp <= 60: return 0.68
    if temp <= 70: return 0.55
    return 0.39

def factor_instalacion(km):
    if km == 1: return 1.118
    if km == 1.5: return 1.1
    if km == 2: return 1.05
    if km == 2.5: return 1
    if km == 3: return 0.96
    return 1

def corriente_corregida_principal(In, ft, fr_inst, fa=1, fp=0.91, far=1, fl=1):
    return In / (ft * fa * fr_inst * fp * far * fl)

def seleccionar_conductor_principal(Ic):
    for limite, conductor in tabla_conductores_principal:
        if Ic <= limite:
            return conductor
    return "No definido"

def corriente_motor(potencia, voltaje, cosfi=0.87, rendimiento=0.937):
    return potencia * 1000 / (math.sqrt(3) * voltaje * cosfi * rendimiento)

def factor_temp_motor(temp):
    if temp <= 10: return 1.22
    if temp <= 20: return 1.12
    if temp <= 30: return 1
    if temp <= 40: return 0.87
    if temp <= 50: return 0.71
    return 0.5

def corriente_corregida_motor(In_motor, ft_m, fa_m=1):
    return In_motor / (math.sqrt(3) * ft_m * fa_m)

def seleccionar_conductor_motor(Ic_motor):
    for limite, conductor in tabla_conductores_motor:
        if Ic_motor <= limite:
            return conductor
    return "No definido"


