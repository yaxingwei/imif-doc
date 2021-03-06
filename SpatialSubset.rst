SpatialSubset
====================

This module is used to extract a spatial subset (e.g. a region) of a variable based on a mask variable


Input
----------

input_vars: one CDMSVariable module, multiple CDMSVariable modules or a list of CDMSVariables attached to single CDMSVariable module

mask_var: the CDMSVariable that will be used as the mask. This CDMSVariable should have one or multiple layers (indexed by the first axis) corresponding to different mask regions (e.g. eco-regions).

mask_value: the mask value. The location with this value will be masked out.

mask_index: the index of the mask layer in mask_var. If no mask_index is provided, the first layer in mask_var will be used. 



Output
-----------

The output can be one CDMSVariable module or a list of CDMSVariables attached to single CDMSVariable module  

