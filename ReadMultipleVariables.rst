ReadMultipleVariables
=====================
This module is used to read multiple variables into memory from a variable (or tile) list file. 

Input
----------
variable_list_file: a variable list file. The list file should have the following format:

number of files
file path;variable name
file path;variable name
file path;variable name
file path;variable name
......
......


Output
-----------

The output is a list of CDMSVariables attached to single CDMSVariable module 
    



    
