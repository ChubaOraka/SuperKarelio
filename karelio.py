import math
from graphics import Canvas
import time
import random

CANVAS_WIDTH = 500
CANVAS_HEIGHT = 400
SIZE = 40

next_level = False

# if you make this larger, the game will go slower
DELAY = 0.1
AIR = 0
WORLD = []
canvas = Canvas(CANVAS_WIDTH, CANVAS_HEIGHT)

class levelsurface:
    def __init__(self):
        GROUND_LEVEL = 250
        WORLD.clear()
        canvas.clear()
        for row in range(0, CANVAS_HEIGHT, SIZE):
            cell = []
            for col in range(0, CANVAS_WIDTH, SIZE):
                cell.append(bricks(col, row, 1).id) if row >= GROUND_LEVEL else cell.append(0)
            WORLD.append(cell)
    
class nextlevel:
    def __init__(self):
        GROUND_LEVEL = random.randint(250, CANVAS_HEIGHT - SIZE)
        WORLD.clear()
        canvas.clear()
        for row in range(0, CANVAS_HEIGHT, SIZE):
            cell = []
            for col in range(0, CANVAS_WIDTH, SIZE):
                cell.append(bricks(col, row, 1).id) if row >= GROUND_LEVEL else cell.append(0)
            WORLD.append(cell)

class bricks:
    def __init__(self, x, y, type):
        self.id = canvas.create_image_with_size(x, y, SIZE, SIZE, f'brick{type}.png')

class current_score:
    def __init__(self, score=0):
        self.curr_score = score
        self.id = canvas.create_text(5, 5, self.__str__())
    def __str__(self, score=0):
        return f"Score: {score}"
    def incrementby(self, points):
        self.curr_score += points
        self.update(self.curr_score)
    def update(self, score):
        canvas.change_text(self.id, self.__str__(score))

class karelio:
    velocity_x = 0
    velocity_y = 0
    gravity = 10
    elapsed_time = 0
    def __init__(self, x, y, running_score):
        self.x = x
        self.y = y
        self.get_next_x = lambda : self.round_to_the_nearest(self.x - 1 , SIZE) + SIZE
        self.id = canvas.create_image_with_size(x, y, SIZE, SIZE, 'karel192.png')
        self.walking = False
        self.jumping = False
        self.bouncing = False
        self.bounces = 0
        self.running_score = running_score
    def round_to_the_nearest(self, number, digit):
        return round(number / digit) * digit
    def update(self):
        dx = 0
        dy = 0
        if self.karel_is_in_the_air():
            self.elapsed_time += DELAY
            dy += self.gravity * 2 * self.elapsed_time
        else:
            self.elapsed_time = 0
        if self.walking:
            dx = self.accelerate()
            if self.karel_is_on_solid_surface():
                dy -= 2
        else:
            dx = self.decelerate()
        if self.jumping:
            self.jump()
            dy -= self.velocity_y
        else:
            self.velocity_y = 0
        if math.floor((self.x + dx) // SIZE) + 1 >= len(WORLD[0]):
            canvas.moveto(self.id, self.x + dx, self.y + dy)
            self.running_score.incrementby(2)
            self.karel_is_successful()
        else:
            # Collision detection and snapping to edge
            if WORLD[math.floor((self.y) // SIZE)][math.floor((self.x + dx) // SIZE) + 1] != AIR:
                dx = 0
                self.x = self.round_to_the_nearest(self.x + SIZE/2 + dx, SIZE)
                self.jumping = False
            if WORLD[math.floor((self.y + dy) // SIZE) + 1][math.floor(self.x // SIZE)] != AIR:
                dy = 0
                self.y = self.round_to_the_nearest(self.y + SIZE/2 + dy, SIZE)
                self.jumping = False
            print(f"dx: {dx} \ndy: {dy}")
            canvas.moveto(self.id, self.x + dx, self.y + dy)
            self.x = canvas.get_left_x(self.id)
            self.y = canvas.get_top_y(self.id)
    def karel_is_in_the_air(self):
        print(f"Cell karel is stepping on: {WORLD[math.floor(self.y // SIZE) + 1][math.floor(self.x // SIZE)]}")
        return WORLD[math.floor(self.y // SIZE) + 1][math.floor(self.x // SIZE)] == AIR
    def karel_is_on_solid_surface(self):
        return not self.karel_is_in_the_air()
    def karel_front_is_clear(self):
        return WORLD[math.floor(self.y // SIZE)][math.floor(self.x // SIZE) + 1] == AIR
    def karel_has_headroom(self):
        return WORLD[math.floor(self.y // SIZE) - 1][math.floor(self.x // SIZE)] == AIR
    def jump(self):
        if self.jumping == False:
            if self.karel_is_on_solid_surface() and self.karel_has_headroom():
                self.velocity_y = 20
            self.jumping = True
    def bounce(self):
        if self.bouncing == False:
            if self.karel_is_on_solid_surface() and self.karel_has_headroom():
                self.velocity_y = 2
            self.bouncing = True
    def accelerate(self):
        if self.karel_is_on_solid_surface() and self.karel_front_is_clear():
            self.velocity_x += 2
        return self.velocity_x
    def decelerate(self):
        if self.karel_front_is_clear() and self.velocity_x > 0:
            if self.karel_is_in_the_air():
                self.velocity_x -= 0.002
            elif self.velocity_x > 4:
                self.velocity_x -= 4
            elif self.velocity_x > 2:
                self.velocity_x -= 2
            else:
                self.velocity_x = 0
        return self.velocity_x
    def karel_is_successful(self):
        global next_level
        next_level = True
    
def main():
    global next_level
    levelsurface()
    curr_score = current_score()
    karel = karelio(0, 0, curr_score)
    next_karel_x = karel.get_next_x()
    while True:
        karel.update()
        keys = canvas.get_new_key_presses()
        if 'ArrowUp' in keys:
            karel.jump()
        if 'ArrowRight' in keys:
            if karel.x != next_karel_x:
                karel.walking = True
        if 'ArrowRight' not in keys and karel.x >= next_karel_x:
            karel.walking = False
            next_karel_x = karel.get_next_x()
        if next_level:
            nextlevel()
            curr_score = current_score(curr_score.curr_score)
            karel = karelio(0, 0, curr_score)
            next_level = False
        time.sleep(DELAY)
    
if __name__ == '__main__':
    main()
