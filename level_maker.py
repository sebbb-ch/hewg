from textbox import *

user_polling = True
playing = True

# rendering issue is fixed by 1) not clearing the on screen text array every time
# 2) taking the commands outside the function, and anything inside placing inside of a conditional

# =============================================================================
# Poll for params
# =============================================================================

tbox = Textbox(40, 20)
tbox.text_print("The five boxing wizards jump quickly.")
while user_polling :
    for event in pygame.event.get() :
        if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
            user_polling = False
        
        if event.type == KEYDOWN :
            tbox.handle_type_event(event)

    tbox.render()
    
tbox.close()

# this feels like a silly way to do this
# but i dont wanna deal with window stuff and this makes sure the canvas gets run after the textbox
from utils import *

# =============================================================================
# Main application loop
# =============================================================================
while playing:
    # Clear window
    raw_window.fill((0,0,0))

    # Turn mouse position into tile coordinates
    mouse_pos = pygame.mouse.get_pos()
    adjusted_mouse_pos = adjust_mouse_pos(mouse_pos)

    # Main event loop ---------------------------------------------------------
    for event in pygame.event.get() :
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        if event.type == KEYDOWN : 
            if event.key == K_ESCAPE :
                playing = False
            if event.key == K_g :
                # Toggle grid drawing
                g_draw_grid = not g_draw_grid
            if event.key == K_e :
                # Export the current contents of the canvas to JSON

                # Python types that map to JSON keys must be str, int, float, bool
                # or None, only need to figure out how to map to one of those types
                # https://stackoverflow.com/questions/56403013/how-to-save-the-dictionary-that-have-tuple-keys
                # ISSUE WITH TUPLE KEYS ^^
                # better: https://stackoverflow.com/questions/12337583/saving-dictionary-whose-keys-are-tuples-with-json-python/12337657#12337657 
                g_draw_grid = False
                pygame.image.save(canvas_subsurf, "export.png")
                push_dict = {str(k): v for (k,v) in canvas.items()}
                with open("map.json", "w") as outfile :
                    json.dump(push_dict, outfile)
                print("MAP EXPORTED")
        if event.type == pygame.MOUSEBUTTONDOWN :
            click_coords = pygame.mouse.get_pos()
            adj_click_coords = adjust_mouse_pos(click_coords)
            # Handle palette click event
            if click_coords[0] > canvas_width * WIN_SCALE :
                if event.button == 1:
                    # turn mouse click coords into tile array index
                    # index = (adj_click_coords[0] - 1) % 3 + 3 * adj_click_coords[1]
                    # TRY SUBTRACTING THE ENTIRE CANVAS WIDTH AND THEN CHECKING INSTEAD

                    index = adj_click_coords[0] - int(canvas_width / TILE_SIZE) + 3 * adj_click_coords[1]
                    if index < len(tile_palette) :
                        curr_brush = tile_palette[index]
                        curr_brush_value = index
                    else :
                        curr_brush = None
            # Handle canvas click event
            else :
                if event.button == 1 : 
                    g_painting = True
                if event.button == 3 :
                    g_erasing = True
        if event.type == pygame.MOUSEBUTTONUP :
            if g_painting :
                g_painting = False
                for key in canvas_buffer.keys() :
                    if canvas_buffer[key] != -1:
                        canvas[key] = canvas_buffer[key]
                canvas_buffer = {}
            elif g_erasing :
                g_erasing = False
                for key in canvas_buffer.keys() :
                    if key in canvas.keys() :
                        canvas.pop(key)

    # Rendering ---------------------------------------------------------------

    if g_painting and adjusted_mouse_pos not in canvas.keys():
        if curr_brush == None : 
            pass
        else :
            canvas_buffer[adjusted_mouse_pos] = curr_brush_value
    elif g_erasing :
        canvas_buffer[adjusted_mouse_pos] = -1


    # Draw the palette on the side 
    draw_pos = [0,0]
    for i in range(len(tile_palette)) :
        draw_pos[0] = canvas_width + (TILE_SIZE * (i % 3))
        if i % 3 == 0 and i != 0:
            draw_pos[1] += TILE_SIZE
        raw_window.blit(tile_palette[i], pygame.Rect(draw_pos, (TILE_SIZE, TILE_SIZE)))

    # Canvas logic 
    if g_draw_grid :
        # Draw grid lines
        # NOTE: we don't need to adjust for win_scale because we're drawing 
        # directly onto the raw surface, which then gets scaled
        for i in range(0, WIN_WIDTH - (TILE_SIZE * 3)) :
            if i % TILE_SIZE == 0:
                pygame.draw.line(
                    raw_window, 
                    (255, 0, 0), 
                    (i + x_offset, 0), 
                    (i + x_offset, WIN_HEIGHT)
                )
        for i in range(0, WIN_HEIGHT) :
            if i % TILE_SIZE == 0 :
                pygame.draw.line(
                    raw_window, 
                    (255, 0, 0), 
                    (0, i + y_offset), 
                    (WIN_WIDTH - (TILE_SIZE * 3), i + y_offset)
                )

        # get mouse position, normalize it to 16x16 grid, account for offset
        
        if curr_brush != None :
            raw_window.blit(curr_brush, (adjusted_mouse_pos[0] * TILE_SIZE, adjusted_mouse_pos[1] * TILE_SIZE) )
                
    # RECALL: idx of this dict is the raw tile coords, capping at (9,8)
    for idx in canvas.keys() :
        draw_coords : tuple = tuple(TILE_SIZE * x for x in idx)
        # WIN_SCALE comes later (I think)
        tile = canvas[idx]
        raw_window.blit(tile_palette[tile], draw_coords)
    

    # Draw to window
    scaled_window = pygame.transform.scale(raw_window, display_window.get_size())
    display_window.blit(scaled_window, (0,0))
    pygame.display.update()

    clock.tick(60)

pygame.quit()
sys.exit()
