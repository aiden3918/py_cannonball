'''
f = force in newtons (kg * m/s^2)
m = mass (kg)
a = acceleration (m/s^2)
ff = force of friction (kg * m/s^2)
u = coefficient of friction (constant)
fn = normal force (kg * m/s^2)
w = weight (kg * m/s^2)
'''

# f = ma and its correspondants
def calculate_forces(what_to_calculate, f, m, a):
    match what_to_calculate:
        case "f":
            return m * a
        case "m":
            return f / a
        case "a":
            return f / m
        
# ff = u * fn
def calc_friction(normal, coefficient_of_friction):
    return normal * coefficient_of_friction
