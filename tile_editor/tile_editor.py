""" Tile editor and map maker

Tool to load in a palette of tiles and export a map of those tiles as JSON

TODO: Load in an existing map to edit
TODO: Allow users to create custom brushes
TODO: Integrate with textbox

Gameboy resolution is 160 x 144 with 16 x 16 tiles - testing with this

Notes: 
    - To handle mouse events, we need to keep track of two (three?) coordinates:
        - The canvas tile coordinates. If we are going by GameBoy aspect ratio,
            this would be tuples in range of (0,0) to (10,9)
        - The window true coordinates. This could be any tuple in range (0,0) to 
            (WINDOW_WIDTH_TRUE, WINDOW_HEIGHT_TRUE)
        - The window scaled coordinates. Basically the same as window true but in 
            range (WINDOW_WIDTH_TRUE * WIN_SCALE, WDINOW_HEIGHT_TRUE * WIN_SCALE)
"""

# External imports
import ast, sys, json

# Internal imports
from .tile_utils import *

def main() :
    playing = True

    # tile_size_px        = int(input("Individual tile size (px): "))
    # CANVAS_WIDTH_T      = int(input("Canvas width (tiles): "))
    # CANVAS_HEIGHT_T     = int(input("Canvas height (tiles): "))

    # TODO Temporary hardcodes to gameboy aspect ratio for debug
    tile_size_px        = 16
    CANVAS_WIDTH_T      = 10 
    CANVAS_HEIGHT_T     = 9

    # TODO Hard code palette to width 3 for now
    palette_width_true  = tile_size_px * 3
    WIN_SCALE           = 3 if tile_size_px == 16 else 4

    # Define window parameters based on inputs
    WINDOW_WIDTH_TRUE   = (CANVAS_WIDTH_T * tile_size_px) + palette_width_true
    WINDOW_HEIGHT_TRUE  = CANVAS_HEIGHT_T * tile_size_px

    # Define pygame rendering surfaces
    DISPLAY_WINDOW      = pygame.display.set_mode(
                            (WINDOW_WIDTH_TRUE * WIN_SCALE, WINDOW_HEIGHT_TRUE * WIN_SCALE),
                            0, 32
                        )
    RAW_WINDOW_SURFACE  = pygame.Surface((WINDOW_WIDTH_TRUE, WINDOW_HEIGHT_TRUE))
    canvas_rect         = pygame.Rect(
                                    0,0, 
                                    CANVAS_WIDTH_T * tile_size_px * WIN_SCALE, 
                                    WINDOW_HEIGHT_TRUE * WIN_SCALE
                                )

    # Misc.
    CANVAS_PALETTE_SPACE_PX = 3

    # Load in palette
    # TODO Make this configurable and make sense
    TILE_PALETTE        = load_dir('./tile_editor/assets/tiles-16')
    ERASER_SPRITE       = load_image('./tile_editor/assets/eraser.png')

    class App : 
        """ Manager class to hold mouse state and their associated buffers

        Attributes:
            brush (Surface)     : the currently selected tile from the palette (None if not drawing)
            brush_index (int)   : index of brush selected - used for the json in canvas
            is_erasing (bool)   : flag to toggle drawing behavior
            is_erasing (bool)   : flag to toggle erasing behavior
            show_grid (bool)    : flag to toggle helper grid
            draw_buffer (Set)   : set of (coordinate, tile surface) tuples that are 
                                    in the process of being drawn
            canvas (list)       : json dict of (coordinate, tile surface) tuples that have  
                                    been drawn
        """
        def __init__(self) :
            self.brush          = None 
            self.brush_index    = -1
            self.is_painting    = False
            self.is_erasing     = False
            self.show_grid      = False 

            self.draw_buffer    = set()
            self.canvas         = {}
            

    app = App()

    # =============================================================================
    # Main application loop
    # =============================================================================
    while playing:
        # Clear window
        RAW_WINDOW_SURFACE.fill((0,0,0))

        tile_mouse_coords = window_scaled_to_canvas_tile(
                                pygame.mouse.get_pos(),
                                tile_size_px * WIN_SCALE
                            )
        mouse_on_palette = tile_mouse_coords[0] + 1 > CANVAS_WIDTH_T
        # -------------------------------------------------------------------------
        # Main event loop 
        # -------------------------------------------------------------------------
        for event in pygame.event.get() :
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN : 
                if event.key == pygame.K_ESCAPE :
                    playing = False
                if event.key == pygame.K_g :
                    # Toggle grid drawing
                    app.show_grid = not app.show_grid
                if event.key == pygame.K_e :
                    # Export the current contents of the canvas to JSON
                    app.show_grid = False
                    with open('./tile_editor/export.json', "w") as f:
                        json.dump(app.canvas, f, indent=4, sort_keys=True)

                    print('Map exported')

            # Handle mouse clicks
            if event.type == pygame.MOUSEBUTTONDOWN :
                # Left click
                if event.button == 1 :
                    # Handle palette click event
                    if mouse_on_palette : 
                        # Turn mouse click coords into palette index
                        # NOTE: we are relying on the assumption that the palette is 3 tiles wide
                        palette_index = (tile_mouse_coords[1] * 3) + ((tile_mouse_coords[0] - CANVAS_WIDTH_T) % 3)
                        if palette_index >= len(TILE_PALETTE) : 
                            app.brush       = None
                        else : 
                            # Tile select
                            app.brush       = TILE_PALETTE[palette_index] 
                            app.brush_index = palette_index

                    # Handle canvas click event
                    else : 
                        app.is_painting = True

                # Right click
                elif event.button == 3 :
                    app.brush       = ERASER_SPRITE
                    app.is_erasing  = True

            # Handle mouse releases
            if event.type == pygame.MOUSEBUTTONUP :
                if app.is_erasing :
                    app.brush = TILE_PALETTE[app.brush_index]

                app.is_painting = False
                app.is_erasing  = False

        # -------------------------------------------------------------------------
        # Handle app states
        # -------------------------------------------------------------------------

        canvas_key = str(tile_mouse_coords)

        if app.is_painting and app.brush != None :
            app.canvas[canvas_key] = app.brush_index
        elif app.is_erasing and (canvas_key in app.canvas.keys()) :
            del(app.canvas[canvas_key])

        # -------------------------------------------------------------------------
        # Rendering
        # -------------------------------------------------------------------------

        # Draw the palette on the side 
        draw_pos = [0,0]
        canvas_width = CANVAS_WIDTH_T * tile_size_px 
        for i in range(len(TILE_PALETTE)) :
            tile_to_draw = TILE_PALETTE[i]
            draw_pos[0] = canvas_width + (tile_size_px * (i % 3))

            if i % 3 == 0 and i != 0:
                draw_pos[1] += tile_size_px 

            RAW_WINDOW_SURFACE.blit(
                tile_to_draw, 
                pygame.Rect(draw_pos, (tile_size_px, tile_size_px))
            )

        # Draw the grid if toggled
        if app.show_grid :
            # Draw vertical lines
            for i in range(CANVAS_WIDTH_T) :
                pygame.draw.line(
                    RAW_WINDOW_SURFACE,                     # Surface
                    (255, 0, 0),                            # Color
                    (tile_size_px * i, 0),                  # Starting position
                    (tile_size_px * i, WINDOW_HEIGHT_TRUE), # Ending position
                    1,                                      # Width
                )
            
            # Draw horizontal lines
            for i in range(CANVAS_HEIGHT_T) :
                pygame.draw.line(
                    RAW_WINDOW_SURFACE,                     # Surface
                    (255, 0, 0),                            # Color
                    (0, tile_size_px * i),                  # Starting position
                    (WINDOW_WIDTH_TRUE - palette_width_true, tile_size_px * i),  # Ending position
                    1,                                      # Width
                )

        # Draw canvas contents
        for key in app.canvas.keys() :
            coords          = ast.literal_eval(key)
            palette_index   = app.canvas[key]
            RAW_WINDOW_SURFACE.blit(
                TILE_PALETTE[palette_index],
                pygame.Rect(coords[0] * tile_size_px, coords[1] * tile_size_px, tile_size_px, tile_size_px)
                )

        # Draw the current brush at mouse position
        if (app.brush != None and not mouse_on_palette) :
            RAW_WINDOW_SURFACE.blit(
                app.brush,
                pygame.Rect(tile_mouse_coords[0] * tile_size_px, tile_mouse_coords[1] * tile_size_px, tile_size_px, tile_size_px)
                )

        # Draw to window
        scaled_window = pygame.transform.scale(RAW_WINDOW_SURFACE, DISPLAY_WINDOW.get_size())
        DISPLAY_WINDOW.blit(scaled_window, (0,0)) 
        pygame.display.update()

        clock.tick(60)

    pygame.quit()
    sys.exit()
