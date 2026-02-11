# ========================================================
# gameboy resolution is 160 x 144 with 16 x 16 tiles
# ========================================================
import pygame, sys, random, os, math, json
clock = pygame.time.Clock()
from pygame.locals import *

BASE_PATH = './'
def load_image(path):
    img = pygame.image.load(BASE_PATH + path).convert()
    img.set_colorkey((0, 0, 0))
    return img

def load_dir(path) :
    images = []
    for img_name in sorted(os.listdir(BASE_PATH + path)):
        images.append(load_image(path + '/' + img_name))
    return images

def window_scaled_to_canvas_tile(t_raw_coordinates: tuple, t_scaled_tile_size : int) :
    """ Given raw mouse coordinates in a window, return their tile position

    Args:
        t_raw_coordinates
        t_scaled_tile_size

    Return
        Tuple of canvas coordinates
    """
    return (
        math.floor( (t_raw_coordinates[0]) / (t_scaled_tile_size) ), 
        math.floor( (t_raw_coordinates[1]) / (t_scaled_tile_size) )
    )

# TODO: take this out of the CLI
def poll_user() -> None :
    global TILE_SIZE
    global X_TILES
    global Y_TILES
    skip_y = False

    print("Welcome to your own in-house tile editor. You can use this to draw tiles on a grid of a size of your choosing, and then output that as a json file.")
    print("NOTE: CHARACTER INPUT FAILS")
    # POLL FOR TILE SIZE
    u_tile_size = input("Enter tile size: ")
    if not u_tile_size.isnumeric() :
        print("Invalid tile size - reverting to default of 16")
    elif u_tile_size == '8' or u_tile_size == '16' :
        TILE_SIZE = int(u_tile_size)
        print(TILE_SIZE)
    else : 
        print("Invalid tile size - reverting to default of 16")

    # POLL FOR X AND Y DIMENSIONS
    print("When inputting x tiles, press enter (blank/invalid) to default to a 10x9 gameboy resolution.")
    # this feels silly
    u_x_tiles = input("Enter the number of tiles in the x-axis: ")
    if not u_x_tiles.isnumeric() :
        skip_y = True
        u_x_tiles = 10
    
    X_TILES = int(u_x_tiles)

    if not skip_y :
        print("When inputting y tiles, press enter (blank/invalid) to default to a 4:3 ratio of whatever x-dimensions you inputted.")
        print("NOTE: gameboy ratio != 4:3")
        u_y_tiles = input("Enter the number of tiles in the y-axis: ")
        if not u_y_tiles.isnumeric() :
            u_y_tiles = math.floor((X_TILES * 3 ) / 4 )
            print("Defaulting to our calculated 4:3 ratio: ", X_TILES, u_y_tiles)
        
        Y_TILES = int(u_y_tiles) 
    else :
        print("Defaulting to 10 x 9 dimesions.")
        Y_TILES = 9

# poll_user()

