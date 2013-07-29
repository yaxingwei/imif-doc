LongTermTemporalMean
====================

This module is used to calculate long term temporal mean based on a specified temporal granularity (temporal_granularity) . Proper temporal bounds will be set before the aggregation. 



Input
----------
input_vars: one CDMSVariable module, multiple CDMSVariable modules or a list of CDMSVariables attached to single CDMSVariable module

temporal_granularity: the supported temporal granularities include: year, season or month

The following temporal granularities are acceptable:

  year or annual 

  season or DJF, MAM, JJA, SON

  month or JAN, FEB, MAR, APR, MAY ......

Output
-----------

The output can be one CDMSVariable module or a list of CDMSVariables attached to single CDMSVariable module  


Notes
----------
The difference between LongTermTemporalMean and TemporalAggregation can be illustrated with the following example: if "month" is chosen as the temporal granularity and the input CDMSVariable has 5 years (60 months) data, TemporalAggregation will create 60 time steps while LongTermTemporalMean will only create 12. 




