Regrid
====================

This module is used to regrid variables.

Input
----------

input_vars: one CDMSVariable module, multiple CDMSVariable modules or a list of CDMSVariables attached to single CDMSVariable module

regrid_method: three regdrid methods are supported. 

bilinear
patch
conserve

use_template: indicate whether to use template or not

longitude_interval: longitude interval of the new grid. It will be used when use_template is set to False

latitude_interval: latitude interval of the new grid. It will be used when use_template is set to False

template_var: the CDMSVariable that will be used as the template. It will be used when use_template is set to True



Output
-----------

The output can be one CDMSVariable module or a list of CDMSVariables attached to single CDMSVariable module  
