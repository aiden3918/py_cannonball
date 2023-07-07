import pygame
import os

WIDTH, HEIGHT = 900, 500
WINDOW = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Hello") # the title of the window

CANNON = pygame.image.load(os.path.join('Assets', 'cannon.png')) # os.path.join instead of absolute path because different operating systems
CANNON = pygame.transform.scale(CANNON, (100, 100))

FPS = 10
MOVEMENT_VELOCITY = 3

def draw_window(hitboxX, hitboxY):
    WINDOW.fill((0, 0, 255)) # need this to update every time or
    WINDOW.blit(CANNON, (hitboxX, hitboxY)) # draw assets, known as services 
    pygame.display.update()

def main():
    hitbox = pygame.Rect(200, 200, 1, 1)

    clock = pygame.time.Clock()

    run = True
    while run:
        clock.tick(FPS) # runs in 10 fps

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            
        keys_pressed = pygame.key.get_pressed()

        if keys_pressed[pygame.K_a]:
            hitbox.x -= MOVEMENT_VELOCITY
        if keys_pressed[pygame.K_d]:
            hitbox.x += MOVEMENT_VELOCITY
        if keys_pressed[pygame.K_s]: # coords read left right, top down
            hitbox.y += MOVEMENT_VELOCITY
        if keys_pressed[pygame.K_w]:
            hitbox.y -= MOVEMENT_VELOCITY

 
        draw_window(hitbox.x, hitbox.y)

    pygame.quit()


if __name__ == "__main__":
    print(os.path.abspath('cannon.png'))
    main()

# coords and sets of data are usually in tuples