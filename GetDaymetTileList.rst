GetDaymetTileList
=================
This module is used to get tile list form Daymet Server based on user specified spatial extent and year. Optionally, the module can also save the list to hard disk if tile_list_file is specified.  


Input
----------

var_name: the variable name 
longitude_min: the miminum longitude of the spatial extent
longitude_max: the maximum longitude of the spatial extent
latitude_min: the minimum latitude of the spatial extent
latitude_max: the maximum latitude of the spatial extent
year: the year
tile_list_file:  the module can also generate a tile list file if this is specifed


Output
-----------
The output is a tile list file.
