from setup import DISPLAY_WIDTH, DISPLAY_HEIGHT, DEBUG, TILE_SIZE
from settings import *
from assets import *
from timerclass import Timer
from math import sin
from random import randint

# Sprite properties _________________________________________________________________________________________________________________________________________________________________

class Sprite(pg.sprite.Sprite):
    def __init__(self, surf, pos: tuple, *groups):
        super().__init__(*groups)
        self.image = surf
        self.rect = self.image.get_frect(topleft = pos)
        self.ground = True



class CollisionSprite(pg.sprite.Sprite):
    def __init__(self, pos: tuple, surf, groups):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_frect(topleft = pos)



class TransparentSprite(pg.sprite.Sprite):
    def __init__(self, pos: tuple, length: float, width: float, *groups, RGB: tuple, debug):
        super().__init__(*groups)
        self.image = pg.Surface((length, width), pg.SRCALPHA)
        # Transparent fill for debugging, otherwise set alpha to 0
        self.debug = debug
        if self.debug:
            self.image.fill((RGB))
            self.image.set_alpha(100) 
        self.rect = self.image.get_frect(topleft = pos)



class AnimatedSprite(Sprite):
    def __init__(self, frames: list , pos: tuple, *groups):
        self.frames, self.frame_index, self.animation_speed = frames, 0, 0
        super().__init__(self.frames[self.frame_index], pos, *groups)

    def animate(self, dt):
        self.frame_index += self.animation_speed * dt
        self.image = self.frames[int(self.frame_index) % len(self.frames)]
        self.image = pg.transform.flip(self.image, self.flip, False)

# Sprite Classes __________________________________________________________________________________________________________________________________


class Bullet(Sprite):
    def __init__(self, surf, pos, direction, *groups):
        super().__init__(surf, pos, *groups)

        # Movement attributes
        self.bullet_dir = direction
        self.bullet_speed = 1200

    def update(self,dt):
        self.rect.x += self.bullet_dir * self.bullet_speed * dt



class Fire(Sprite):
    def __init__(self, surf, pos, player, *groups):
        super().__init__(surf, pos, *groups)
        self.player = player
        self.flip = player.flip
        self.timer = Timer(100, autostart = True, func=self.kill)
        # Properly fit the animation to the barrel
        self.offset_y = pg.Vector2(0,9)

        if self.player.flip:
            self.rect.midright = self.player.rect.midleft + self.offset_y
            self.image = pg.transform.flip(self.image, True, False)
        else:
            self.rect.midleft = self.player.rect.midright + self.offset_y

    def update(self, _):
        self.timer.update()

        if self.player.flip:
            self.rect.midright = self.player.rect.midleft + self.offset_y
        else:
            self.rect.midleft = self.player.rect.midright + self.offset_y
        
        if self.flip != self.player.flip:
            self.kill()



'''Handles all the controls and movement logic for the player'''
class Player(AnimatedSprite):
    def __init__(self, frames, pos, clock, create_bullet, collision_sprites, *groups):
        super().__init__(frames, pos, *groups)

        # Animation/rect attributes
        self.create_bullet = create_bullet
        self.flip = False
        self.player_start_pos = pos
        self.animation_speed = 10
        self.rect_hitbox = self.rect.inflate(-20,0)      

        # Movement attributes
        self.player_dir = pg.Vector2()
        self.player_speed = 400
        self.player_gravity = 100    
        self.jump_velocity_PPS = 1020   # Pixels per second
        self.jump_velocity_PPF = 0      # Pixels per frame

        # Jump attributes
        self.jump_timer = 0            
        self.max_jump_time = 24    
        self.max_jump_height = 250
        self.jumping = False
        self.jump_pressed = False
        self.on_floor = True;

        self.max_hangtime = 0.15
        self.hangtime_timer = 0
        self.in_hangtime = False;

        self.collision_sprites = collision_sprites
        self.jump_start = self.rect.copy()

        self.clock = clock

        # Timer
        self.shoot_timer = Timer(500)
        

    def input(self):
        self.keys = pg.key.get_pressed()
        # Movement vector
        self.player_dir.x = int(self.keys[pg.K_d]) - int(self.keys[pg.K_a]) # Both return boolean values
        # Jump 
        if self.keys[pg.K_SPACE]:
            if self.on_floor and not self.jump_pressed:
                self.jumping = True
                self.jump_timer = 0
                self.player_dir.y = 0
                self.jump_pressed = True
        else:
            self.jump_pressed = False  # Allow jump trigger again when space is released
            self.jumping = False      
            self.player_velocity = 450
        
        self.mouse = pg.mouse.get_just_pressed()
        if (self.mouse[0] or self.keys[pg.K_LEFT] or self.keys[pg.K_RIGHT]) and not self.shoot_timer:
            shoot_bullet_sound()
            self.create_bullet(self.rect.center, -1 if self.flip else 1)
            self.shoot_timer.activate()


    def movement(self, dt, clock):
        '''
        We divide 1020 by the current FPS to find px/frame. 1020 is a good px/s rate for the jump velocity. 
        Thus, dividing by the FPS, we get some px/frame rate that makes the velocity consistent
        over all frame rates.
        '''

        # Displacement storage
        if self.jumping and self.jump_timer == 0:
            self.jump_start_y = self.rect.centery  # store Y when jump starts


        if self.jumping:
            # Frame independence logic
            self.jump_velocity_PPF  = self.jump_velocity_PPS / self.clock.get_fps()
            self.player_dir.y -= self.jump_velocity_PPF 
        
            jump_displacement = self.jump_start_y - self.rect.centery
            self.jump_timer += dt 
            if DEBUG:
                self.jump_frames = round(self.jump_timer / dt)   
                print(f"Jump Y velocity (px/frame) : {round(self.player_dir.y)}")
                print(f"Jump duration              : {round(self.jump_timer, 2)}s")
                print(f"Jump Frames (total)        : {self.jump_frames}")
                print(f"Jump Height (pixels)       : {round(jump_displacement)}\n")

            if jump_displacement >= self.max_jump_height:
                self.jumping = False
                self.player_velocity = 0
                self.in_hangtime = True 
                self.hangtime_timer = 0
        # We introduce some hangtime when if the player maxes out their jump
        elif self.in_hangtime:
            self.hangtime_timer += dt
            if self.hangtime_timer >= self.max_hangtime:
                self.in_hangtime = False
        else:
            self.jumping = False
            self.player_velocity = 0
            self.in_hangtime = False


        # Horizontal movement and collision
        self.rect_hitbox.x += self.player_dir.x * self.player_speed * dt
        self.collision('horizontal')

        # Apply gravity
        if not self.in_hangtime:
            self.player_dir.y += self.player_gravity * 4 * dt
            self.rect_hitbox.y += self.player_dir.y
            self.collision('vertical')

        self.rect.center = self.rect_hitbox.center

    def collision(self, direction):
        '''Handles all of object collision logic'''

        # Iterate over all collision sprites each frame to check for collisions
        for sprite in self.collision_sprites:
            # Returns True if any part of the two rects overlap (player and object), including edges
            # However, it does NOT determine which side the collision occurs on—only that an overlap exists
            if sprite.rect.colliderect(self.rect_hitbox):

                if direction == 'horizontal':
                     # If the player is moving right (positive velocity), snap their right side to the object's left side
                    if self.player_dir.x > 0: self.rect_hitbox.right = sprite.rect.left
                    # And vice-versa
                    if self.player_dir.x < 0: self.rect_hitbox.left = sprite.rect.right
                if direction == 'vertical': 
                     # If the player is moving up (negative velocity), snap their top side to the object's bottom side
                    if self.player_dir.y < 0: self.rect_hitbox.top = sprite.rect.bottom
                    if self.player_dir.y > 0: self.rect_hitbox.bottom = sprite.rect.top
                    
                    self.player_dir.y = 0

    def check_floor(self):
        '''
        We create a small rect at the bottom of the player which checks for collisions with objects
        '''
        bottom_rect = self.rect_hitbox.copy()
        bottom_rect.height = 2
        bottom_rect.top = self.rect_hitbox.bottom
        # any() returns True if at least one value in an iterable is True
        self.on_floor = any(bottom_rect.colliderect(sprite.rect) for sprite in self.collision_sprites)

    def animate(self, dt):
        if self.player_dir.x:
            self.frame_index += self.animation_speed * dt
            # If the player is moving in a negaitve direction, flip the animation state
            self.flip = self.player_dir.x < 0 # Returns a boolean value
        else:
            # No animation state if the player is not moving
            self.frame_index = 0
        if not self.on_floor:
            self.frame_index = 1

        self.image = self.frames[int(self.frame_index) % len(self.frames)]
        self.image = pg.transform.flip(self.image, self.flip, False)


    def update(self, dt):
        self.shoot_timer.update()
        self.check_floor()
        self.input()
        self.movement(dt, self.clock)
        self.animate(dt)

        # Normalize the player velocity vector for diagonal movement
        if self.player_dir.length() > 0:
            self.player_dir = self.player_dir.normalize()
        


class Enemy(AnimatedSprite):
    def __init__(self, frames, pos, *groups):
        super().__init__(frames, pos, *groups)            
        self.death_timer = Timer(200, func= self.kill)
 

    def destroy(self):
        self.death_timer.activate()
        self.animation_speed = 0
        self.image = pg.mask.from_surface(self.image).to_surface()
        self.image.set_colorkey('black')

    def update(self, dt):
        self.death_timer.update()
        if not self.death_timer:
            self.movement(dt)
            self.animate(dt)
        self.constraint()



class Worm(Enemy):
    def __init__(self, frames, pos, area, collision_sprites, *groups):
            super().__init__(frames, pos, *groups)

            self.collision_sprites = collision_sprites

            # Animation states
            self.animation_speed = 6
            self.rect_hitbox = self.rect.inflate(-30, 1)
            # Enemy attributes
            self.speed = 50
            self.gravity = 5
            self.worm_dir = pg.Vector2(1,0)
            self.worm_area = area
            self.flip = self.worm_dir.x < 0


    def movement(self, dt): 
        self.rect_hitbox.x += self.speed * self.worm_dir.x * dt
        self.rect_hitbox.y += self.gravity
        self.worm_dir.y += self.gravity
        self.collision()


        self.rect.center = self.rect_hitbox.center

    def constraint(self):
        shrunk_rect = self.worm_area.rect.inflate(-40,-40)  # Fixes finicky behavior
        if not shrunk_rect.colliderect(self.rect_hitbox):
            self.worm_dir.x *= -1

    def collision(self):

        for sprite in self.collision_sprites:
                if sprite.rect.colliderect(self.rect_hitbox):

                    if self.worm_dir.y > 0: self.rect_hitbox.bottom = sprite.rect.top

    def animate(self, dt):
        self.frame_index += self.animation_speed * dt
        self.flip = self.worm_dir.x < 0
        self.image = self.frames[int(self.frame_index) % len(self.frames)]
        self.image = pg.transform.flip(self.image, self.flip, False)



class Bee(Enemy):
    def __init__(self, frames, pos, groups, speed):
        super().__init__(frames, pos, groups)
        self.flip = False
        self.speed = speed
        self.animation_speed = 8
        self.amplitude = randint(500,600)
        self.frequency = randint(300,600)

    def movement(self, dt):
        self.rect.x -= self.speed * dt
        # Bees move in a sinusodial path
        self.rect.y += sin(pg.time.get_ticks() / self.frequency) * self.amplitude * dt

    def constraint(self):
        # When the bees go way off screen
        if self.rect.right <= -1500:
            self.kill()

  

# LOADING SPRITE ASSETS ___________________________________________________________________________________________________________________________________________________________________________________________________________

def ground(self):
    for x,y, image in self.map.get_layer_by_name('Main').tiles():
        Sprite(image, (x * TILE_SIZE ,y * TILE_SIZE ), (self.all_sprites, self.collision_sprites))

def objects(self):
    for x,y, image in self.map.get_layer_by_name('Decoration').tiles():
        Sprite(image, (x * TILE_SIZE ,y * TILE_SIZE ), self.all_sprites)

def collision(self):
    self.worm_spawn_area = []
    for col in self.map.get_layer_by_name('Entities'):
        if col.name == 'Worm':
            self.worm_spawn_area.append(TransparentSprite((col.x, col.y), col.width, col.height, 
                                                self.all_sprites, RGB=(255,0,0), debug=DEBUG))
    
