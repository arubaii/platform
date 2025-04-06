import pygame as pg
import os
from os.path import join


# Global variables
DEBUG = False
FPS = 120
FPS_TOGGLE = True
TILE_SIZE = 64
DISPLAY_WIDTH, DISPLAY_HEIGHT = 1280, 720
BACKGROUND_COLOR = "#fcdfcd"
BASE_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def initialize():
    pg.init()
    pg.mixer.init()

    display = pg.display.set_mode((DISPLAY_WIDTH, DISPLAY_HEIGHT), flags=pg.SCALED, vsync=1)
    pg.display.set_caption("Platform")
    
    return display