from setup import *

'''
Since the included time module within pygame breaks the game when used within the game loop,
we use a seperate timer class, which we can add functions that activate at the end of the duration,
and configurate whether the timer repeats, or autostarts.
'''
class Timer:
    def __init__(self, duration, func = None, repeat = None, autostart = False):
        self.duration = duration
        self.start_time = 0
        self.active = False
        self.func = func
        self.repeat = repeat

        if autostart:
            self.activate()

    def __bool__(self):
        # If the timer is active--True, else False
        return self.active
    
    def activate(self):
        self.active = True
        self.start_time = pg.time.get_ticks()

    def deactivate(self):
        self.active = False
        self.start_time = 0
        if self.repeat:
            self.activate()

    def update(self):
        ''' 
        If the timer has ended, start the function, 
        check every frame if func is not zero, else deactivate.
        '''
        if pg.time.get_ticks() - self.start_time >= self.duration:
            if self.func and self.start_time != 0:
                self.func()
            self.deactivate()