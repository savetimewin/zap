import pygame
import sys
import math
import random


class zap(object):
    def __init__(self):
        pygame.init()
        self.minutes_passed = 0
        self.screen = pygame.display.set_mode((800, 600))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 32)

        self.screen_width, self.screen_height = self.screen.get_size()
        self.character_pos = [self.screen_width // 2, self.screen_height // 2]

        self.character_size = 50
        self.laser_speed = 5 * 1.5
        self.lasers = []
        self.cooldown_timer = 0

        self.game_started = False
        self.start_time = None

        self.start_game_rect = None
        self.shapes = []
        self.next_shape_time = pygame.time.get_ticks()
        self.shape_multiplier = 1

        # Allowable shapes (rectangles and polygons) and colors
        self.available_shapes = ["rectangle"]
        self.available_colors = [(r, g, b) for r in range(256) for g in range(256) for b in range(256)
                                 if (r, g, b) not in [(255, 255, 255), (0, 255, 0), (255, 105, 180), (0, 0, 0)]]
        # Define the try again button
        button_width = 200
        button_height = 50
        button_x = self.screen_width / 2 - button_width / 2  # Centered on the screen
        button_y = self.screen_height / 2  # Middle of the screen
        self.try_again_button = pygame.Rect(button_x, button_y, button_width, button_height)

    def start_game(self):
        self.reset_game_state(auto_start=True)

    def reset_game_state(self, auto_start=False):
        self.character_pos = [self.screen_width // 2, self.screen_height // 2]
        self.lasers = []
        self.shapes = []
        self.cooldown_timer = 0
        self.shape_multiplier = 1
        self.minutes_passed = 0
        self.next_shape_time = pygame.time.get_ticks() + 3000
        self.game_started = auto_start
        self.start_time = pygame.time.get_ticks() if auto_start else None

    def draw_start_screen(self):
        self.screen.fill((255, 255, 255))  # white background

        text = self.font.render("Start Game", True, (0, 0, 0))  # black text
        rect = text.get_rect()
        rect.inflate_ip(100, 50)  # increases the size of the rectangle by 100 pixels in width and 50 in height
        rect.center = self.screen_width // 2, self.screen_height // 2

        pygame.draw.rect(self.screen, (0, 0, 0), rect, 2)  # black rectangle border

        # create a new rect for text, place it at the center of the button rectangle
        text_rect = text.get_rect()
        text_rect.center = rect.center
        self.screen.blit(text, text_rect)

        self.start_game_rect = rect

    def process_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if self.game_started:
                    if event.key in {pygame.K_a, pygame.K_d, pygame.K_s, pygame.K_w,
                                     pygame.K_e, pygame.K_q, pygame.K_z, pygame.K_c, pygame.K_x}:  # added pygame.K_x
                        self.shoot(event.key)
                else:
                    if event.key == pygame.K_RETURN:
                        if self.start_game_rect:
                            self.start_game()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if (not self.game_started and self.start_game_rect and
                        self.start_game_rect.collidepoint(pygame.mouse.get_pos())):
                    self.start_game()

    def move_character(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP]:
            self.character_pos[1] -= 5
        if keys[pygame.K_DOWN]:
            self.character_pos[1] += 5
        if keys[pygame.K_LEFT]:
            self.character_pos[0] -= 5
        if keys[pygame.K_RIGHT]:
            self.character_pos[0] += 5

        self.character_pos[0] = max(
            min(self.character_pos[0], self.screen_width - self.character_size // 2),
            self.character_size // 2,
        )
        self.character_pos[1] = max(
            min(self.character_pos[1], self.screen_height - self.character_size // 2),
            self.character_size // 2,
        )

    def draw_character(self):
        radius = self.character_size // 2
        radius_cos_45 = radius * math.cos(math.radians(45))

        pygame.draw.circle(self.screen, (255, 105, 180), self.character_pos, radius, 1)

        pygame.draw.line(
            self.screen, (255, 105, 180),
            (self.character_pos[0], self.character_pos[1] - radius),
            (self.character_pos[0], self.character_pos[1] + radius),
            1
        )
        pygame.draw.line(
            self.screen, (255, 105, 180),
            (self.character_pos[0] - radius, self.character_pos[1]),
            (self.character_pos[0] + radius, self.character_pos[1]),
            1
        )

        pygame.draw.line(
            self.screen, (255, 105, 180),
            (self.character_pos[0] - radius_cos_45, self.character_pos[1] - radius_cos_45),
            (self.character_pos[0] + radius_cos_45, self.character_pos[1] + radius_cos_45),
            1
        )
        pygame.draw.line(
            self.screen, (255, 105, 180),
            (self.character_pos[0] - radius_cos_45, self.character_pos[1] + radius_cos_45),
            (self.character_pos[0] + radius_cos_45, self.character_pos[1] - radius_cos_45),
            1
        )

    @staticmethod
    def circle_rect_collision(circle_center, radius, rect_pos, rect_size):
        rect_left = rect_pos[0]
        rect_top = rect_pos[1]
        rect_right = rect_left + rect_size
        rect_bottom = rect_top + rect_size

        closest_x = max(rect_left, min(circle_center[0], rect_right))
        closest_y = max(rect_top, min(circle_center[1], rect_bottom))
        dx = circle_center[0] - closest_x
        dy = circle_center[1] - closest_y
        return dx * dx + dy * dy <= radius * radius

    def shoot(self, key):
        if self.cooldown_timer > 0:
            return

        self.cooldown_timer = 5

        dir = [0, 0]
        if key == pygame.K_a:
            dir[0] = -1
        elif key == pygame.K_d:
            dir[0] = 1
        elif key in {pygame.K_s, pygame.K_x}:  # added pygame.K_x
            dir[1] = 1
        elif key == pygame.K_w:
            dir[1] = -1
        elif key == pygame.K_e:
            dir = [1, -1]
        elif key == pygame.K_q:
            dir = [-1, -1]
        elif key == pygame.K_z:
            dir = [-1, 1]
        elif key == pygame.K_c:
            dir = [1, 1]

        if dir != [0, 0]:
            length = math.sqrt(dir[0] ** 2 + dir[1] ** 2)
            dir = [d / length for d in dir]

            radius = self.character_size // 2
            start_pos = [
                self.character_pos[0] + dir[0] * radius,
                self.character_pos[1] + dir[1] * radius,
            ]

            self.lasers.append({'pos': start_pos, 'dir': dir})

    def update_lasers(self):
        lasers_to_remove = []  # List to keep track of lasers to remove
        shapes_to_remove = []  # List to keep track of shapes to remove
        for laser in self.lasers:
            laser['pos'][0] += laser['dir'][0] * self.laser_speed
            laser['pos'][1] += laser['dir'][1] * self.laser_speed

            # If laser collides with a shape, mark both for removal
            for shape in self.shapes:
                if pygame.Rect(laser['pos'][0], laser['pos'][1], 2, 2).colliderect(shape['pos'][0], shape['pos'][1],
                                                                                   shape['size'], shape['size']):
                    lasers_to_remove.append(laser)
                    shapes_to_remove.append(shape)
                    break

            # If laser goes off the screen, mark it for removal
            if (
                    laser['pos'][0] < 0 or laser['pos'][0] > self.screen_width or
                    laser['pos'][1] < 0 or laser['pos'][1] > self.screen_height
            ):
                lasers_to_remove.append(laser)

        # Now remove all marked lasers and shapes
        for laser in lasers_to_remove:
            if laser in self.lasers:
                self.lasers.remove(laser)
        for shape in shapes_to_remove:
            if shape in self.shapes:
                self.shapes.remove(shape)

    def draw_lasers(self):
        beam_length = self.character_size // 5

        for laser in self.lasers:
            start_pos = (int(laser['pos'][0]), int(laser['pos'][1]))
            end_pos = (
                int(laser['pos'][0] + laser['dir'][0] * beam_length),
                int(laser['pos'][1] + laser['dir'][1] * beam_length),
            )

            pygame.draw.line(self.screen, (0, 255, 0), start_pos, end_pos, 2)

    def draw_timer(self):
        if self.start_time is None:
            return

        elapsed_time = pygame.time.get_ticks() - self.start_time
        hours, remainder = divmod(elapsed_time, 3600000)  # milliseconds to hours
        minutes, remainder = divmod(remainder, 60000)  # milliseconds to minutes
        seconds, milliseconds = divmod(remainder, 1000)  # milliseconds to seconds

        timer_text = f"{hours:02}:{minutes:02}:{seconds:02}:{milliseconds:03}"
        text = self.font.render(timer_text, True, (255, 255, 255))  # white text

        self.screen.blit(text, (10, 10))  # draw at top left of the screen

    def generate_shape(self):
        shape_types = ["rectangle"]  # The types of shapes
        shape_type = random.choice(shape_types)

        color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        # Excluding white(game text), green(laser), hot pink(character), black (background)
        while color in [(255, 255, 255), (0, 255, 0), (255, 105, 180), (0, 0, 0)]:
            color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

        size = random.randint(10, 50)  # Random size between 10 and 50 pixels

        # Set the speed based on the time passed and the shape multiplier
        base_speed = 1
        if self.shape_multiplier > 10:
            base_speed *= 4 / 3
        speed = random.uniform(base_speed, base_speed + self.minutes_passed * 1.5)

        edge = random.choice(['left', 'right', 'top', 'bottom'])  # Pick a random edge
        if edge == 'left':
            x, y = -size, random.randint(0, self.screen_height)
        elif edge == 'right':
            x, y = self.screen_width + size, random.randint(0, self.screen_height)
        elif edge == 'top':
            x, y = random.randint(0, self.screen_width), -size
        elif edge == 'bottom':
            x, y = random.randint(0, self.screen_width), self.screen_height + size

        # Position at center of the screen
        center = [self.screen_width / 2, self.screen_height / 2]

        # Calculate direction towards the center of the screen
        direction = [center[0] - x, center[1] - y]

        # Normalize direction to get a unit vector
        magnitude = (direction[0] ** 2 + direction[1] ** 2) ** 0.5
        direction = [direction[0] / magnitude, direction[1] / magnitude]

        return {"type": shape_type, "color": color, "size": size, "speed": speed,
                "pos": [x, y], "dir": direction}

    def update_shapes(self):
        # Trim only half a pixel from the radius so the collider nearly matches the drawn outline
        player_radius = self.character_size / 2 - 0.5

        for shape in self.shapes:
            # Move the shape
            shape["pos"][0] += shape["dir"][0] * shape["speed"]
            shape["pos"][1] += shape["dir"][1] * shape["speed"]

            # Game over if character collides with a shape
            if self.circle_rect_collision(self.character_pos, player_radius, shape['pos'], shape['size']):
                pygame.display.flip()  # Draw the current frame to the screen
                self.game_over_capture = pygame.display.get_surface().copy()  # Capture the screen
                self.game_over_screen()
                return

        # If it's time to add new shapes
        if pygame.time.get_ticks() >= self.next_shape_time:
            # Add new shapes
            for _ in range(int(1 * self.shape_multiplier)):
                self.shapes.append(self.generate_shape())

            # Increment shape_multiplier for the next generation
            self.shape_multiplier += 1

            # Reset the shape_multiplier and increase speed after 30 seconds
            if self.shape_multiplier > 10:
                self.shape_multiplier = 1
                for shape in self.shapes:
                    shape["speed"] *= 4 / 3

            # Schedule the next shape addition
            self.next_shape_time += 3 * 1000

    def draw_shapes(self):
        for shape in self.shapes:
            if shape['type'] == 'rectangle':
                pygame.draw.rect(self.screen, shape['color'],
                                 pygame.Rect(shape['pos'][0], shape['pos'][1], shape['size'], shape['size']))

    def game_over_screen(self):
        self.start_time = None
        while True:
            self.screen.blit(self.game_over_capture, (0, 0))
            pygame.draw.rect(self.screen, (255, 255, 255), self.try_again_button, 2)

            button_text = "Try Again?"
            font_size = 32
            font = pygame.font.Font(pygame.font.get_default_font(), font_size)
            text_surface = font.render(button_text, True, (255, 255, 255))
            text_rect = text_surface.get_rect()
            text_rect.center = self.try_again_button.center
            self.screen.blit(text_surface, text_rect)

            self.display_text("Game Over!", 48, self.screen_width / 2, self.screen_height / 4)

            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.try_again_button.collidepoint(event.pos):
                        self.reset_game_state(auto_start=False)
                        return

    def display_text(self, text, size, x, y, color=(255, 255, 255)):
        font = pygame.font.Font(pygame.font.get_default_font(), size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        text_rect.center = (x, y)
        self.screen.blit(text_surface, text_rect)

    def game_loop(self):
        while True:
            self.process_events()

            if self.game_started:
                self.move_character()
                self.update_lasers()
                self.update_shapes()

                self.cooldown_timer = max(0, self.cooldown_timer - 1)

                self.screen.fill((0, 0, 0))

                self.draw_character()
                self.draw_lasers()
                self.draw_shapes()
                self.draw_timer()

            else:
                self.draw_start_screen()

            pygame.display.flip()
            self.clock.tick(60)


if __name__ == "__main__":
    game = zap()
    game.game_loop()