from tile_editor import tile_editor 

module = input("Tell me what to run: ")

if module == "tile_editor" or str("tile editor").lower():
    tile_editor.main()

