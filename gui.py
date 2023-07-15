import pygame

pygame.font.init()
number_keys_input = [pygame.K_0, pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5, pygame.K_6, pygame.K_7, pygame.K_8, pygame.K_9]

# create button classes to use in game
class Button():
    def __init__(self, x, y, image, scale): 
        width = image.get_width()
        height = image.get_height()
        self.image = pygame.transform.scale(image, (int(width * scale), int(height * scale)))
        self.rect = self.image.get_rect() # hitbox
        self.rect.topleft = (x, y)
        self.clicked = False

    def update(self, window):
        pressed = False

        cursor = pygame.mouse.get_pos()

        if self.rect.collidepoint(cursor): # if hitbox collides with mouse
            if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False: #self.clicked prevents multiple inputs when holding down mouse1
                pressed = True
                self.clicked = True

        if pygame.mouse.get_pressed()[0] == 0:
            self.clicked = False

        window.blit(self.image, (self.rect.x, self.rect.y))
        return pressed


class Number_Input():
    def __init__(self, x, y, font_type, font_size, r, g, b, min, max):
        self.element = pygame.font.SysFont(font_type, font_size)
        self.y = y
        self.x = x
        self.text = ''
        self.rgb = (r, g, b)
        self.selected = False
        self.font_size = font_size

    def update_text_via_event(self, event):
        if pygame.mouse.get_pressed()[0] == 1:
            if self.element.collidepoint(pygame.mouse.get_pos()): # collidepoint does not exist for sysfont
                self.selected = True
            else:
                self.selected = False
                return
            
        if self.selected:
            if event.type == pygame.KEYDOWN:
                if event.key in number_keys_input:
                    self.text += str(event.key)
                elif event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]

    def render(self, window):
        text_surface = self.element.render(self.text, True, self.rgb) # ig this is like finalizing the object data for blit?

        rect = pygame.Rect(self.x - 5, self.y - 5, max(30, text_surface.get_width()) + 5, self.font_size + 10)
        pygame.draw.rect(window, (255, 255, 255), rect, 2)

        window.blit(text_surface, (self.x, self.y))
    
    # first try too im goated
    # now make it check that its selected using a selected/active var and give it min/max cap values


        


        

        
