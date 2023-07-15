import pygame
import os

import gui

# init stuff
pygame.mixer.init()
pygame.font.init()

# set window
WIDTH, HEIGHT = 900, 500
WINDOW = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Cannonball - Python") # the title of the window

# init cannon to project
CANNON = pygame.image.load(os.path.join('Assets', 'cannon.png')).convert_alpha() # os.path.join instead of absolute path because different operating systems
CANNON = pygame.transform.scale(CANNON, (100, 100))

# shooting sound
SHOOT_SOUND = pygame.mixer.Sound(os.path.join('Assets', 'cannon-shoot.mp3'))

# test text
TEXT = pygame.font.SysFont('arial', 20)

#test image
IMAGE = pygame.image.load(os.path.join('Assets', 'testbtn.png'))
test_btn = gui.Button(300, 100, IMAGE, 0.75)

# test input
TEXT_INPUT = gui.Number_Input(300, 300, 'arial', 20, 255, 255, 255, 0, 1000)

# fps and movement of cannon
FPS = 10
MOVEMENT_VELOCITY = 3

# draw window (called every frame)
def draw_window(hitbox_x, hitbox_y):
    WINDOW.fill((50, 50, 50)) # need this to update every time or
    WINDOW.blit(CANNON, (hitbox_x, hitbox_y)) # draw assets, known as services

    test_text = TEXT.render('testing', 1, (255, 255, 255)) # not sure what the middle one does, but its a 0 or 1
    WINDOW.blit(test_text, (10, 10))

    TEXT_INPUT.render(WINDOW)

    # button update (blit) and event listener
    if test_btn.update(WINDOW):
        print("clicked")

    pygame.display.update()

# update movement (called every frame)
def handle_movement(keys_pressed_list, hitbox):
    # literally a list of keys with boolean values, so i doubt that case switches will work
    if keys_pressed_list[pygame.K_a]:
        hitbox.x -= MOVEMENT_VELOCITY
    if keys_pressed_list[pygame.K_d]:
        hitbox.x += MOVEMENT_VELOCITY
    if keys_pressed_list[pygame.K_s]: # coords read left right, top down
        hitbox.y += MOVEMENT_VELOCITY
    if keys_pressed_list[pygame.K_w]:
        hitbox.y -= MOVEMENT_VELOCITY
    if keys_pressed_list[pygame.K_SPACE]:
        SHOOT_SOUND.play()

# main program
def main():
    hitbox = pygame.Rect(200, 200, CANNON.get_width(), CANNON.get_height())

    clock = pygame.time.Clock()

    run = True
    while run:
        clock.tick(FPS) # runs in 10 fps

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            TEXT_INPUT.update_text_via_event(event)
            
        keys_pressed = pygame.key.get_pressed()

        handle_movement(keys_pressed, hitbox)
        draw_window(hitbox.x, hitbox.y)


    pygame.quit()

if __name__ == "__main__":
    main()

# coords and sets of data are usually in tuples