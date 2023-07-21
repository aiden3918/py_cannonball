import pygame
import math

pygame.init()
number_keys_list = [pygame.K_0, pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5, pygame.K_6, pygame.K_7, pygame.K_8, pygame.K_9]

# create button classes to use in game
class Button():
    def __init__(self, image, pos: tuple, size: tuple) -> None: 
        self.image = pygame.image.load(image)

        self.image = pygame.transform.scale(self.image, (int(size[0]), int(size[1])))

        self.rect = self.image.get_rect() # hitbox
        self.rect.topleft = pos
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

        window.blit(self.image, self.rect.topleft)
        return pressed


class Number_Input():
    def __init__(self, pos: tuple, size: tuple, font_type: str, font_size: int, color: tuple, background_color: tuple, initial_val: int, max_digits: int) -> None:
        self.element = pygame.font.SysFont(font_type, font_size)
        self.size = size
        self.pos = pos
        self.text_color = color
        self.bg_color = background_color
        self.selected = False
        self.font_size = font_size

        self.initial_val = initial_val
        self.text = str(initial_val)

        self.max_digits = max_digits

    def update(self, window, event_list):
        background = pygame.Rect(self.pos[0], self.pos[1], self.size[0], self.size[1])

        keys_pressed = pygame.key.get_pressed()

        if pygame.mouse.get_pressed()[0] == 1:
            if background.collidepoint(pygame.mouse.get_pos()): 
                self.selected = True
            else:
                self.selected = False
                return
            
        
        if self.selected:
            for i in range(10):
                if keys_pressed[number_keys_list[i]] and len(self.text) < self.max_digits:
                    self.text += str(i)
                    pygame.time.delay(100)
                    
            if self.text != "":
                if (keys_pressed[pygame.K_BACKSPACE]):
                        self.text = self.text[:-1]
                        pygame.time.delay(100)

        text_display = self.element.render(self.text, 1, self.text_color)
        pygame.draw.rect(window, self.bg_color, background)
        window.blit(text_display, (self.pos[0] + 5, self.pos[1]))

    def get_value(self):
        return int(self.text) if self.text != "" else ""
    
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

        self.min_val = min
        self.max_val = max
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
        return round(((current_val / val_range) * (self.max_val - self.min_val) + self.min_val) * rounding) / rounding

class Checkbox():
    def __init__(self, pos: tuple, side_length: int, color: tuple) -> None:
        self.pos = pos
        self.side_length = side_length
        self.color = color

        self.active = False
        self.outer_rect = pygame.Rect(self.pos[0], self.pos[1], self.side_length, self.side_length)
        self.inner_rect = pygame.Rect(self.pos[0] + 4, self.pos[1] + 4, self.side_length - 8, self.side_length - 8)

        self.mouse_is_down = False

    def update(self, window):
        pygame.draw.rect(window, self.color, self.outer_rect, 2)
        if self.active:
            pygame.draw.rect(window, self.color, self.inner_rect)

    def listen(self, mouse_get_pressed):
        if mouse_get_pressed[0] and self.outer_rect.collidepoint(pygame.mouse.get_pos()) and not self.mouse_is_down: 

            if self.active == False:
                self.active = True
            else:
                self.active = False

            self.mouse_is_down = True

        elif not mouse_get_pressed[0]:
            self.mouse_is_down = False
