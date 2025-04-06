import pygame as pg
from assets import *
from os.path import join

'''Text should always be a string type'''
def font(font_size):
    return pg.font.Font(font_path, size=font_size)

def fps_counter(display, clock, FPS_TOGGLE):
    if FPS_TOGGLE:
        fps = str(int(clock.get_fps()))
        fps_t = font(18).render(fps, antialias=True, color='red')
        display.blit(fps_t,(2,2)) 

def kill_text(display, kill_count):
    kill_t = font(35).render(f" KILL COUNT: {str(kill_count)}", antialias=True, color='red')
    text_width = kill_t.get_width()
    x_position = 1278 - text_width  
    display.blit(kill_t, (x_position, 2))

def player_position_text(display, player_rectx, player_recty):
    kill_t = font(35).render(f" Position: ({str(int(player_rectx))},{str(int(player_recty))})", antialias=True, color='red')
    text_width = kill_t.get_width()
    x_position = 1278 - text_width  
    display.blit(kill_t, (x_position, 2))


font_path = join(BASE_PATH,'data', 'Oxanium-Bold.ttf')