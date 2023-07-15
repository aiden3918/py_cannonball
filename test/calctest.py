import math
import kinematics as k
import forces as f

accel_gravity = 9.8
force = 1000
cannonball_mass = 10
barrel_length = 5
angle = 45

cannon_offset_x = 200
cannon_offset_y = 200

# assume cannon and cannonball have no friction

# find net vertical force (fa - w)
vert_force_applied = force * math.sin(angle)
weight = f.calculate_forces('f', 0, cannonball_mass, accel_gravity)
net_vert_force = vert_force_applied - weight

# find net acceleration
# if w < fa, then no accel
# else, using net vertical force and horizontal force, find net force
if net_vert_force <= 0:
    net_accel = 0
else: 
    net_force = math.sqrt(math.pow(net_vert_force, 2) + math.pow(force * math.cos(angle), 2))
    net_accel = f.calculate_forces('a', net_force, cannonball_mass, 0)

exit_cannon_vel = k.calc_vf_using_vo_a_and_d(0, net_accel, barrel_length)
exit_cannon_time = k.calc_vf_using_vo_a_and_t('t', exit_cannon_vel, 0, net_accel, 0)


print(f'''
gravity: {accel_gravity} m/s^2
force: {force} N
cannonball mass: {cannonball_mass} kg
barrel length: {barrel_length} m
angle: {angle} degrees

cannonball:
    acceleration: {net_accel} m/s^2
    exit velocity: {exit_cannon_vel} m/s
    time it would take to exit: {exit_cannon_time} s

      
''')