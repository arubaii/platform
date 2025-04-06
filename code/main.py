from setup import *
from settings import *
from assets import * 
from sprites import *
from groups import AllSprites
from timerclass import Timer
from random import randint

class Game:
    def __init__(self):
        # Initialization 
        self.display = initialize() 
        self.clock = pg.Clock()
        self.running = True

        # Groups
        self.all_sprites = AllSprites()
        self.enemy_sprites = pg.sprite.Group()
        self.collision_sprites = pg.sprite.Group()
        self.bullet_sprites = pg.sprite.Group()

        # Spawn loading
        self.worm_spawn_positions = []
        self.bee_spawn_positions = []
        self.player_start_pos = load_assets(self)
        
        # Timers
        self.bees = True
        if self.bees:
            self.bee_timer = Timer(200, func=self.create_bee, repeat=True, autostart=True)
            self.bee_timer.activate()
        self.setup()

        # Class instances
        self.player = Player(self.player_frames, self.player_start_pos, self.clock, self.create_bullet, 
                             self.collision_sprites, self.all_sprites)

        for pos, area in zip(self.worm_spawn_positions, self.worm_spawn_area):
                self.worm = Worm(self.worm_frames, pos, area,
                                self.collision_sprites, self.enemy_sprites, self.all_sprites)


    def create_bee(self):
        self.bee = Bee(frames=self.bee_frames,
                       pos=((self.map_width + DISPLAY_WIDTH), randint(100,self.map_height)),
                       speed=randint(300,500), 
                       groups=(self.all_sprites, self.enemy_sprites))
        
    def create_bullet(self, pos, direction):
        x = pos[0] + direction * 34 if direction == 1 else pos[0] + direction * 34 - self.bullet_png.get_width()
        self.bullet = Bullet(self.bullet_png, (x, pos[1]), direction, 
                             (self.all_sprites, self.bullet_sprites))
        
        Fire(self.fire_png, pos, self.player, self.all_sprites)

    def collision(self):
        for bullet in self.bullet_sprites:
            sprite_collsion = pg.sprite.spritecollide(bullet, self.enemy_sprites, False, pg.sprite.collide_mask)
            if sprite_collsion:
                bullet.kill()
                impact_sound()
                for sprite in sprite_collsion:
                    sprite.destroy()

            # If the player collides with an enemy, game ends
            if pg.sprite.spritecollide(self.player, self.enemy_sprites, False, pg.sprite.collide_mask):
                if not DEBUG:
                    self.running = True

    def setup(self):
        ground(self)
        objects(self)
        collision(self)
        if not DEBUG:
            music(self)


    def run(self):
        while self.running:
            dt = self.clock.tick(FPS) / 1000 

            for event in pg.event.get():
                if event.type == pg.QUIT: 
                    self.running = False 
                elif event.type == pg.KEYDOWN:
                    if event.key == pg.K_ESCAPE:
                        self.running = False
            # Player jumps off the map
            if self.player.rect.y > 2200:
                self.running = False
            
            # update
            if self.bees:
                self.bee_timer.update()
            self.all_sprites.update(dt)

            self.collision()
            # draw 
            self.display.fill(BACKGROUND_COLOR)
            self.all_sprites.draw(self.player.rect.center)


            fps_counter(self.display, self.clock, FPS_TOGGLE)   
            if DEBUG:
                player_position_text(self.display, self.player.rect.x, self.player.rect.y)        
            pg.display.flip()
        
        pg.quit()

if __name__ == '__main__':
    game = Game()
    game.run()
    