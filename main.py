import pygame
import os

import gui
import kinematics as k
import forces as f
import math
import angles as a

pygame.init()

# initialize window -----------------------------------------------------------------------------------
WINDOW_RES = (1280, 720)
WINDOW = pygame.display.set_mode(WINDOW_RES)
pygame.display.set_caption("Cannonball - Python/Pygame")
WINDOW_CENTER = (WINDOW_RES[0] // 2, WINDOW_RES[1] // 2)

# background
GRID_BG = pygame.image.load(os.path.join('Assets', 'grid-background-1280.png'))

# initialize sprites -----------------------------------------------------------------------------------
WHEEL = pygame.image.load(os.path.join('Assets', 'cannon-wheel-transparent.png')).convert_alpha()
WHEEL = pygame.transform.scale(WHEEL, (50, 50))
BARREL = pygame.image.load(os.path.join('Assets', 'cannon-barrel-transparent.png')).convert_alpha()
BARREL = pygame.transform.scale(BARREL, (120, 120))
CANNONBALL = pygame.image.load(os.path.join('Assets', 'cannonball-transparent.png')).convert_alpha()
CANNONBALL_SIZE = 14
CANNONBALL = pygame.transform.scale(CANNONBALL, (CANNONBALL_SIZE, CANNONBALL_SIZE))
CANNONBALL_HALF_OF_SIZE = CANNONBALL_SIZE // 2

CANNONBALL_PHYSICS_DATA_FONT = pygame.font.SysFont('arial', 20, True)

BARREL_CENTER = (120, 600)

# performance data
PERF_DATA_FONT = pygame.font.SysFont('arial', 22)
ANGLE_TEXT = pygame.font.SysFont('arial', 20, True)

# firing state variables
seconds_since_event = 0
frames_since_event = 0
tracer_dots = []

# user input panel
USER_PANEL = pygame.Surface((880, 200))
USER_PANEL.set_alpha(200)
USER_PANEL.fill((150, 150, 150))

# user inputs and their labels
WHITISH = (200, 200, 200)
GRAYISH = (100, 100, 100)
WHITE = (255, 255, 255)
GREENISH = (105, 150, 62)
BLACK = (0, 0, 0)

cannonball_mass_slider_input = gui.Slider((400, 120), (100, 20), 0.1, 0, 100, WHITISH, GRAYISH, 1)
gravity_slider_input = gui.Slider((800, 50), (100, 20), 0.49, 0, 20, WHITISH, GRAYISH, 1)
barrel_length_slider_input = gui.Slider((800, 120), (100, 20), 0.25, 0, 20, WHITISH, GRAYISH, 1)
user_slider_inputs = [cannonball_mass_slider_input, gravity_slider_input, barrel_length_slider_input]

USER_INPUT_FONT = pygame.font.SysFont('arial', 22)

FORCE_NUM_INPUT = gui.Number_Input((350, 20), (100, 30), 'arial', 22, GRAYISH, WHITISH, 1000, 5)
SUBTEXT_FONT = pygame.font.SysFont('arial', 14)

SHOW_PERF_STATS_CHECKBOX = gui.Checkbox((150, 20), 20, GREENISH)
SHOW_CB_EXIT_DATA_CHECKBOX = gui.Checkbox((150, 45), 20, GREENISH)
MUTE_CHECKBOX = gui.Checkbox((150, 70), 20, GREENISH)

# other settings
MORE_INFO_BTN = gui.Button(os.path.join('Assets', 'question-mark.png'), (1220, 10), (50, 50))
MORE_INFO = pygame.image.load(os.path.join('Assets', 'description.png'))
RETURN_INFO_TEXT = USER_INPUT_FONT.render("Press any key to continue...", 1, BLACK)

# sounds -----------------------------------------------------------------------------------
CANNON_SHOOT_SOUND = pygame.mixer.Sound(os.path.join('Assets', 'cannon-shoot.mp3'))
INVALID_INPUT_SOUND = pygame.mixer.Sound(os.path.join('Assets', 'invalid-input.mp3'))
INVALID_INPUT_SOUND.set_volume(0.3)

# some constants and variables -----------------------------------------------------------------------------------
FPS = 60
BACKGROUND_COLOR = (100, 100, 100)
pixels_to_meters_rate = 6.0 # this is rate of the number of pixels for every simulated meter
dots_per_sec = 4

# update background -----------------------------------------------------------------------------------
def update_background():
    WINDOW.fill(BACKGROUND_COLOR)
    WINDOW.blit(GRID_BG, (0, 0))

# play sound if user has not decided to mute
def play_sound_if_needed():
    INVALID_INPUT_SOUND.stop()
    if not MUTE_CHECKBOX.active:
        INVALID_INPUT_SOUND.play()

# update cannon when aiming -----------------------------------------------------------------------------------
# parameters: app state, mouse position, barrel image, barrel length
# returns: a copy of the barrel image, the angle
def aiming_and_config_render(app_state, mouse, BARREL, barrel_length):
    WINDOW.blit(USER_PANEL, (200, 0))

    ray_adj = mouse[0] - BARREL_CENTER[0]
    # switch coordinates to read that y-axis is at the bottom
    ray_opp = (WINDOW.get_height() - mouse[1]) - (WINDOW.get_height() - BARREL_CENTER[1]) # offset due to image translation + whitespace
    theta = a.conv_rad_to_deg(math.atan2(ray_opp, ray_adj)) # angle of cannon
    
    # theta cannot be greater than 90 or less than 0
    theta = min(theta, 90)
    theta = max(theta, 0)
    barrel_copy = pygame.transform.scale(BARREL, (barrel_length * (pixels_to_meters_rate + (19/17)) * 2, 120))
    # +18/17 to compensate for whitespace on the actual image file (170 -> 180) and the centering distortion (+1/17), maybe thats how it works, idk, looks good tho
    # *2 because thats how the file works (other side is whitespace)
    barrel_copy = pygame.transform.rotate(barrel_copy, theta)

    rounded_theta = round(theta * 100) / 100
    ANGLE_DISPLAY = ANGLE_TEXT.render(f"Angle: {rounded_theta}°", 1, (0, 0, 0))
    WINDOW.blit(ANGLE_DISPLAY, (125, 615))

    WINDOW.blit(barrel_copy, (BARREL_CENTER[0] - int(barrel_copy.get_width() / 2), BARREL_CENTER[1] - int(barrel_copy.get_height() / 2)))
    # basically, whenever rotating the object creates a surface on the back that completely covers the rotated object
    WINDOW.blit(WHEEL, (BARREL_CENTER[0] - 25, BARREL_CENTER[1] - 20))

    return (barrel_copy, theta)

# render user input elements during aiming and config -----------------------------------------------------------------------------------
# parameters: mouse position, whether or not mouse was pressed, pygame event loop
# returns: whether or not the more info button was clicked
def render_inputs(mouse_pos, mouse_pressed, event):

    FORCE_NUM_INPUT.update(WINDOW, pygame.event.get())
    
    for input in user_slider_inputs:
        input.update(WINDOW, mouse_pos, mouse_pressed)
    
    force_text_rendered = USER_INPUT_FONT.render(f'Force:                        N', 1, WHITE)
    cb_mass_rendered = USER_INPUT_FONT.render(f'Cannonball Mass: {cannonball_mass_slider_input.get_value()} kg', 1, WHITE)
    gravity_rendered = USER_INPUT_FONT.render(f'Gravity: {gravity_slider_input.get_value()} m/s^2', 1, WHITE)
    barrel_length_rendered = USER_INPUT_FONT.render(f'Barrel Length: {barrel_length_slider_input.get_value()} m', 1, WHITE)

    SUBTEXT_FONT_text = SUBTEXT_FONT.render('Note: min = 0, max = 10,000', 1, WHITE)

    SHOW_PERF_STATS_CHECKBOX.listen(mouse_pressed)
    SHOW_PERF_STATS_CHECKBOX.update(WINDOW)
    show_perf_stats_text = SUBTEXT_FONT.render("Show performance stats:", 1, SHOW_PERF_STATS_CHECKBOX.color)

    SHOW_CB_EXIT_DATA_CHECKBOX.listen(mouse_pressed)
    SHOW_CB_EXIT_DATA_CHECKBOX.update(WINDOW)
    show_cb_exit_data_text = SUBTEXT_FONT.render("Show cannonball exit data:", 1, SHOW_CB_EXIT_DATA_CHECKBOX.color)

    MUTE_CHECKBOX.listen(mouse_pressed)
    MUTE_CHECKBOX.update(WINDOW)
    mute_check_box_text = SUBTEXT_FONT.render("Mute sound:", 1, SHOW_CB_EXIT_DATA_CHECKBOX.color)

    WINDOW.blit(force_text_rendered, (FORCE_NUM_INPUT.pos[0] - 60, FORCE_NUM_INPUT.pos[1]))
    WINDOW.blit(cb_mass_rendered, (cannonball_mass_slider_input.pos[0] - (cb_mass_rendered.get_width() // 2), cannonball_mass_slider_input.pos[1] - 40))
    WINDOW.blit(gravity_rendered, (gravity_slider_input.pos[0] - (gravity_rendered.get_width() // 2), gravity_slider_input.pos[1] - 40))
    WINDOW.blit(barrel_length_rendered, (barrel_length_slider_input.pos[0] - (barrel_length_rendered.get_width() // 2), barrel_length_slider_input.pos[1] - 40))
    WINDOW.blit(SUBTEXT_FONT_text, (FORCE_NUM_INPUT.pos[0] - 30, FORCE_NUM_INPUT.pos[1] + 32))

    WINDOW.blit(show_perf_stats_text, (SHOW_PERF_STATS_CHECKBOX.pos[0] - 140, SHOW_PERF_STATS_CHECKBOX.pos[1]))
    WINDOW.blit(show_cb_exit_data_text, (SHOW_CB_EXIT_DATA_CHECKBOX.pos[0] - 140, SHOW_CB_EXIT_DATA_CHECKBOX.pos[1]))
    WINDOW.blit(mute_check_box_text, (MUTE_CHECKBOX.pos[0] - 140, MUTE_CHECKBOX.pos[1]))

    return MORE_INFO_BTN.update(WINDOW)
        

# calculate forces and information needed when user fires -----------------------------------------------------------------------------------
# return time it would take for the cannonball to exit the cannon and the net velocity at which it will exit the cannon
# if there is not enough force, then returns list (-1, -1)
def calc_prereq_forces(gravity, force, cb_mass, barrel_length, angle):
    # assume cannon and cannonball have no friction

    # find net vertical force
    vert_force_applied = force * math.sin(a.conv_deg_to_rad(angle))
    vert_weight = f.calculate_forces('f', 0, cb_mass, gravity)
    vert_normal_force = vert_weight * math.cos(a.conv_deg_to_rad(angle)) if angle != 90 else vert_weight # is the cannon's angle the right one
    print(f"Weight: {vert_weight}")
    print(f'vert normal force: {vert_normal_force}')
    net_vert_force = max(vert_force_applied + vert_normal_force - vert_weight, 0)
    print(f"net vert force: {net_vert_force}")
    # does the bug occur because once the cb leaves the ground, there is no longer any normal force acting on it?
    # get back to this

    # find net horizontal force
    hori_force_applied = force * math.cos(a.conv_deg_to_rad(angle))
    hori_normal_force = f.calculate_forces('f', 0, cb_mass, gravity) * math.sin(a.conv_deg_to_rad(angle))
    net_hori_force = max(hori_force_applied - hori_normal_force, 0) # - 0 (force of friction)
    print(f'''
        hori force applied: {hori_force_applied}
        hori normal force: {hori_normal_force}
        net hori force: {net_hori_force}
          ''')

    # find net acceleration
    # if forces not great enough, dont launch
    if net_vert_force == 0 and net_hori_force == 0:
        return ((-1, -1), 0, 0, 0, 0, 0, 0, 0, 0, 0, angle)
    else: 
        net_force = math.sqrt(math.pow(net_vert_force, 2) + math.pow(net_hori_force, 2))
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

        #                                                                 |                                                      |                                                         
        return ((exit_cannon_time, exit_cannon_vel), net_force, net_accel, hori_force_applied, hori_normal_force, net_hori_force, vert_force_applied, vert_normal_force, vert_weight, net_vert_force, angle)
    
# render the cannonball shooting in a straight line out of the cannon -----------------------------------------------------------------------------------
# paramters: acceleration, angle, barrel length, frames elapsed since space key was pressed, dots per sec for tracer, (cannon barrel image copy, angle)
# returns: (cannonball displacement is greater than or equal to cannon (if it has shot out), most recent (x, y) of cannonball)
def render_cannonball_exiting_cannon(acceleration, angle, barrel_length, frames_elapsed, dots_per_sec, cannon_barrel_copy_list):
    if SHOW_CB_EXIT_DATA_CHECKBOX.active:
        WINDOW.blit(USER_PANEL, (200, 0))

    time_elapsed = frames_elapsed / FPS

    # calculate displacement using net acceleration
    vec_displacement = k.calc_d_using_vo_a_and_t(0, acceleration, time_elapsed) * pixels_to_meters_rate
    hori_displacement = vec_displacement * math.cos(a.conv_deg_to_rad(angle))
    vert_displacement = vec_displacement * math.sin(a.conv_deg_to_rad(angle))

    cb_new_pos = (BARREL_CENTER[0] + hori_displacement - CANNONBALL_HALF_OF_SIZE, BARREL_CENTER[1] - vert_displacement - CANNONBALL_HALF_OF_SIZE)
    WINDOW.blit(CANNONBALL, (cb_new_pos))

    # have to draw the cannon still
    cannon_barrel_copy = cannon_barrel_copy_list[0]
    WINDOW.blit(cannon_barrel_copy, (BARREL_CENTER[0] - int(cannon_barrel_copy.get_width() / 2), BARREL_CENTER[1] - int(cannon_barrel_copy.get_height() / 2)))
    WINDOW.blit(WHEEL, (BARREL_CENTER[0] - 25, BARREL_CENTER[1] - 20))

    return (vec_displacement >= barrel_length * pixels_to_meters_rate, cb_new_pos)

# render motion of cannonball -----------------------------------------------------------------------------------
# parameters: (cannonball copy image, angle), horizontal velocity, vertical velocity, cannon opening position, gravity, frames elasped since firing, dots per sec for tracer
# no return
def render_cannonball_motion(cannon_barrel_copy_list, hori_vel, vert_vel, cannon_opening_pos, gravity, frames_elapsed, dots_per_sec):
    # calculate displacement
    time = (frames_elapsed / FPS)
    vertical_displacement = k.calc_d_using_vo_a_and_t(vert_vel, gravity, time) * pixels_to_meters_rate
    horizontal_displacement = k.calculate_d_v_or_t('d', hori_vel, 0, time) * pixels_to_meters_rate
    # the -10 is to center the cannonball bc it starts from top left (width/height of cb, also its diameter)

    cb_new_pos = (cannon_opening_pos[0] + horizontal_displacement, cannon_opening_pos[1] - vertical_displacement)


    # render cannonball based on cannon's position and horizontal and vertical displacement
    WINDOW.blit(CANNONBALL, cb_new_pos)

    # just keep rending cannon using a copy
    cannon_barrel_copy = cannon_barrel_copy_list[0]
    WINDOW.blit(cannon_barrel_copy, (BARREL_CENTER[0] - int(cannon_barrel_copy.get_width() / 2), BARREL_CENTER[1] - int(cannon_barrel_copy.get_height() / 2)))
    WINDOW.blit(WHEEL, (BARREL_CENTER[0] - 25, BARREL_CENTER[1] - 20))

    update_tracers(dots_per_sec, time, cb_new_pos)

# renders cannonball exit data -----------------------------------------------------------------------------------
# parameters: cannonball data in a tuple
# returns: a list containing all of the text that will format this information
def render_cb_exit_data_text(cannonball_data_tuple):
    # the tuple in question: ^ ((exit_cannon_time, exit_cannon_vel), net_force, net_accel ||| hori_force_applied, hori_normal, net_hori_force, ||| vert_force_applied, vert_normal_force, vert_weight, net_vert_force, angle)

    # return a list of the rendered text to traverse later
    return [
        CANNONBALL_PHYSICS_DATA_FONT.render(f'Cannonball exit time: {round(cannonball_data_tuple[0][0] * 100) / 100} s', 1, WHITE),
        CANNONBALL_PHYSICS_DATA_FONT.render(f'Cannonball exit velocity: {round(cannonball_data_tuple[0][1] * 100) / 100} m/s', 1, WHITE),
        CANNONBALL_PHYSICS_DATA_FONT.render(f'Cannonball net force: {round(cannonball_data_tuple[1] * 100) / 100} N', 1, WHITE),
        CANNONBALL_PHYSICS_DATA_FONT.render(f'Cannonball net acceleration: {round(cannonball_data_tuple[2] * 100) / 100} m/s^2', 1, WHITE),

        CANNONBALL_PHYSICS_DATA_FONT.render(f'Horizontal force applied: {round(cannonball_data_tuple[3] * 100) / 100} N', 1, WHITE),
        CANNONBALL_PHYSICS_DATA_FONT.render(f'Net horizontal force: {round(cannonball_data_tuple[5] * 100) / 100} N', 1, WHITE),
        CANNONBALL_PHYSICS_DATA_FONT.render(f'Net horizontal force: {round(cannonball_data_tuple[5] * 100) / 100} N', 1, WHITE),
        
        CANNONBALL_PHYSICS_DATA_FONT.render(f'Vertical force applied: {round(cannonball_data_tuple[6]* 100) / 100} N', 1, WHITE),
        CANNONBALL_PHYSICS_DATA_FONT.render(f'Vertical normal force: {round(cannonball_data_tuple[7] * 100) / 100} N', 1, WHITE),
        CANNONBALL_PHYSICS_DATA_FONT.render(f'Vertical weight: {round(cannonball_data_tuple[8] * 100) / 100} N', 1, WHITE),
        CANNONBALL_PHYSICS_DATA_FONT.render(f'Net vertical force: {round(cannonball_data_tuple[9] * 100) / 100} N', 1, WHITE)
    ]

# renders cannonball exit data every frame -----------------------------------------------------------------------------------
# separated from above because only one render is needed beforehand
# paramters: list from render_cb_exit_data_text
# no return
def draw_cb_exit_data_text(cb_exit_data_strs_list):
    WINDOW.blit(USER_PANEL, (200, 0))

    x = 220
    y = 25
    for i in range(0, 4):
        WINDOW.blit(cb_exit_data_strs_list[i], (x, y))
        y += 30
    
    x += 300
    y = 25
    for i in range(4, 7):
        WINDOW.blit(cb_exit_data_strs_list[i], (x, y))
        y += 30

    x += 300
    y = 25
    for i in range(7, 11):
        WINDOW.blit(cb_exit_data_strs_list[i], (x, y))
        y += 30
    

# update performance data on the bottom -----------------------------------------------------------------------------------
# parmaters: pygame clock, frames elapsed since firing, angle
# no returns
def update_display_data(clock, frames_elapsed, angle):
    # render data during launch (after cannonball leaves cannon)
    FPS_DISPLAY = PERF_DATA_FONT.render(f'FPS : {int(clock.get_fps())}', 1, GREENISH)
    SECONDS_SINCE_EVENT_DISPLAY = PERF_DATA_FONT.render(f'Seconds since cb launch: {round(1000 * frames_elapsed / FPS) / 1000}', 1, GREENISH)
    FRAMES_SINCE_EVENT_DISPLAY = PERF_DATA_FONT.render(f'Frames since cb launch: {frames_elapsed}', 1, GREENISH)
    
    WINDOW.blit(FPS_DISPLAY, (20, 660))
    WINDOW.blit(SECONDS_SINCE_EVENT_DISPLAY, (20, 690))
    WINDOW.blit(FRAMES_SINCE_EVENT_DISPLAY, (300, 660))

def update_tracers(dots_per_sec, time, cb_new_pos):
    # add one every quarter second (15 frames)
    if time % (1 / dots_per_sec) == 0: # cheking anyt time under every 0.25 seconds doesnt work for whatever reason
        tracer_dots.append([cb_new_pos[0] + CANNONBALL_HALF_OF_SIZE, cb_new_pos[1] + CANNONBALL_HALF_OF_SIZE, (200, 0, 0), 3])
        if time == round(time):
            tracer_dots[-1][2] = (0, 0, 200) 
            tracer_dots[-1][3] = 4 
            
    # keep drawing all tracer dots
    for tracer_data in tracer_dots:
        pygame.draw.circle(WINDOW, tracer_data[2], (tracer_data[0], tracer_data[1]), tracer_data[3])

def render_more_info():
    more_info_rect = MORE_INFO.get_rect()
    half_of_more_info =  (more_info_rect.width // 2, more_info_rect.height // 2)

    return_info_text_rect = RETURN_INFO_TEXT.get_rect()
    half_of_return_info = (return_info_text_rect.width // 2, return_info_text_rect.height // 2)

    WINDOW.blit(MORE_INFO, (WINDOW_CENTER[0] - half_of_more_info[0], WINDOW_CENTER[1] - half_of_more_info[1]))
    WINDOW.blit(RETURN_INFO_TEXT, (WINDOW_CENTER[0] - half_of_return_info[0], 650))

# main function -----------------------------------------------------------------------------------
# no paramters, no returns
def main():

    clock = pygame.time.Clock()
    run = True
    app_state = 'aiming and config'
    frames_elapsed = 0

    while run:

        clock.tick(FPS)

        mouse = pygame.mouse.get_pos()
        mouse_pressed = pygame.mouse.get_pressed()
        keys_pressed = pygame.key.get_pressed()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                print(mouse)
            if event.type == pygame.KEYDOWN:
                if app_state == 'more info':
                    app_state = 'aiming and config'

        if keys_pressed[pygame.K_SPACE]:
            if app_state == 'aiming and config':

                force_input_val = FORCE_NUM_INPUT.get_value()
                if force_input_val == "" or force_input_val < 0 or force_input_val > 10_000:
                    play_sound_if_needed()
                else:
                    cannonball_physics_data = calc_prereq_forces(gravity=gravity_slider_input.get_value(), force=force_input_val, cb_mass=cannonball_mass_slider_input.get_value(), barrel_length=barrel_length_slider_input.get_value(), angle=barrel_angle) # test values
                    # ^ ((exit_cannon_time, exit_cannon_vel), net_force, net_accel, ||| hori_force_applied, hori_normal_force, net_hori_force, ||| vert_force_applied, vert_normal_force, vert_weight, net_vert_force, angle)
                    print(f'cannonball_physics_data: {cannonball_physics_data}')
                    if cannonball_physics_data[0] != (-1, -1):
                        play_sound_if_needed()
                        FORCE_NUM_INPUT.selected = False
                        app_state = 'firing'
                    else:
                        play_sound_if_needed()

        update_background()

        # for different "states" of application (what is currently happening)
        match app_state:
            case "aiming and config":
                frames_elapsed = 0
                barrel_copy_and_angle = aiming_and_config_render(app_state, mouse, BARREL, barrel_length_slider_input.get_value())
                # ^ (image surface to keep rendering, angle) 

                barrel_angle = barrel_copy_and_angle[1]

                if render_inputs(mouse, mouse_pressed, pygame.event.get()):
                    app_state = 'more info'
            case "more info":
                render_more_info()
            case "firing":

                # (returns boolean; whether the displacement is greater or equal to barrel length, (new displacement of cannonball x, y))
                cb_exiting_cannon_data = render_cannonball_exiting_cannon(cannonball_physics_data[2], cannonball_physics_data[-1], barrel_length_slider_input.get_value(), frames_elapsed, dots_per_sec, barrel_copy_and_angle)
                
                if cb_exiting_cannon_data[0]:
                    hori_init_vel = cannonball_physics_data[0][1] * math.cos(barrel_angle * math.pi / 180)
                    vert_init_vel = cannonball_physics_data[0][1] * math.sin(barrel_angle * math.pi / 180)

                    # whichever velocity = cannonball's exit velocity * math.trig(angle of cannon)
                    print(f'''
                        horizontal exit velocity: {hori_init_vel}   
                        vertical exit velocity: {vert_init_vel}
                    ''')

                    cannon_exit_pos = cb_exiting_cannon_data[1]
                    frame_where_cb_exits_cannon = frames_elapsed
                    app_state = 'cannonball arc'

                    cb_exit_data_strs_list = render_cb_exit_data_text(cannonball_physics_data)
                    tracer_dots.append([cb_exiting_cannon_data[1][0] + CANNONBALL_HALF_OF_SIZE, cb_exiting_cannon_data[1][1] + CANNONBALL_HALF_OF_SIZE, (0, 0, 200), 4])
                
                frames_elapsed += 1

            case "cannonball arc":
                render_cannonball_motion(barrel_copy_and_angle, hori_init_vel, vert_init_vel, cannon_exit_pos, -gravity_slider_input.get_value(), frames_elapsed - frame_where_cb_exits_cannon, dots_per_sec)
                
                if SHOW_CB_EXIT_DATA_CHECKBOX.active:
                    draw_cb_exit_data_text(cb_exit_data_strs_list)

                frames_elapsed += 1

                if (frames_elapsed > FPS and keys_pressed[pygame.K_r]) or frames_elapsed > FPS * 20:
                    tracer_dots.clear()
                    app_state = 'aiming and config'
        
        if SHOW_PERF_STATS_CHECKBOX.active:
            update_display_data(clock, frames_elapsed, barrel_angle)

        pygame.display.update()

    pygame.QUIT()

# call it all -----------------------------------------------------------------------------------
if __name__ == "__main__":
    main()

