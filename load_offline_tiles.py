# Скопировано с https://github.com/TomSchimansky/TkinterMapView/blob/main/examples/load_offline_tiles.py

import tkintermapview
import os


# This scripts creates a database with offline tiles.

# Петрозаводск (61.8365125, 34.1999899) - (61.7475835, 34.4787680)
top_left_position = (61.8365125, 34.1999899)
bottom_right_position = (61.7475835, 34.4787680)
zoom_min = 13
zoom_max = 20

# specify path and name of the database
script_directory = os.path.dirname(os.path.abspath(__file__))
database_path = os.path.join(script_directory, "offline_tiles.db")

# create OfflineLoader instance
loader = tkintermapview.OfflineLoader(path=database_path,
                                      tile_server="https://mt0.google.com/vt/lyrs=s&hl=en&x={x}&y={y}&z={z}&s=Ga")

# save the tiles to the database, an existing database will extended
loader.save_offline_tiles(top_left_position, bottom_right_position, zoom_min, zoom_max)

# You can call save_offline_tiles() multiple times and load multiple regions into the database.
# You can also pass a tile_server argument to the OfflineLoader and specify the server to use.
# This server needs to be then also set for the TkinterMapView when the database is used.
# You can load tiles of multiple servers in the database. Which one then will be used depends on
# which server is specified for the TkinterMapView.

# print all regions that were loaded in the database
loader.print_loaded_sections()
