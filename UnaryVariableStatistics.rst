UnaryVariableStatistics
==========

This module is used to calculate basic statistic along different aixs.



Input
----------
input_vars: one CDMSVariable module, multiple CDMSVariable modules or a list of CDMSVariables attached to single CDMSVariable module

statistics: the supported statistics include: mean, sum, std, variance, max, min.

list_of_summary_axis: the format should be: [axis index 1, axis index 2, ...]. For example [0, 1] means you want to caclulate statistics along the first and the second axis. 


Output
-----------

The output can be one CDMSVariable module or a list of CDMSVariables attached to single CDMSVariable module 
