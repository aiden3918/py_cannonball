import pygame
import math

pygame.font.init()
number_keys_input = [pygame.K_0, pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5, pygame.K_6, pygame.K_7, pygame.K_8, pygame.K_9]

# create button classes to use in game
class Button():
    def __init__(self, x: int, y: int, image, scale: float) -> None: 
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
    def __init__(self, x: int, y: int, font_type: str, font_size: int, color: tuple, min: float, max: float) -> None:
        self.element = pygame.font.SysFont(font_type, font_size)
        self.y = y
        self.x = x
        self.text = ''
        self.rgb = color
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

class Slider():
    # pos should be the center of the slider and where the button to drag begins (x, y)
    # size is the length and width of the slider (width, height)
    def __init__(self, pos: tuple, size: tuple, initial_val: float, min: int, max: int, container_color: tuple, slider_color: tuple, round_num_decimals: int) -> None:
        self.pos = pos
        self.size = size
        self.slider_right_pos = self.pos[0] + (size[0] // 2)
        self.slider_left_pos = self.pos[0] - (size[0] // 2)
        self.slider_top_pos = self.pos[1] - (size[1] // 2)

        self.container_color = container_color
        self.slider_color = slider_color

        self.min = min
        self.max = max
        self.initial_val = (self.slider_right_pos - self.slider_left_pos) * initial_val # <- float (0 to 1)

        self.rounded_to_nearest_decimal = round_num_decimals

        self.container_rect = pygame.Rect(self.slider_left_pos, self.slider_top_pos, self.size[0], self.size[1])
        self.drag_button_rect = pygame.Rect(self.slider_left_pos + self.initial_val - 5, self.slider_top_pos - 2, 10, self.size[1] + 4) # will stick out 2 pixels top and bottom

    def update(self, window, mouse_pos, mouse_pressed): # this will likely conflict with display upldate, unless i call it at the very end, which is kind of awkward
        if self.container_rect.collidepoint(mouse_pos) and mouse_pressed[0]:
            self.drag_button_rect.centerx = mouse_pos[0]

        pygame.draw.rect(window, self.container_color, self.container_rect)
        pygame.draw.rect(window, self.slider_color, self.drag_button_rect)

    def get_value(self):
        val_range = self.slider_right_pos - self.slider_left_pos
        current_val = self.drag_button_rect.centerx - self.slider_left_pos

        rounding = math.pow(10, self.rounded_to_nearest_decimal)
        return round(((current_val / val_range) * (self.max - self.min) + self.min) * rounding) / rounding
