import pygame
import os

import gui
import kinematics as k
import forces as f
import math
import angles as a

'''
pygame.mixer.init()
pygame.font.init()
'''

pygame.init()

# initialize window -----------------------------------------------------------------------------------
WINDOW_RES = (1280, 720)
WINDOW = pygame.display.set_mode(WINDOW_RES)
pygame.display.set_caption("Cannonball - Python/Pygame")
WINDOW_CENTER = (WINDOW_RES[0] // 2, WINDOW_RES[1] // 2)

GRID_BG = pygame.image.load(os.path.join('Assets', 'grid-background-white.png'))
GRID_BG = pygame.transform.scale(GRID_BG, WINDOW_RES)

# initialize sprites -----------------------------------------------------------------------------------
WHEEL = pygame.image.load(os.path.join('Assets', 'cannon-wheel-transparent.png')).convert_alpha()
WHEEL = pygame.transform.scale(WHEEL, (50, 50))
BARREL = pygame.image.load(os.path.join('Assets', 'cannon-barrel-transparent.png')).convert_alpha()
BARREL = pygame.transform.scale(BARREL, (120, 120))
CANNONBALL = pygame.image.load(os.path.join('Assets', 'cannonball-transparent.png')).convert_alpha()
CANNONBALL = pygame.transform.scale(CANNONBALL, (20, 20))

BARREL_CENTER = (110, 610)

FPS_TEXT = pygame.font.SysFont('arial', 22)
SECONDS_SINCE_EVENT_TEXT = pygame.font.SysFont('arial', 22)
FRAMES_SINCE_EVENT_TEXT = pygame.font.SysFont('arial', 22)
ANGLE_TEXT = pygame.font.SysFont('arial', 22)

seconds_since_event = 0
frames_since_event = 0
tracer_dots = []

# some constants and variables -----------------------------------------------------------------------------------
FPS = 60
BACKGROUND_COLOR = (100, 100, 100)
GREENISH = (105, 150, 62)
pixels_to_meters_rate = 11.2 # 11.2 is the # of pixelsp for every simulated meter

# update window -----------------------------------------------------------------------------------
def update_background():
    WINDOW.fill(BACKGROUND_COLOR)
    WINDOW.blit(GRID_BG, (0, 0))

def aiming_and_config_render(app_state, mouse, BARREL):
    ray_adj = mouse[0] - BARREL_CENTER[0]
    # switch coordinates to read that y-axis is at the bottom
    ray_opp = (WINDOW.get_height() - mouse[1]) - (WINDOW.get_height() - BARREL_CENTER[1]) # offset due to image translation + whitespace
    theta = math.atan2(ray_opp, ray_adj) * (180 / math.pi) # angle of cannon
    
    # theta cannot be greater than 90 or less than 0
    theta = min(theta, 90)
    theta = max(theta, 0)
    barrel_copy = pygame.transform.rotate(BARREL, theta)

    WINDOW.blit(barrel_copy, (BARREL_CENTER[0] - int(barrel_copy.get_width() / 2), BARREL_CENTER[1] - int(barrel_copy.get_height() / 2)))
    # basically, whenever rotating the object creates a surface on the back that completely covers the rotated object
    WINDOW.blit(WHEEL, (BARREL_CENTER[0] - 25, BARREL_CENTER[1] - 20))

    return [barrel_copy, theta]

# return time it would take for the cannonball to exit the cannon and the net velocity at which it will exit the cannon
# if there is not enough force, then returns list (-1, -1)
def calc_prereq_forces(gravity, force, cb_mass, barrel_length, angle):
    # assume cannon and cannonball have no friction

    # find net vertical force
    vert_force_applied = force * math.sin(a.conv_deg_to_rad(angle))
    vert_weight = f.calculate_forces('f', 0, cb_mass, gravity)
    normal_force = f.calculate_forces('f', 0, cb_mass, gravity) * math.cos(a.conv_deg_to_rad(angle))
    net_vert_force = vert_force_applied + normal_force - vert_weight

    # find net horizontal force
    hori_force_applied = force * math.cos(a.conv_deg_to_rad(angle))
    hori_weight = f.calculate_forces('f', 0, cb_mass, gravity) * math.sin(a.conv_deg_to_rad(angle))
    net_hori_force = hori_force_applied - hori_weight # - 0 (force of friction)

    # find net acceleration
    # if forces not great enough, dont launch
    if net_vert_force < 0 or net_hori_force < 0:
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

def render_cannonball_motion(cannon_barrel_copy_list, hori_vel, vert_vel, cannon_opening_pos, gravity, frames_elapsed):
    # calculate displacement
    time = (frames_elapsed / FPS)
    vertical_displacement = k.calc_d_using_vo_a_and_t(vert_vel, gravity, time) * pixels_to_meters_rate + 10
    horizontal_displacement = k.calculate_d_v_or_t('d', hori_vel, 0, time) * pixels_to_meters_rate - 10
    # the -10 is to center the cannonball bc it starts from top left (width/height of cb, also its diameter)

    cb_new_pos = (cannon_opening_pos[0] + horizontal_displacement, cannon_opening_pos[1] - vertical_displacement)
    # add one every quarter second (15 frames)
    if time % 0.25 == 0:
        tracer_dots.append((cb_new_pos[0] + 10, cb_new_pos[1] + 10))

    # render cannonball based on cannon's position and horizontal and vertical displacement
    WINDOW.blit(CANNONBALL, cb_new_pos)

    # just keep rending cannon using a copy
    cannon_barrel_copy = cannon_barrel_copy_list[0]
    WINDOW.blit(cannon_barrel_copy, (BARREL_CENTER[0] - int(cannon_barrel_copy.get_width() / 2), BARREL_CENTER[1] - int(cannon_barrel_copy.get_height() / 2)))
    WINDOW.blit(WHEEL, (BARREL_CENTER[0] - 25, BARREL_CENTER[1] - 20))

    # keep drawing all tracer dots
    for coordinate in tracer_dots:
        pygame.draw.circle(WINDOW, (200, 0, 0), coordinate, 5)

def update_display_data(clock, frames_elapsed, angle):
    # render data during launch (after cannonball leaves cannon)
    FPS_DISPLAY = FPS_TEXT.render(f'FPS : {int(clock.get_fps())}', 1, GREENISH)
    SECONDS_SINCE_EVENT_DISPLAY = SECONDS_SINCE_EVENT_TEXT.render(f'Seconds since cb exited c: {round(1000 * frames_elapsed / FPS) / 1000}', 1, GREENISH)
    FRAMES_SINCE_EVENT_DISPLAY = FRAMES_SINCE_EVENT_TEXT.render(f'Frames since cb exited c: {frames_elapsed}', 1, GREENISH)
    
    rounded_angle = round(angle * 100) / 100
    ANGLE_DISPLAY = ANGLE_TEXT.render(f"Angle: {rounded_angle}", 1, GREENISH)

    WINDOW.blit(FPS_DISPLAY, (20, 20))
    WINDOW.blit(SECONDS_SINCE_EVENT_DISPLAY, (20, 50))
    WINDOW.blit(FRAMES_SINCE_EVENT_DISPLAY, (20, 80))
    WINDOW.blit(ANGLE_DISPLAY, (300, 20))

def render_inputs():
    pass

# main function -----------------------------------------------------------------------------------
def main():

    clock = pygame.time.Clock()
    run = True
    app_state = 'aiming and config'
    frames_elapsed = 0

    while run:
        
        clock.tick(FPS)

        mouse = pygame.mouse.get_pos()
        keys_pressed = pygame.key.get_pressed()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                print(mouse)

        if keys_pressed[pygame.K_SPACE]:
            if app_state == 'aiming and config':
                cb_exit_time_and_vel = calc_prereq_forces(gravity=9.8, force=500, cb_mass=10, barrel_length=5, angle=barrel_angle) # test values
                if cb_exit_time_and_vel != (-1, -1):
                    app_state = 'firing'

        update_background()

        match app_state:
            case "aiming and config":
                frames_elapsed = 0
                cannon_barrel_and_angle = aiming_and_config_render(app_state, mouse, BARREL)
                barrel_angle = cannon_barrel_and_angle[1]
                render_inputs()
            case "firing":
                pygame.time.delay(int(cb_exit_time_and_vel[0] * 1000)) # simulate cannonball firing out of cannon by just waiting for it to come out lol 
                # whichever velocity = cannonball's exit velocity * math.trig(angle of cannon)
                hori_init_vel = cb_exit_time_and_vel[1] * math.cos(barrel_angle * math.pi / 180)
                vert_init_vel = cb_exit_time_and_vel[1] * math.sin(barrel_angle * math.pi / 180)

                print(f'''
                    horizontal exit velocity: {hori_init_vel}   
                    vertical exit velocity: {vert_init_vel}
                ''')

                barrel_relative_length = int(BARREL.get_width() / 2)
                cannon_opening_offset = (BARREL_CENTER[0] + int(barrel_relative_length * math.cos(a.conv_deg_to_rad(barrel_angle))), BARREL_CENTER[1] - int(barrel_relative_length * math.sin(a.conv_deg_to_rad(barrel_angle))), )
                
                app_state = 'cannonball arc'
            case "cannonball arc":
                render_cannonball_motion(cannon_barrel_and_angle, hori_init_vel, vert_init_vel, cannon_opening_offset, -9.8, frames_elapsed)
                frames_elapsed += 1
        
        update_display_data(clock, frames_elapsed, barrel_angle)

        pygame.display.update()

    pygame.QUIT()

# call it all babyyyyyy -----------------------------------------------------------------------------------
if __name__ == "__main__":
    main()


