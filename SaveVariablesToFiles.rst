SaveVariablesToFiles
====================

This module is used to save multiple CDMSVariables into NetCDF files. 


Input
----------

input_vars: one CDMSVariable module, multiple CDMSVariable modules or a list of CDMSVariables attached to single CDMSVariable module

file_names: a list of file file names. The list should have the following format:

  [path to netCDF file 1, path to NetCDF file 2, path to NetCDF file 3, ......]

The number of files in the list should match the number of CDMSVaraiables.


Output
-----------

There is no output module. The NetCDF files will be written to hard disk. 
