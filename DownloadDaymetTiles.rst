DownloadDaymetTiles
===========================
This module is used to download tiles form Daymet Server based on user specified spatial extent and year range. Optionally, the module can also save a tile list file to hard disk if tile_list_file is specified.  

Input
----------

var_name: the variable name 
longitude_min: the miminum longitude of the spatial extent
longitude_max: the maximum longitude of the spatial extent
latitude_min: the minimum latitude of the spatial extent
latitude_max: the maximum latitude of the spatial extent
year_min: the earliest year of the year range
year_max: the latest year to the year range
output_folder: output directory:
tile_list_file:  the module can also generate a tile list file if this is specifed


Output
-----------
There is no output module. The downloaded tile(s) will be put into the output directory
