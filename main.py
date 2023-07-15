import pygame
import os

import gui
import kinematics as k
import forces as f
import math

pygame.mixer.init()
pygame.font.init()

# initialize window -----------------------------------------------------------------------------------
WINDOW_RES = (960, 540)
WINDOW = pygame.display.set_mode(WINDOW_RES)
pygame.display.set_caption("Cannonball - Python/Pygame")
WINDOW_CENTER = (WINDOW_RES[0] // 2, WINDOW_RES[1] // 2)

# initialize sprites -----------------------------------------------------------------------------------
WHEEL = pygame.image.load(os.path.join('Assets', 'cannon-wheel-transparent.png')).convert_alpha()
WHEEL = pygame.transform.scale(WHEEL, (50, 50))
BARREL = pygame.image.load(os.path.join('Assets', 'cannon-barrel.png')).convert_alpha()
BARREL = pygame.transform.scale(BARREL, (120, 120))
CANNONBALL = pygame.image.load(os.path.join('Assets', 'cannonball-transparent.png')).convert_alpha()
CANNONBALL = pygame.transform.scale(CANNONBALL, (20, 20))

BARREL_CENTER = (70, 400)
# rotation works

# some constants and variables -----------------------------------------------------------------------------------
FPS = 30
BACKGROUND_COLOR = (100, 100, 100)

# update window -----------------------------------------------------------------------------------
def aiming_and_config_render(app_state, mouse, BARREL):
    print(mouse)
    ray_adj = mouse[0] - BARREL_CENTER[0]
    # switch coordinates to read that y-axis is at the bottom
    ray_opp = (WINDOW.get_height() - mouse[1]) - (WINDOW.get_height() - (BARREL_CENTER[1] + 60)) # offset due to image translation + whitespace
    theta = math.atan2(ray_opp, ray_adj) * (180 / math.pi) # angle of cannon
    print(theta)

    if theta >= 0 and theta <= 90: # so that it doesnt rotate too crazy
        barrel_copy = pygame.transform.rotate(BARREL, theta)
    elif theta > 90:
        barrel_copy = pygame.transform.rotate(BARREL, 90)
    else: 
        barrel_copy = pygame.transform.rotate(BARREL, 0)

    WINDOW.fill(BACKGROUND_COLOR)
    WINDOW.blit(barrel_copy, (BARREL_CENTER[0] - int(barrel_copy.get_width() / 2), BARREL_CENTER[1] - int(barrel_copy.get_height() / 2)))
    # basically, whenever rotating the object creates a surface on the back that completely covers the rotated object
    WINDOW.blit(WHEEL, (BARREL_CENTER[0] - 25, BARREL_CENTER[1] - 20))

    pygame.display.update()
    return [barrel_copy, theta]

# return time it would take for the cannonball to exit the cannon and the net velocity at which it will exit the cannon
# if there is not enough force, then returns list (-1, -1)
def calc_prereq_forces(gravity, force, cb_mass, barrel_length, angle):
    # assume cannon and cannonball have no friction

    # find net vertical force (fa - w)
    vert_force_applied = force * math.sin(angle)
    weight = f.calculate_forces('f', 0, cb_mass, gravity)
    net_vert_force = vert_force_applied - weight

    # find net acceleration
    # if w < fa, then no accel
    # else, using net vertical force and horizontal force, find net force
    if net_vert_force <= 0:
        return (-1, -1)
    else: 
        net_force = math.sqrt(math.pow(net_vert_force, 2) + math.pow(force * math.cos(angle), 2))
        net_accel = f.calculate_forces('a', net_force, gravity, 0)

    exit_cannon_vel = k.calc_vf_using_vo_a_and_d(0, net_accel, barrel_length)
    exit_cannon_time = k.calc_vf_using_vo_a_and_t('t', exit_cannon_vel, 0, net_accel, 0)

    print(f'''
        gravity: {gravity} m/s^2
        force: {force} N
        cannonball mass: {cb_mass} kg
        barrel length: {barrel_length} m
        angle: {angle} degrees

        cannonball:
            acceleration: {net_accel} m/s^2
            exit velocity: {exit_cannon_vel} m/s
            time it would take to exit: {exit_cannon_time} s

    ''')

    return (exit_cannon_time, exit_cannon_vel)

'''def firing_cannon_render(cannonball_exit_time_and_vel_tuple, barrel_copy_data_list):
    # keep on rendering cannon oriented at cursor
    barrel_copy_data_list[1] = pygame.transform.rotate(barrel_copy_data_list[1], barrel_copy_data_list[0])
    WINDOW.blit(barrel_copy_data_list[1], (BARREL_CENTER[0] - int(barrel_copy_data_list[1].get_width() / 2), BARREL_CENTER[1] - int(barrel_copy_data_list[1].get_height() / 2)))

    # simulate the time it takes for the cannonball to leave the barrel
    pygame.time.wait(cannonball_exit_time_and_vel_tuple[0] * 1000)
'''

def render_cannonball_motion(cannon_barrel_copy_list, hori_vel, vert_vel, cannon_opening_pos, gravity):
    WINDOW.fill(BACKGROUND_COLOR)

    time = (frames_elapsed / FPS)
    vertical_displacement = k.calc_d_using_vo_a_and_t(0, gravity, time)
    horizontal_displacement = k.calculate_d_v_or_t('d', hori_vel, time)
    WINDOW.blit(CANNONBALL, (cannon_opening_pos[0] + horizontal_displacement, cannon_opening_pos[1] - vertical_displacement))

    cannon_barrel_copy = cannon_barrel_copy_list[0]
    WINDOW.blit(cannon_barrel_copy, (BARREL_CENTER[0] - int(cannon_barrel_copy.get_width() / 2), BARREL_CENTER[1] - int(cannon_barrel_copy.get_height() / 2)))
    WINDOW.blit(WHEEL, (BARREL_CENTER[0] - 25, BARREL_CENTER[1] - 20))

    pygame.display.update()

# main function -----------------------------------------------------------------------------------
def main():

    clock = pygame.time.Clock()
    run = True
    app_state = 'aiming and config'

    while run:
        
        clock.tick(FPS)

        mouse = pygame.mouse.get_pos()
        keys_pressed = pygame.key.get_pressed()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        if keys_pressed[pygame.K_SPACE] and app_state == 'aiming and config':
            cb_exit_time_and_vel = calc_prereq_forces(9.8, 2000, 10, 5, 45) # test values
            app_state = 'firing'

        match app_state:
            case "aiming and config":
                cannon_barrel_and_angle = aiming_and_config_render(app_state, mouse, BARREL)
                # MAKE IT SO THAT THE CANNON STOPS ROTATING WHEN YOU FIRE IT
                # 1. wrap an if statement lines 35-52, modify as needed
                # 2. make a whole new drawing function (this would likely require you to make a new variable in main that stores theta so you can keep the barrel rotated)
            case "firing":
                pygame.time.delay(int(cb_exit_time_and_vel[0] * 1000)) # simulate cannon firing out of 
                # firing_cannon_render(cb_exit_time_and_vel, cannon_barrel_pos_and_ori)
                app_state = 'cannonball arc'
                # whichever velocity = cannonball's exit velocity * math.trig(angle of cannon)
                hori_init_vel = cb_exit_time_and_vel[1] * math.cos(cannon_barrel_and_angle[1])
                vert_init_vel = cb_exit_time_and_vel[1] * math.sin(cannon_barrel_and_angle[1])
            case "cannonball arc":
                render_cannonball_motion(cannon_barrel_and_angle, hori_init_vel, vert_init_vel, (100, 400), -9.8)


    pygame.QUIT()

# call it all-----------------------------------------------------------------------------------
if __name__ == "__main__":
    main()


