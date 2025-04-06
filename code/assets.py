import pygame as pg
import os
from os.path import join 
from pytmx.util_pygame import load_pygame
from setup import TILE_SIZE, BASE_PATH

'''All of the asset management is handeled in this file'''

pg.init()
pg.mixer.init()



# Images ----------------------------------------------------------

IMAGE_PATHS = {
    "bee"       : [(join(BASE_PATH, 'images', 'enemies', 'bee', f"{image}.png")) for image in range (2)],
    "worm"      : [(join(BASE_PATH, 'images', 'enemies', 'worm', f"{image}.png")) for image in range (2)],
    "bullet"    : pg.image.load(join(BASE_PATH, 'images', 'gun', 'bullet.png')),
    "fire"      : pg.image.load(join(BASE_PATH, 'images', 'gun', 'fire.png')),
    "player"    : [(join(BASE_PATH, 'images', 'player', f"{image}.png")) for image in range (3)],
    "map"       : (join(BASE_PATH, 'data', 'maps', 'world.tmx'))
}


# Audio -----------------------------------------------------------

AUDIO_PATHS = {
    "shoot_sound"   : pg.mixer.Sound(join(BASE_PATH,'audio', 'shoot.wav')),
    "impact_sound"  : pg.mixer.Sound(join(BASE_PATH,'audio', 'impact.ogg')),
    "music"         : pg.mixer.Sound(join(BASE_PATH,'audio', 'music.wav')),   
}


def load_assets(Game):
    # Load player 
    Game.player_frames = [pg.image.load(path).convert_alpha() for path in IMAGE_PATHS['player']]
    # Load enemies
    Game.bee_frames = [pg.image.load(path).convert_alpha() for path in IMAGE_PATHS['bee']]
    Game.worm_frames = [pg.image.load(path).convert_alpha() for path in IMAGE_PATHS['worm']]
    
    # Load audio
    Game.music = AUDIO_PATHS['music']
    Game.impact_sound = AUDIO_PATHS['impact_sound']
    Game.shoot_sound = AUDIO_PATHS['shoot_sound']

    # Load map
    Game.map = load_pygame(IMAGE_PATHS['map'])
    Game.map_width = Game.map.width * TILE_SIZE
    Game.map_height = Game.map.height * TILE_SIZE
    # Load weapon
    Game.bullet_png = IMAGE_PATHS['bullet']
    Game.fire_png =  IMAGE_PATHS['fire']
    pg.display.set_icon(Game.player_frames[1])        
    return entity(Game)

def entity(Game) -> tuple:
    for entity in Game.map.get_layer_by_name('Entities'):
        # Grabs the starting position of the player entity in the tile map
        if entity.name == 'Player':
            player_start_pos = (entity.x, entity.y)
        elif entity.name == 'Worm':
            Game.worm_spawn_positions.append((entity.x, entity.y))
        # Bee spawn positions will be random

    return player_start_pos

def shoot_bullet_sound():
    shoot_sound = AUDIO_PATHS['shoot_sound']
    shoot_sound.play()
    shoot_sound.set_volume(0.3)

def impact_sound():
    impact_sound = AUDIO_PATHS['impact_sound']
    impact_sound.play()
    impact_sound.set_volume(0.3)

def music(self):
    self.music.play(loops = -1)
    self.music.set_volume(0.2)

