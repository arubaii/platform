from setup import *

class AllSprites(pg.sprite.Group):
    def __init__(self, *sprites):
        super().__init__(*sprites)
        self.display_surface = pg.display.get_surface()
        self.offset = pg.Vector2()
    
    def draw(self, target_pos):
        '''
        Camera Operation:
        Grabs the center position of the player (passed through in the game loop), and moves the game world
        around the player, keeping the player centered. We multiply the entire operation to a negative so
        that the game world moves in the opposite direction the player is moving in to keep them centered.
        '''
        self.offset.x = -(target_pos[0] - DISPLAY_WIDTH / 2)
        self.offset.y = -(target_pos[1] - DISPLAY_HEIGHT / 2)

        ground_sprites = [sprite for sprite in self if hasattr(sprite, 'Main')]
        object_sprites = [sprite for sprite in self if not hasattr(sprite, 'Main')]
        for layer in [ground_sprites, object_sprites]:
            for sprite in sorted(layer, key = lambda sprite: sprite.rect.centery):
                self.display_surface.blit(sprite.image, sprite.rect.topleft + self.offset)
