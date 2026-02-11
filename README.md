DESIGN

Goals:
- Allow users to load in a canvas with tiles of a fixed size (8x8 or 16x16)
    - The canvas must be displayed cleanly in the sidebar for n-many tiles
    - Each tile in the canvas will be given a number that should be known at load in. This number will be assigned to that tile at export
- Allow users to select a tile (OR TILES) from the canvas as a brush
    - Extra credit: allow users to create their own brush in a separate canvas
- Allow users to erase parts of the canvas that have already been drawn to
- Allow users to export what is drawn on the canvas as a json file
    - Keys of this file will be the coordinates and values will be the tile number

NOTES

- Exports a dict with coordinates as keys (as strings) and tile "value" as values
    - This means that when reading in the json, you need to convert those string keys into actual int tuples (most likely using literal_eval)
- The tile palette is in a directory with the tiles named in the numerical order you want them to appear on the palette

BUGS
- When you export with the grid on, the screenshot will show both the mouse brush and the grid. No bueno.

TODOS
- move the grid around so you can edit something more than just the one screen
    - the top left and bottom right corners will delineate the size of the map in this case
- load in a map from json and be able to make edits
- click and drag to place multiple tiles of a certain brush
- custom brushes (i.e. more than just the one tile at a time)
