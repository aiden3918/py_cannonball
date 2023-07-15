'''
d = displacement (m)
v = velocity (given velocity is constant) (m/s)
vo = initial velocity (m/s)
vf = final velocity (m/s)
a = acceleration (given acceleration is constant) (m/s^2)
t = time (t)
'''

import math

def calculate_d_v_or_t(what_to_calculate, v, d, t):
    match what_to_calculate:
        case "v": 
            return d / t
        case "d":
            return v * t
        case "t":
            return d / v
        case _:
            return "Invalid unknown"

# d = vo(t) + 1/2(at^2)
def calc_d_using_vo_a_and_t(vo, a, t):
    return (vo*t) + (0.5*a*math.pow(t,2))

# vf^2 = vo^2 + 2ad
# vf = sqrt(vo^2 + 2ad)
def calc_vf_using_vo_a_and_d(vo, a, d):
    return math.sqrt(math.pow(vo, 2) + (2*a*d))

# vf = vo + a*t
def calc_vf_using_vo_a_and_t(what_to_calculate, vf, vo, a, t):
    match what_to_calculate:
        case "vf":
            return vo + (a * t)
        case "vo": 
            return vf - (a*t)
        case "a":
            return (vf - vo) / t
        case "t":
            return (vf - vo) / a

