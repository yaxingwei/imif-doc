from PyQt4 import QtCore, QtGui

from cdatguiwrap import VCSQtManager
import vcs
import genutil
import cdutil
import cdms2
import time
import api
import re
import MV2
import os
import ast
import string
from info import identifier
from core.configuration import get_vistrails_configuration
from core.modules.module_registry import get_module_registry
from core.modules.vistrails_module import Module, ModuleError, NotCacheable
from core import debug
from core.utils import InstanceObject
from packages.spreadsheet.basic_widgets import SpreadsheetCell
from packages.spreadsheet.spreadsheet_controller import spreadsheetController
from packages.spreadsheet.spreadsheet_cell import QCellWidget, QCellToolBar
from packages.uvcdat.init import Variable, Plot
from gui.uvcdat.theme import UVCDATTheme
from gui.uvcdat.cdmsCache import CdmsCache

from packages.uvcdat_cdms.init import CDMSVariable
from regrid2 import Regridder
import math
from core.modules.basic_modules import File
import numpy as np
import sys


from matrix import Matrix
from config_reader import ConfigReader, WriteVarsIntoDataFile, ReadMatrixFromFile
from core.modules.module_registry import get_module_registry
from plots import Coordinator, Dendrogram, ParallelCoordinates, TaylorDiagram, SeriesPlot, BarChart, HeatMap
from core.bundles import py_import



def setLatLonBoundsForCurvilinear(var):

	nLat = var.getLatitude().data.shape[0]
	nLon = var.getLatitude().data.shape[1]

	lat_missing_value = var.getLatitude().missing_value
	lon_missing_value = var.getLongitude().missing_value
                
               
        if var.getLongitude().getBounds() == None:
            dataLon = var.getLongitude().data
            boundsLon = None

	    for i in range(nLat):

	        # first element 
                if math.fabs(dataLon[i][0] - lon_missing_value) < 1 or math.fabs(dataLon[i][1] - lon_missing_value) < 1:
                    left = lon_missing_value
                    right = lon_missing_value
                else:
	            left = (dataLon[i][0] - (dataLon[i][1] -dataLon[i][0])/2)
                    right = (dataLon[i][0] +dataLon[i][1])/2                      

                    if dataLon[i][0] > 90 and dataLon[i][1] < -90:
	                interval = 180 - dataLon[i][0] + dataLon[i][1] + 180
                        right = dataLon[i][0] + interval /2
                        if right > 180:
                            right = -180 + (right - 180)
                        left = dataLon[i][0] - interval/2

                    if (dataLon[i][0] - (dataLon[i][1] -dataLon[i][0])/2) < -180:
                        left = 180 - (dataLon[i][0] - (dataLon[i][1] -dataLon[i][0])/2) - (-180)
               
                row = np.array([lon_missing_value, lon_missing_value])
                

                # middle elements
	        for j in range(1, nLon-1):
                    if math.fabs(dataLon[i][j-1] - lon_missing_value) < 1 or math.fabs(dataLon[i][j] - lon_missing_value) < 1 or math.fabs(dataLon[i][j+1] - lon_missing_value) < 1:
                        left = lon_missing_value
                        right = lon_missing_value
                    else:

                        left = (dataLon[i][j-1] + dataLon[i][j])/2
                        right = (dataLon[i][j+1] + dataLon[i][j])/2

                        if dataLon[i][j-1] > 90 and dataLon[i][j] < -90:
                            interval = 180 - dataLon[i][j-1] + dataLon[i][j] + 180
                            left = dataLon[i][j-1] + interval /2
                            if left > 180:
                                left = -180 + (left - 180)

                        if dataLon[i][j] > 90 and dataLon[i][j+1] < -90:
                            interval = 180 - dataLon[i][j] + dataLon[i][j+1] + 180
                            right = dataLon[i][j] + interval /2
                            if right > 180:
                                right = -180 + (right - 180)

                    row = np.vstack((row, [left, right]))

                # last element
                if math.fabs(dataLon[i][nLon-1] - lon_missing_value) < 1 or math.fabs(dataLon[i][nLon-2] - lon_missing_value) < 1:
                    left = lon_missing_value
                    right = lon_missing_value
                else:

                    left = (dataLon[i][nLon-1] +dataLon[i][nLon-2])/2
                    right = dataLon[i][nLon-1] + (dataLon[i][nLon-1] -dataLon[i][nLon-2])/2

                    if dataLon[i][nLon-2] > 90 and dataLon[i][nLon-1] < -90:
                        interval = 180 - dataLon[i][nLon-2] + dataLon[i][nLon-1] + 180
                        right = dataLon[i][nLon-2] + interval /2
                        if right > 180:
                            right = -180 + (right - 180)
                        left = dataLon[i][nLon-1] + interval/2

                    if dataLon[i][nLon-1] + (dataLon[i][nLon-1] - dataLon[i][nLon-2])/2 > 180:
                        right = -180 + (dataLon[i][nLon-1] + (dataLon[i][nLon-1] -dataLon[i][nLon-2])/2) - 180

                row = np.vstack((row, [left, right]))



                if i == 0:
                    boundsLon = np.array([row])
                else:
                    boundsLon = np.vstack((boundsLon, [row]))


            var.getLongitude().setBounds(boundsLon.astype('f'))



        if var.getLatitude().getBounds() == None:
            dataLat = var.getLatitude().data
            boundsLat = None

            for i in range(nLat):
                if i==0: 
                    if math.fabs(dataLat[i][0] - lat_missing_value) < 1 or math.fabs(dataLat[i+1][0] - lat_missing_value) < 1:
                        row = np.array([lat_missing_value, lat_missing_value])
                    else:
                        row = np.array([(dataLat[i][0] - (dataLat[i+1][0] -dataLat[i][0])/2), (dataLat[i+1][0] + dataLat[i][0])/2])
                    for j in range(1, nLon):
                        if math.fabs(dataLat[i][j] - lat_missing_value) < 1 or math.fabs(dataLat[i+1][j] - lat_missing_value) < 1:
                            row = np.vstack((row, [lat_missing_value, lat_missing_value]))
                        else:
                            row = np.vstack((row, [(dataLat[i][j] -(dataLat[i+1][j] -dataLat[i][j])/2), (dataLat[i+1][j] + dataLat[i][j])/2]))
                    boundsLat = np.array([row])
                elif  i> 0 and i < nLat-1:
                    if math.fabs(dataLat[i-1][0] - lat_missing_value) < 1 or math.fabs(dataLat[i][0] - lat_missing_value) < 1 or math.fabs(dataLat[i+1][0] - lat_missing_value) < 1:
                        row = np.array([lat_missing_value, lat_missing_value])
                    else:
                        row = np.array([(dataLat[i-1][0] + dataLat[i][0])/2, (dataLat[i+1][0] + dataLat[i][0])/2])

                    for j in range(1, nLon):
                        if math.fabs(dataLat[i-1][j] - lat_missing_value) < 1 or math.fabs(dataLat[i][j] - lat_missing_value) < 1 or math.fabs(dataLat[i+1][j] - lat_missing_value) < 1:
                            row = np.vstack((row, [lat_missing_value, lat_missing_value]))
                        else:
                            row = np.vstack((row, [(dataLat[i-1][j] + dataLat[i][j])/2, (dataLat[i+1][j] + dataLat[i][j])/2]))
                    boundsLat = np.vstack((boundsLat, [row]))
                else:
                    if math.fabs(dataLat[i][0] - lat_missing_value) < 1 or math.fabs(dataLat[i-1][0] - lat_missing_value) < 1:
                        row = np.array([lat_missing_value, lat_missing_value])
                    else:
                        row = np.array( [(dataLat[i][0] + dataLat[i-1][0])/2, (dataLat[i][0] + (dataLat[i][0] -dataLat[i-1][0])/2)])
                    for j in range(1, nLon):
                        if math.fabs(dataLat[i][j] - lat_missing_value) < 1 or math.fabs(dataLat[i-1][j] - lat_missing_value) < 1:
                            row = np.vstack((row, [lat_missing_value, lat_missing_value]))
                        else:
                            row = np.vstack((row, [(dataLat[i][j] + dataLat[i-1][j])/2, (dataLat[i][j] + (dataLat[i][j] -dataLat[i-1][j])/2)]))
                    boundsLat = np.vstack((boundsLat, [row]))

            var.getLatitude().setBounds(boundsLat.astype('f'))





def setBoundsFor1DAxis(var, axisIndex):

    if var.getAxis(axisIndex).getBounds() != None:
        return

    nIntervals = var.getAxis(axisIndex).shape[0]
    interval = var.getAxis(axisIndex)[1] -var.getAxis(axisIndex)[0] 

    for i in range(nIntervals):
        start = var.getAxis(axisIndex)[i] - interval/2
        end = var.getAxis(axisIndex)[i] + interval/2

        if i == 0:
	    bounds = np.array([start, end])
        else:
            bounds = np.vstack((bounds, [start, end]))

    var.getAxis(axisIndex).setBounds(bounds.astype('f'))





def expand_port_specs(port_specs, pkg_identifier=None):
    if pkg_identifier is None:
        pkg_identifier = identifier
    reg = get_module_registry()
    out_specs = []
    for port_spec in port_specs:
        if len(port_spec) == 2:
            out_specs.append((port_spec[0],
                              reg.expand_port_spec_string(port_spec[1],
                                                          pkg_identifier)))
        elif len(port_spec) == 3:
            out_specs.append((port_spec[0],
                              reg.expand_port_spec_string(port_spec[1],
                                                          pkg_identifier),
                              port_spec[2])) 
    return out_specs





class GetMatrixFromVariables(Module):


    _input_ports = expand_port_specs([("input_vars", "gov.llnl.uvcdat.cdms:CDMSVariable")])

    _output_ports  = [('matrix',   Matrix)]

 
#    _output_ports = expand_port_specs([("matrix", "Matrix")])


   # _output_ports  =  expand_port_specs[('matrix',   "Matrix")]


    def compute(self):
     	if not self.hasInputFromPort('input_vars'):
            raise ModuleError(self, "'input_vars' is mandatory.")
	else:
	    vars1 = self.getInputFromPort('input_vars')
            vars2 = self.getInputListFromPort('input_vars')
            if type(vars1) is list:  # the input is a list of variables
                self.vars = vars1
            else:  # the input is multiple CDMSVariables pointing to this module
                self.vars = vars2


       # for i in range(len(self.vars)):  
            
          
        values = self.vars[0].var.data

        matrix = Matrix()
        matrix.values     = values
        #matrix.ids        = ids
        #matrix.labels     = labels
        #matrix.attributes = attributes
        
        self.setResult('matrix', matrix)
    




class TemporalAggregation(Module):

   """

TemporalAggregation
===================
This module is used to calculate temporal mean based on a specified temporal granularity (temporal_granularity) . Proper temporal bounds will be set before the aggregation.
 
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
-----------
The difference between TemporalAggregation and LongTermTemporalMean can be illustrated with the following example: if "month" is chosen as the temporal granularity and the input CDMSVariable has 5 years (60 months) data, TemporalAggregation will create 60 time steps while LongTermTemporalMean will only create 12. 


    """


    _input_ports = expand_port_specs([("input_vars", "gov.llnl.uvcdat.cdms:CDMSVariable"),
                                      ("temporal_granularity", "basic:String")])
 
    _output_ports = expand_port_specs([("output_vars", "gov.llnl.uvcdat.cdms:CDMSVariable")])


    def compute(self):
     	if not self.hasInputFromPort('input_vars'):
            raise ModuleError(self, "'input_vars' is mandatory.")
	else:
	    vars1 = self.getInputFromPort('input_vars')
            vars2 = self.getInputListFromPort('input_vars')
            if type(vars1) is list:  # the input is a list of variables
                self.vars = vars1
            else:  # the input is multiple CDMSVariables pointing to this module
                self.vars = vars2
   

        if not self.hasInputFromPort("temporal_granularity"):
            raise ModuleError(self, "'temporal_granularity' is mandatory.")
        else:
            self.temporal_granularity = self.getInputFromPort('temporal_granularity')

        self.outvars = []
        

        # add proper bounds if there are no bounds definition in the .nc file

        for i in range(len(self.vars)):  
            outvar = CDMSVariable(filename=None,name=self.vars[i].var.id)
            #outvar.var = self.vars[i].var.clone()
            
            if self.temporal_granularity.startswith("Annual") or self.temporal_granularity.startswith("annual") or self.temporal_granularity.startswith("Year") or self.temporal_granularity.startswith("year"):      
                #if self.vars[i].var.getTime().getBounds() == None:
                cdutil.times.setTimeBoundsMonthly(self.vars[i].var) 

                #setBoundsFor1DAxis(self.vars[i].var, 0)
                outvar.var = cdutil.times.YEAR(self.vars[i].var) 
      
            elif self.temporal_granularity.startswith("Season") or self.temporal_granularity.startswith("season"):
                #if self.vars[i].var.getTime().getBounds() == None:
                cdutil.times.setTimeBoundsMonthly(self.vars[i].var) 
                #setBoundsFor1DAxis(self.vars[i].var, 0)
                outvar.var = cdutil.times.SEASONALCYCLE(self.vars[i].var) 

            elif self.temporal_granularity.startswith("Month") or self.temporal_granularity.startswith("month"):
                #if self.vars[i].var.getTime().getBounds() == None:
                cdutil.times.setTimeBoundsDaily(self.vars[i].var) 

                #setBoundsFor1DAxis(self.vars[i].var, 0)
                outvar.var = cdutil.times.ANNUALCYCLE(self.vars[i].var) 
            else:
                #if self.vars[i].var.getTime().getBounds() == None:
                cdutil.times.setTimeBoundsDaily(self.vars[i].var) 
                #setBoundsFor1DAxis(self.vars[i].var, 0)
                func = getattr(cdutil.times,self.temporal_granularity)
                outvar.var = func(self.vars[i].var) 
          
 	    outvar.var.id = self.vars[i].var.id + '_' + self.temporal_granularity
            self.outvars.append(outvar)

        if len(self.vars) == 1: # only one output variable
            self.setResult("output_vars", self.outvars[0])
        else:  # a list of output variables
            self.setResult("output_vars", self.outvars)




class LongTermTemporalMean(Module):
    """

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

    """


    _input_ports = expand_port_specs([("input_vars", "gov.llnl.uvcdat.cdms:CDMSVariable"),
                                      ("temporal_granularity", "basic:String")])
 
    _output_ports = expand_port_specs([("output_vars", "gov.llnl.uvcdat.cdms:CDMSVariable")])


    def compute(self):
     	if not self.hasInputFromPort('input_vars'):
            raise ModuleError(self, "'input_vars' is mandatory.")
	else:
	    vars1 = self.getInputFromPort('input_vars')
            vars2 = self.getInputListFromPort('input_vars')
            if type(vars1) is list:  # the input is a list of variables
                self.vars = vars1
            else:  # the input is multiple CDMSVariables pointing to this module
                self.vars = vars2
   

        if not self.hasInputFromPort("temporal_granularity"):
            raise ModuleError(self, "'temporal_granularity' is mandatory.")
        else:
            self.temporal_granularity = self.getInputFromPort('temporal_granularity')

        self.outvars = []
        

        # add proper bounds if there are no bounds definition in the .nc file

        for i in range(len(self.vars)):  
            outvar = CDMSVariable(filename=None,name=self.vars[i].var.id)
            #outvar.var = self.vars[i].var.clone()
            
            if self.temporal_granularity.startswith("Annual") or self.temporal_granularity.startswith("annual") or self.temporal_granularity.startswith("Year") or self.temporal_granularity.startswith("year"):      
                #if self.vars[i].var.getTime().getBounds() == None:
                cdutil.times.setTimeBoundsMonthly(self.vars[i].var) 
                #setBoundsFor1DAxis(self.vars[i].var, 0)

                yearVar = cdutil.times.YEAR(self.vars[i].var)
                outvar.var = genutil.averager(yearVar, action='average', axis='(' + yearVar.getTime().id + ')')


      
            elif self.temporal_granularity.startswith("Season") or self.temporal_granularity.startswith("season"):
                #if self.vars[i].var.getTime().getBounds() == None:
                cdutil.times.setTimeBoundsMonthly(self.vars[i].var) 
                #setBoundsFor1DAxis(self.vars[i].var, 0)
                var = cdutil.times.SEASONALCYCLE(self.vars[i].var) 


                seasonsAvgArray = []
                numOfTotalSeasons = var.getTime().shape[0]
                numOfYears = numOfTotalMonths /4
                  
                for t in range(12):
                    aSeasonArray = []
                    for k in range(numOfYears + 1):
                        index = k*12 + t
                        if index < numOfTotalSeasons:
                            aSeasonArray.append(var[k*12 + t])
                    aSeasonVar = MV2.array(aSeasonArray)  #comipile a season of all the years into one var
                    setBoundsFor1DAxis(aSeasonArray, 0)
                    seasonsAvgArray.append(genutil.averager(aSeasonVar, action='average', axis=0))

                outvar.var = MV2.array(seasonsAvgArray)
                outvar.var.getAxis(0).id = 'seasons'
                outvar.var.setAxis(1,self.vars[i].var.getAxis(1))
                outvar.var.setAxis(2,self.vars[i].var.getAxis(2))



            elif self.temporal_granularity.startswith("Month") or self.temporal_granularity.startswith("month"):
                #if self.vars[i].var.getTime().getBounds() == None:
                cdutil.times.setTimeBoundsDaily(self.vars[i].var) 

                #setBoundsFor1DAxis(self.vars[i].var, 0)
                #calculate monthly mean first
                var = cdutil.times.ANNUALCYCLE(self.vars[i].var) 

                monthsAvgArray = []
                numOfTotalMonths = var.getTime().shape[0]
                numOfYears = numOfTotalMonths /12
                  
                for t in range(12):
                    aMonthArray = []
                    for k in range(numOfYears + 1):
                        index = k*12 + t
                        if index < numOfTotalMonths:
                            aMonthArray.append(var[k*12 + t])
                    aMonthVar = MV2.array(aMonthArray)
                    setBoundsFor1DAxis(aMonthVar, 0)
                    monthsAvgArray.append(genutil.averager(aMonthVar, action='average', axis=0))



                outvar.var = MV2.array(monthsAvgArray)
                outvar.var.getAxis(0).id = 'months'
                outvar.var.setAxis(1,self.vars[i].var.getAxis(1))
                outvar.var.setAxis(2,self.vars[i].var.getAxis(2))
                



            else:
                #if self.vars[i].var.getTime().getBounds() == None:
                cdutil.times.setTimeBoundsDaily(self.vars[i].var) 
                #setBoundsFor1DAxis(self.vars[i].var, 0)
                func = getattr(cdutil.times,self.temporal_granularity)
                var = func(self.vars[i].var)
                outvar.var = genutil.averager(var, action='average', axis='(' + var.getTime().id + ')')

          
 	    outvar.var.id = self.vars[i].var.id + '_' + self.temporal_granularity
            self.outvars.append(outvar)

        if len(self.vars) == 1: # only one output variable
            self.setResult("output_vars", self.outvars[0])
        else:  # a list of output variables
            self.setResult("output_vars", self.outvars)





class Statistics(Module):
    """
Statistics
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

    """
    _input_ports = expand_port_specs([("input_vars", "gov.llnl.uvcdat.cdms:CDMSVariable"),
                                      ("statistics", "basic:String"),
                                      ("list_of_summary_axis", "basic:List")])
 
    _output_ports = expand_port_specs([("output_vars", "gov.llnl.uvcdat.cdms:CDMSVariable")])


    def compute(self):
     	if not self.hasInputFromPort('input_vars'):
            raise ModuleError(self, "'input_vars' is mandatory.")
	else:
	    vars1 = self.getInputFromPort('input_vars')
            vars2 = self.getInputListFromPort('input_vars')
            if type(vars1) is list:  # the input is a list of variables
                self.vars = vars1
            else:  # the input is multiple CDMSVariables pointing to this module
                self.vars = vars2
   

        if not self.hasInputFromPort("statistics"):
            raise ModuleError(self, "'statistics' is mandatory.")
        else:
            self.statistics = self.getInputFromPort('statistics')


        if not self.hasInputFromPort("list_of_summary_axis"):
            raise ModuleError(self, "'list_of_summary_axis' is mandatory.")
        else:
            self.list_of_summary_axis = self.getInputFromPort('list_of_summary_axis')


        if all(isinstance(i, int) for i in self.list_of_summary_axis) == False: # if all elements in a list are integer
            raise ModuleError(self, "'list_of_summary_axis' must only contain integers")


        self.outvars = []

        for i in range(len(self.vars)):


            # set proper bounds before statistics
            curved = len(self.vars[i].var.getLatitude().shape) > 1 or len(self.vars[i].var.getLatitude().shape) > 1

            if curved:
                setLatLonBoundsForCurvilinear(self.vars[i].var)
      
            for j in range(len(self.vars[i].var.getAxisList())):
                setBoundsFor1DAxis(self.vars[i].var, j)

            outvar = CDMSVariable(filename=None,name=self.vars[i].var.id)      

            axisOption = ''
            for axisIndex in self.list_of_summary_axis:
                if axisIndex >= 0 and axisIndex < len(self.vars[i].var.getAxisList()):
                    axisOption += '(' + self.vars[i].var.getAxis(axisIndex).id + ')'

            if axisOption == '': # the default option is do statistics along the first axis
                axisOption = '(' + self.vars[i].var.getAxis(0).id + ')'


            if self.statistics.startswith("mean") or self.statistics.startswith("Mean") or self.statistics.startswith("aver") or self.statistics.startswith("Aver") or self.statistics.startswith("avg") or self.statistics.startswith("Avg"):
                outvar.var = genutil.averager(self.vars[i].var, action='average', axis=axisOption)
            elif self.statistics.startswith("sum") or self.statistics.startswith("Sum") :
                outvar.var = genutil.averager(self.vars[i].var, action='sum', axis=axisOption)
            elif self.statistics.startswith("std") or self.statistics.startswith("Std") or self.statistics.startswith("stand") or self.statistics.startswith("Stand"):
                outvar.var = genutil.statistics.std(self.vars[i].var, centered=1, biased=1, max_pct_missing=100.0, axis=axisOption)
            elif self.statistics.startswith("var") or self.statistics.startswith("Var"):
                outvar.var = genutil.statistics.variance(self.vars[i].var, centered=1, biased=1, max_pct_missing=100.0, axis=axisOption)
            elif self.statistics.startswith("med") or self.statistics.startswith("Med"):
                outvar.var = genutil.statistics.median(self.vars[i].var, axis=axisOption)
            elif self.statistics.startswith("min") or self.statistics.startswith("Min"):
                outvar.var = genutil.statistics.percentiles(self.vars[i].var, percentiles=[0], axis=axisOption)
            elif self.statistics.startswith("max") or self.statistics.startswith("Min"):
                outvar.var = genutil.statistics.percentiles(self.vars[i].var, percentiles=[100], axis=axisOption)


 	    outvar.var.id = self.vars[i].var.id + "_" + axisOption + "_" + self.statistics
            self.outvars.append(outvar)


        if len(self.vars) == 1: # only one output variable
            self.setResult("output_vars", self.outvars[0])
        else:  # a list of output variables
            self.setResult("output_vars", self.outvars)




class StatisticsAlongTemporalAxis(Module):
    """

StatisticsAlongTemporalAxis
===========================

This module is used to calculate basic statistic along temporal aixs.

Input
----------
input_vars: one CDMSVariable module, multiple CDMSVariable modules or a list of CDMSVariables attached to single CDMSVariable module

statistics: the supported statistics include: mean, sum, std, variance, max, min.


Output
-----------

The output can be one CDMSVariable module or a list of CDMSVariables attached to single CDMSVariable module  


    """
    _input_ports = expand_port_specs([("input_vars", "gov.llnl.uvcdat.cdms:CDMSVariable"),
                                      ("statistics", "basic:String")])
 
    _output_ports = expand_port_specs([("output_vars", "gov.llnl.uvcdat.cdms:CDMSVariable")])


    def compute(self):
     	if not self.hasInputFromPort('input_vars'):
            raise ModuleError(self, "'input_vars' is mandatory.")
	else:
	    vars1 = self.getInputFromPort('input_vars')
            vars2 = self.getInputListFromPort('input_vars')
            if type(vars1) is list:  # the input is a list of variables
                self.vars = vars1
            else:  # the input is multiple CDMSVariables pointing to this module
                self.vars = vars2
   

        if not self.hasInputFromPort("statistics"):
            raise ModuleError(self, "'statistics' is mandatory.")
        else:
            self.statistics = self.getInputFromPort('statistics')


        self.outvars = []

        for i in range(len(self.vars)):


            # set proper bounds before statistics
            curved = len(self.vars[i].var.getLatitude().shape) > 1 or len(self.vars[i].var.getLatitude().shape) > 1

            if curved:
                setLatLonBoundsForCurvilinear(self.vars[i].var)
      
            for j in range(len(self.vars[i].var.getAxisList())):
                setBoundsFor1DAxis(self.vars[i].var, j)

            outvar = CDMSVariable(filename=None,name=self.vars[i].var.id)      

            axisOption =  '(' + self.vars[i].var.getTime().id + ')'


            if self.statistics.startswith("mean") or self.statistics.startswith("Mean") or self.statistics.startswith("aver") or self.statistics.startswith("Aver") or self.statistics.startswith("avg") or self.statistics.startswith("Avg"):
                outvar.var = genutil.averager(self.vars[i].var, action='average', axis=axisOption)
            elif self.statistics.startswith("sum") or self.statistics.startswith("Sum") :
                outvar.var = genutil.averager(self.vars[i].var, action='sum', axis=axisOption)
            elif self.statistics.startswith("std") or self.statistics.startswith("Std") or self.statistics.startswith("stand") or self.statistics.startswith("Stand"):
                outvar.var = genutil.statistics.std(self.vars[i].var, centered=1, biased=1, max_pct_missing=100.0, axis=axisOption)
            elif self.statistics.startswith("var") or self.statistics.startswith("Var"):
                outvar.var = genutil.statistics.variance(self.vars[i].var, centered=1, biased=1, max_pct_missing=100.0, axis=axisOption)
            elif self.statistics.startswith("med") or self.statistics.startswith("Med"):
                outvar.var = genutil.statistics.median(self.vars[i].var, axis=axisOption)
            elif self.statistics.startswith("min") or self.statistics.startswith("Min"):
                outvar.var = genutil.statistics.percentiles(self.vars[i].var, percentiles=[0], axis=axisOption)
            elif self.statistics.startswith("max") or self.statistics.startswith("Min"):
                outvar.var = genutil.statistics.percentiles(self.vars[i].var, percentiles=[100], axis=axisOption)
 	    outvar.var.id = self.vars[i].var.id + "_" + axisOption + "_" + self.statistics
            self.outvars.append(outvar)


        if len(self.vars) == 1: # only one output variable
            self.setResult("output_vars", self.outvars[0])
        else:  # a list of output variables
            self.setResult("output_vars", self.outvars)




class StatisticsAlongSpatialAxis(Module):
    """
StatisticsAlongSpatialAxis
==========================
This module is used to calculate basic statistic along spatial aixs (lat/lon or x/y). For example, if you want to get the mean value for a spatial region, you can use this module.



Input
----------
input_vars: one CDMSVariable module, multiple CDMSVariable modules or a list of CDMSVariables attached to single CDMSVariable module

statistics: the supported statistics include: mean, sum, std, variance, max, min.


Output
-----------

The output can be one CDMSVariable module or a list of CDMSVariables attached to single CDMSVariable module  

    """
    _input_ports = expand_port_specs([("input_vars", "gov.llnl.uvcdat.cdms:CDMSVariable"),
                                      ("statistics", "basic:String")])
 
    _output_ports = expand_port_specs([("output_vars", "gov.llnl.uvcdat.cdms:CDMSVariable")])


    def compute(self):
     	if not self.hasInputFromPort('input_vars'):
            raise ModuleError(self, "'input_vars' is mandatory.")
	else:
	    vars1 = self.getInputFromPort('input_vars')
            vars2 = self.getInputListFromPort('input_vars')
            if type(vars1) is list:  # the input is a list of variables
                self.vars = vars1
            else:  # the input is multiple CDMSVariables pointing to this module
                self.vars = vars2
   

        if not self.hasInputFromPort("statistics"):
            raise ModuleError(self, "'statistics' is mandatory.")
        else:
            self.statistics = self.getInputFromPort('statistics')


        self.outvars = []

        for i in range(len(self.vars)):


            # set proper bounds before statistics
            curved = len(self.vars[i].var.getLatitude().shape) > 1 or len(self.vars[i].var.getLatitude().shape) > 1

            if curved:
                setLatLonBoundsForCurvilinear(self.vars[i].var)
      
            for j in range(len(self.vars[i].var.getAxisList())):
                setBoundsFor1DAxis(self.vars[i].var, j)

            outvar = CDMSVariable(filename=None,name=self.vars[i].var.id) 


            numOfAxis = len(self.vars[i].var.shape) 

            latAxis = -1 
            lonAxis = -1
            xAxis = -1
            yAxis = -1


            for j in range(numOfAxis):
                if self.vars[i].var.getAxis(j).isLatitude():
                    latAxis = j
                if self.vars[i].var.getAxis(j).isLongitude():
                    lonAxis = j
                if self.vars[i].var.getAxis(j).id == 'x' or self.vars[0].var.getAxis(j).id == 'X':
                    xAxis = j
                if self.vars[i].var.getAxis(j).id == 'y' or self.vars[0].var.getAxis(j).id == 'Y':
                    yAxis = j

   
            if xAxis <> -1 and yAxis <> -1: # projected or arbitrary coordinate
	        axisOption =  '(' + self.vars[i].var.getAxis(xAxis).id + ')' + '(' + self.vars[i].var.getAxis(yAxis).id + ')'
            elif latAxis <> -1 and lonAxis <> -1: # lat, lon
                axisOption =  '(' + self.vars[i].var.getAxis(latAxis).id + ')' + '(' + self.vars[i].var.getAxis(lonAxis).id + ')'
            else: #not supported
            	raise Exception("The input netcdf files should have 'x','y' or 'lat', 'lon' axis")


            if self.statistics.startswith("mean") or self.statistics.startswith("Mean") or self.statistics.startswith("aver") or self.statistics.startswith("Aver") or self.statistics.startswith("avg") or self.statistics.startswith("Avg"):
                outvar.var = genutil.averager(self.vars[i].var, action='average', axis=axisOption)
            elif self.statistics.startswith("sum") or self.statistics.startswith("Sum") :
                outvar.var = genutil.averager(self.vars[i].var, action='sum', axis=axisOption)
            elif self.statistics.startswith("std") or self.statistics.startswith("Std") or self.statistics.startswith("stand") or self.statistics.startswith("Stand"):
                outvar.var = genutil.statistics.std(self.vars[i].var, centered=1, biased=1, max_pct_missing=100.0, axis=axisOption)
            elif self.statistics.startswith("var") or self.statistics.startswith("Var"):
                outvar.var = genutil.statistics.variance(self.vars[i].var, centered=1, biased=1, max_pct_missing=100.0, axis=axisOption)
            elif self.statistics.startswith("med") or self.statistics.startswith("Med"):
                outvar.var = genutil.statistics.median(self.vars[i].var, axis=axisOption)
            elif self.statistics.startswith("min") or self.statistics.startswith("Min"):
                outvar.var = genutil.statistics.percentiles(self.vars[i].var, percentiles=[0], axis=axisOption)
            elif self.statistics.startswith("max") or self.statistics.startswith("Min"):
                outvar.var = genutil.statistics.percentiles(self.vars[i].var, percentiles=[100], axis=axisOption)

 	    outvar.var.id = self.vars[i].var.id + "_" + axisOption + "_" + self.statistics
            self.outvars.append(outvar)


        if len(self.vars) == 1: # only one output variable
            self.setResult("output_vars", self.outvars[0])
        else:  # a list of output variables
            self.setResult("output_vars", self.outvars)





class GetDaymetTileList(Module):

    """
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


    """
    #input: variable name, spatial extent, time range
    #output: a configuration file
    _input_ports = expand_port_specs([	("var_name", "basic:String"),
                                        ("longitude_min", "basic:Float"),
					("latitude_min", "basic:Float"),
                                        ("longitude_max", "basic:Float"),
					("latitude_max", "basic:Float"),
                                        ("year", "basic:Integer"),
                                        ("tile_list_file", "basic:String")])
    _output_ports = expand_port_specs([("output_list_file", "edu.utah.sci.vistrails.basic:File")])


    def compute(self):

        if not self.hasInputFromPort('var_name'):
            raise ModuleError(self, "'var_name' is mandatory.")
	else:
	    self.var_name = self.getInputFromPort('var_name')


        self.tile_list_file = self.forceGetInputFromPort('tile_list_file')

        if not self.hasInputFromPort('year'):
            raise ModuleError(self, "'year' is mandatory.")
	else:
	    self.year = self.getInputFromPort('year')
 

        if not self.hasInputFromPort('longitude_min'):
            raise ModuleError(self, "'longitude_min' is mandatory.")
	else:
            self.longitude_min = self.getInputFromPort('longitude_min')
        if not self.hasInputFromPort('latitude_min'):
            raise ModuleError(self, "'latitude_min' is mandatory.")
	else:
            self.latitude_min = self.getInputFromPort('latitude_min')

        if not self.hasInputFromPort('longitude_max'):
            raise ModuleError(self, "'longitude_max' is mandatory.")
	else:
            self.longitude_max = self.getInputFromPort('longitude_max')
        if not self.hasInputFromPort('latitude_max'):
            raise ModuleError(self, "'latitude_max' is mandatory.")
	else:
	    self.latitude_max = self.getInputFromPort('latitude_max')

	
        
        self.fileObj = self.interpreter.filePool.create_file()
        listfile = open(self.fileObj.name, 'w')


        if self.tile_list_file <> None and self.tile_list_file <> '':
            listfileHardDisk = open(self.tile_list_file,'w')


        listOfTiles = []


        startRow = int(self.latitude_min/2 + 45)
        startCol = int((180 + self.longitude_min) / 2) + 1

        

        endRow = self.latitude_max/2 + 45
        if endRow%2 == 0:
            endRow = int(self.latitude_max/2 + 45) -1
        else:
            endrow = int(self.latitude_max/2 + 45)
        endCol = (180 + self.longitude_max) / 2 
        if endCol%2 == 0:
            endCol = int((180 + self.longitude_max) / 2)
        else:
            endCol = int((180 + self.longitude_max) / 2) + 1

        for i in range(startRow, endRow+1):
            for j in range(startCol, endCol+1):
                print i*180+j
                listOfTiles.append(i*180+j)



        urls_to_get=[]

        numOfTiles = (self.year_max - self.year_min + 1) * len(listOfTiles)

        listfile.write(str(numOfTiles) + '\n')


        if self.tile_list_file <> None and self.tile_list_file <> '':
            listfileHardDisk.write(str(numOfTiles) + '\n')


        base_url = 'http://daymet.ornl.gov/thredds//dodsC/allcf/'
        #base_url = 'http://daymet.ornl.gov/thredds/fileServer/allcf/'
        #for year in range(self.year_min, self.year_max + 1):
        for tile in listOfTiles:
            url = base_url + str(self.year) + '/' + str(tile) + '_' + str(self.year) + '/' + self.var_name + '.nc'
            urls_to_get.append(url)       
            aline = url + ';' + self.var_name + '\n'
            #print aline
            listfile.write(aline)
            if self.tile_list_file <> None and self.tile_list_file <> '':
                listfileHardDisk.write(aline)
    
        listfile.close()

        if self.tile_list_file <> None and self.tile_list_file <> '': 
            listfileHardDisk.close()
        self.setResult("output_list_file", self.fileObj)



class DownloadDaymetTiles(Module):
    """
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

    """

    _input_ports = expand_port_specs([	("var_name", "basic:String"),
                                        ("output_folder", "basic:String"),
                                        ("longitude_min", "basic:Float"),
					("latitude_min", "basic:Float"),
                                        ("longitude_max", "basic:Float"),
					("latitude_max", "basic:Float"),
                                        ("year_min", "basic:Integer"),
					("year_max", "basic:Integer"),
                                        ("tile_list_file", "basic:String")])
    #_output_ports = expand_port_specs([("output_list_file", "edu.utah.sci.vistrails.basic:File")])



    def compute(self):

        if not self.hasInputFromPort('var_name'):
            raise ModuleError(self, "'var_name' is mandatory.")
	else:
	    self.var_name = self.getInputFromPort('var_name')

        if not self.hasInputFromPort('output_folder'):
            raise ModuleError(self, "'output_folder' is mandatory.")
	else:
	    self.output_folder = self.getInputFromPort('output_folder')


        if not self.hasInputFromPort('year_min'):
            raise ModuleError(self, "'year_min' is mandatory.")
	else:
	    self.year_min = self.getInputFromPort('year_min')

        if not self.hasInputFromPort('year_max'):
            raise ModuleError(self, "'year_max' is mandatory.")
	else:
	    self.year_max = self.getInputFromPort('year_max')
 
	if not self.hasInputFromPort('longitude_min'):
            raise ModuleError(self, "'longitude_min' is mandatory.")
	else:
            self.longitude_min = self.getInputFromPort('longitude_min')
        if not self.hasInputFromPort('latitude_min'):
            raise ModuleError(self, "'latitude_min' is mandatory.")
	else:
            self.latitude_min = self.getInputFromPort('latitude_min')

        if not self.hasInputFromPort('longitude_max'):
            raise ModuleError(self, "'longitude_max' is mandatory.")
	else:
            self.longitude_max = self.getInputFromPort('longitude_max')
        if not self.hasInputFromPort('latitude_max'):
            raise ModuleError(self, "'latitude_max' is mandatory.")
	else:
	    self.latitude_max = self.getInputFromPort('latitude_max')


        self.tile_list_file = self.forceGetInputFromPort('tile_list_file')



        listOfTiles = []


        startRow = int(self.latitude_min/2 + 45)
        startCol = int((180 + self.longitude_min) / 2) + 1

        


        endRow = int(self.latitude_max/2 + 45)

        if endRow%2 == 0:
            endRow = int(self.latitude_max/2 + 45) -1
        else:
            endrow = int(self.latitude_max/2 + 45)
        endCol = int((180 + self.longitude_max) / 2)

        if endCol%2 == 0:
            endCol = int((180 + self.longitude_max) / 2)
        else:
            endCol = int((180 + self.longitude_max) / 2) + 1

        for i in range(startRow, endRow+1):
            for j in range(startCol, endCol+1):
                print i*180+j
                listOfTiles.append(i*180+j)



        urls_to_get=[]

        numOfTiles = (self.year_max - self.year_min + 1) * len(listOfTiles)

        if self.tile_list_file <> None and self.tile_list_file <> '':
            listfileHardDisk = open(self.tile_list_file,'w')
            listfileHardDisk.write(str(numOfTiles) + '\n')


        #base_url = 'http://daymet.ornl.gov/thredds//dodsC/allcf/'
        base_url = 'http://daymet.ornl.gov/thredds/fileServer/allcf/'
        for year in range(self.year_min, self.year_max + 1):
            for tile in listOfTiles:
                url = base_url + str(year) + '/' + str(tile) + '_' + str(year) + '/' + self.var_name + '.nc'
                urls_to_get.append(url)       
                u = urllib2.urlopen(url) 
                filename = self.output_folder + "/" + str(tile) + '_' + self.var_name + '_' + str(year) + '.nc'
                
                if self.tile_list_file <> None and self.tile_list_file <> '':
                    aline = filename + ';' + self.var_name + '\n'
                    listfileHardDisk.write(aline)


                localFile = open(filename, 'wb')
                localFile.write(u.read())
                localFile.close() 
      
        if self.tile_list_file <> None and self.tile_list_file <> '':
            listfileHardDisk.close()



class ParallelDownloadDaymetTiles(Module):
    """
ParallelDownloadDaymetTiles
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

    """


    _input_ports = expand_port_specs([	("var_name", "basic:String"),
                                        ("output_folder", "basic:String"),
                                        ("longitude_min", "basic:Float"),
					("latitude_min", "basic:Float"),
                                        ("longitude_max", "basic:Float"),
					("latitude_max", "basic:Float"),
                                        ("year_min", "basic:Integer"),
					("year_max", "basic:Integer"),
                                        ("tile_list_file", "basic:String")])
    #_output_ports = expand_port_specs([("output_list_file", "edu.utah.sci.vistrails.basic:File")])



    def compute(self):

        if not self.hasInputFromPort('var_name'):
            raise ModuleError(self, "'var_name' is mandatory.")
	else:
	    self.var_name = self.getInputFromPort('var_name')

        if not self.hasInputFromPort('output_folder'):
            raise ModuleError(self, "'output_folder' is mandatory.")
	else:
	    self.output_folder = self.getInputFromPort('output_folder')


        if not self.hasInputFromPort('year_min'):
            raise ModuleError(self, "'year_min' is mandatory.")
	else:
	    self.year_min = self.getInputFromPort('year_min')

        if not self.hasInputFromPort('year_max'):
            raise ModuleError(self, "'year_max' is mandatory.")
	else:
	    self.year_max = self.getInputFromPort('year_max')
 
	if not self.hasInputFromPort('longitude_min'):
            raise ModuleError(self, "'longitude_min' is mandatory.")
	else:
            self.longitude_min = self.getInputFromPort('longitude_min')
        if not self.hasInputFromPort('latitude_min'):
            raise ModuleError(self, "'latitude_min' is mandatory.")
	else:
            self.latitude_min = self.getInputFromPort('latitude_min')

        if not self.hasInputFromPort('longitude_max'):
            raise ModuleError(self, "'longitude_max' is mandatory.")
	else:
            self.longitude_max = self.getInputFromPort('longitude_max')
        if not self.hasInputFromPort('latitude_max'):
            raise ModuleError(self, "'latitude_max' is mandatory.")
	else:
	    self.latitude_max = self.getInputFromPort('latitude_max')


        self.tile_list_file = self.forceGetInputFromPort('tile_list_file')

        if self.tile_list_file == None or self.tile_list_file == "":
            self.tile_list_file = "#"


        os.system("python download.py " + self.var_name + " " +self.output_folder + " " + str(self.year_min) + " " + str(self.year_max) + " " + str(self.longitude_min) + " " + str(self.longitude_max) + " " + str(self.latitude_min) + " " + str(self.latitude_max) + " " + self.tile_list_file )





class ReadMultipleVariables(Module):
    """

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

    """

    _input_ports  = expand_port_specs([("variable_list_file", "edu.utah.sci.vistrails.basic:File")])
    _output_ports = expand_port_specs([("output_vars", "gov.llnl.uvcdat.cdms:CDMSVariable")])

    def compute(self):
        fileObj = self.getInputFromPort("variable_list_file")

        ncfiles    = []
        variables = []
        self.outvars = []
        
        listfile = open(fileObj.name, 'r')

        numvars = int(listfile.readline().strip())

        for i in range(numvars): 
           line = listfile.readline().strip().split(';')
           outvar = CDMSVariable(filename=None,name=line[1])
           f = cdms2.open(line[0])
           outvar.var = f(line[1])
           outvar.var.id = line[1]
           f.close()
           self.outvars.append(outvar)

        if numvars == 1: # only one output variable
            self.setResult("output_vars", self.outvars[0])
        else:  # a list of output variables
            self.setResult("output_vars", self.outvars)


class UnitConvertor(Module):

    #input: a list of variables (attach to one CDMSVariable) or multiple CDMSVariables pointing to this module
    #output:a list of variable or only one variable

    """
UnitConverter
=============

This module is used to convert unit for a variable. 

Input
----------

input_vars: one CDMSVariable module, multiple CDMSVariable modules or a list of CDMSVariables attached to single CDMSVariable module

target_units: target unit must be UDUNITS (http://www.unidata.ucar.edu/software/udunits/) compatible



Output
-----------

The output can be one CDMSVariable module or a list of CDMSVariables attached to single CDMSVariable module 
   """

    _input_ports = expand_port_specs([("input_vars", "gov.llnl.uvcdat.cdms:CDMSVariable"),
                                      ("target_unit", "basic:String")])
 
    _output_ports = expand_port_specs([("output_vars", "gov.llnl.uvcdat.cdms:CDMSVariable")])


   
  
    def compute(self):
     	if not self.hasInputFromPort('input_vars'):
            raise ModuleError(self, "'input_vars' is mandatory.")
	else:
	    vars1 = self.getInputFromPort('input_vars')
            vars2 = self.getInputListFromPort('input_vars')
            if type(vars1) is list:  # the input is a list of variables
                self.vars = vars1
            else:  # the input is multiple CDMSVariables pointing to this module
                self.vars = vars2
   

        if not self.hasInputFromPort("target_unit"):
            raise ModuleError(self, "'target_unit' is mandatory.")
        else:
            self.target_unit = self.getInputFromPort('target_unit')
   

       
        self.outvars = []
        

        for i in range(len(self.vars)):
  
            outvar = CDMSVariable(filename=None,name=self.vars[i].var.id)
            #outvar.var = self.vars[i].var.clone()
            
            # check if target unit is UDUNITS compatible
	    try:
	        tmp = genutil.udunits(0,self.target_unit)
	        tmp.to(self.target_unit)
	    except(TypeError):
	        raise Exception("The target unit is not supported")

            # check if the unit of the input variable is UDUNITS compatible
	    try:
	        tmp = genutil.udunits(0,self.vars[i].var.units)
	        tmp.to(self.vars[i].var.units)
	    except(TypeError):
	        raise Exception("The unit of the input variable is not supported")


            # do the actual conversion
	    try:
       	        oldunits = genutil.udunits(self.vars[i].var, self.vars[i].var.units)        
       	        newunits = oldunits.to(self.target_unit)
	        outvar.var = newunits.value
	        outvar.var.units = self.target_unit
	    except(TypeError):
	        raise Exception("The two units are not convertible")


 	    outvar.var.id = self.vars[i].var.id
            self.outvars.append(outvar)

        if len(self.vars) == 1: # only one output variable
            self.setResult("output_vars", self.outvars[0])
        else:  # a list of output variables
            self.setResult("output_vars", self.outvars)
    
    

class SaveVariablesToFiles(Module):
    """
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
   """


    _input_ports = expand_port_specs([("input_vars", "gov.llnl.uvcdat.cdms:CDMSVariable"),
                                      ("file_names", "basic:List")])
 
    def compute(self):

	if not self.hasInputFromPort('input_vars'):
            raise ModuleError(self, "'input_vars' is mandatory.")
	else:
	    vars1 = self.getInputFromPort('input_vars')
            vars2 = self.getInputListFromPort('input_vars')
            if type(vars1) is list:  # the input is a list of variables
                self.vars = vars1
            else:
                self.vars = vars2   # the input is multiple CDMSVariables pointing to this module
   
     
        if not self.hasInputFromPort("file_names"):
            raise ModuleError(self, "'file_names' is mandatory.")
        else:
            self.file_names = self.getInputFromPort('file_names')

        if len(self.vars) != len(self.file_names):
            raise Exception("The number of variables and the number of file names do not match")
        
        for i in range(len(self.vars)):
            cdmsf = cdms2.open(self.file_names[i], 'w')
            cdmsf.write(self.vars[i].var)
            cdmsf.close()



       
            
class SpatialSubset(Module):

   """
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


   """



    _input_ports = expand_port_specs([("input_vars", "gov.llnl.uvcdat.cdms:CDMSVariable"),
                                      ("mask_var", "gov.llnl.uvcdat.cdms:CDMSVariable"),
  				      ("mask_value", "basic:Float"),
                                      ("mask_index", "basic:Integer")])
    _output_ports = expand_port_specs([("output_vars", "gov.llnl.uvcdat.cdms:CDMSVariable")])


    
    def compute(self):
      	if not self.hasInputFromPort('input_vars'):
            raise ModuleError(self, "'input_vars' is mandatory.")
	else:
	    vars1 = self.getInputFromPort('input_vars')
            vars2 = self.getInputListFromPort('input_vars')
            if type(vars1) is list:  # the input is a list of variables
                self.vars = vars1
            else:  # the input is multiple CDMSVariables pointing to this module
                self.vars = vars2
   
        
        if not self.hasInputFromPort('mask_var'):
            raise ModuleError(self, "'mask_var' is mandatory.")
	else:
            self.mask_var = self.getInputFromPort('mask_var')

     	if not self.hasInputFromPort("mask_value"):
            raise ModuleError(self, "'mask_value' is mandatory.")
	else:
	    self.mask_value = self.getInputFromPort("mask_value")
         
        self.mask_index = self.forceGetInputFromPort('mask_index') 


        self.outvars = []       

        for i in range(len(self.vars)):
            outvar = CDMSVariable(filename=None,name=self.vars[i].var.id)
         
            #self.outvar = CDMSVariable(filename=None,name=self.var.var.id)
            outvar.var = self.vars[i].var.clone()
            numOfLayers = outvar.var.mask.shape[0]

	    # regrid the mask variable as float type 
            # note: if no mask_index is specified or it is invalid, the first layer of mask variable is used
            if self.mask_index == None or self.mask_index < 0 or self.mask_index >= numOfLayers :
                mask_var_regrid = self.mask_var.var[0].astype('f').regrid(outvar.var.getGrid()) 
            else:
                mask_var_regrid = self.mask_var.var[self.mask_index].astype('f').regrid(outvar.var.getGrid())

 
            new_mask_var = MV2.masked_equal(mask_var_regrid, self.mask_value)
            new_mask = MV2.getmask(new_mask_var)

            
    
	    if outvar.var.mask <> None:
	        for j in range(numOfLayers):
            	    outvar.var.mask[j] = MV2.logical_or(outvar.var.mask[j], new_mask)
            else:
	        for j in range(numOfLayers):
            	    outvar.var.mask[j] = new_mask;

            self.outvars.append(outvar)

        if len(self.vars) == 1: # only one output variable
            self.setResult("output_vars", self.outvars[0])
        else:  # a list of output variables
            self.setResult("output_vars", self.outvars)


        
class Regrid(Module):


   """
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


   """


    #input: a list of variables (attach to one CDMSVariable) or multiple CDMSVariables pointing to this module
    #output:a list of variable or only one variable

    _input_ports = expand_port_specs([("input_vars", "gov.llnl.uvcdat.cdms:CDMSVariable"),
					("regrid_method", "basic:String"),
					("use_template", "basic:Boolean"),
                                        ("longitude_interval", "basic:Float"),
					("latitude_interval", "basic:Float"),
    					("template_var", "gov.llnl.uvcdat.cdms:CDMSVariable")])
    _output_ports = expand_port_specs([("output_vars", "gov.llnl.uvcdat.cdms:CDMSVariable")])


    def compute(self):
        if not self.hasInputFromPort('input_vars'):
            raise ModuleError(self, "'input_vars' is mandatory.")
	else:
	    vars1 = self.getInputFromPort('input_vars')
            vars2 = self.getInputListFromPort('input_vars')
            if type(vars1) is list:  # the input is a list of variables
                self.vars = vars1
            else:  # the input is multiple CDMSVariables pointing to this module
                self.vars = vars2


        self.regrid_method = self.forceGetInputFromPort('regrid_method')     
	self.use_template = self.forceGetInputFromPort('use_template')
	
	if self.use_template == None or self.use_template == False:
            if not self.hasInputFromPort('longitude_interval'):
                raise ModuleError(self, "'longitude_interval' is mandatory.")
	    else:
		self.longitude_interval = self.getInputFromPort('longitude_interval')
            if not self.hasInputFromPort('latitude_interval'):
                raise ModuleError(self, "'latitude_interval' is mandatory.")
	    else:
		self.latitude_interval = self.getInputFromPort('latitude_interval')

	else:
            if not self.hasInputFromPort('template_var'):
                raise ModuleError(self, "'template_var' is mandatory.")
            else:
		self.template_var = self.getInputFromPort('template_var')

        self.outvars = []        

        for v in range(len(self.vars)):
  
            outvar = CDMSVariable(filename=None,name=self.vars[v].var.id)

            regridToolStr = ''
	    regridMethodStr = ''


	    if self.regrid_method == 'bilinear':
	        regridToolStr = 'esmf'
                regridMethodStr = 'linear'
	    elif self.regrid_method == 'patch':
	        regridToolStr = 'esmf'
	        regridMethodStr = 'patch'
	    elif self.regrid_method == 'conserve':
	        regridToolStr = 'esmf'
	        regridMethodStr = 'conserve'	
	    else: #default is esmf-linear
	        regridToolStr = 'esmf'
	        regridMethodStr = 'linear'
	


            curved = len(self.vars[v].var.getLatitude().shape) > 1 or len(self.vars[v].var.getLatitude().shape) > 1

            if curved == True: 
                setLatLonBoundsForCurvilinear(self.vars[v].var)
           
            for j in range(len(self.vars[v].var.getAxisList())):
                setBoundsFor1DAxis(self.vars[v].var, j)

	    if self.use_template == None or self.use_template == False: # if there is no template

	        if curved == False: #the input var has a rectangular grid
                    # longitude needs special handling since it's cyclic
                    nLon = self.vars[v].var.getLongitude().shape[0]
	            firstLon = self.vars[v].var.getLongitude()[0]
                    lastLon = self.vars[v].var.getLongitude()[nLon-1]           

	            if self.vars[v].var.getLongitude()[1]  > 90 and firstLon < -90: #special case 1
                        left = lastLone
	                right = firstLon
                        interLon = 180 - self.vars[v].var.getLongitude()[1] + firstLon + 180
	   
	            elif firstLon > 90 and self.vars[v].var.getLongitude()[1] < -90: #special case 2
                        left = firstLon
                        right = lastLon
                        interLon = 180 - firstLon +  self.vars[v].var.getLongitude()[1] + 180

                    else:
                        interLon = self.vars[v].var.getLongitude()[1] - firstLon
		        if interLon > 0:
		            left = firstLon
		            right = lastLon
                        else:
		            left = lastLon
                            right = firstLon
                            interLon = - interLon
                    minLon_new = left - interLon/2 + self.longitude_interval/2 
                    if minLon_new < -180: #special case
                        minLon_new = 180 - (-180 - minLon_new)                
                    nLon_new =  math.ceil(interLon * nLon / self.longitude_interval)
                  
                    #latitude 
                    nLat = self.vars[v].var.getLatitude().shape[0]
	            firstLat = self.vars[v].var.getLatitude()[0]
	            lastLat = self.vars[v].var.getLatitude()[nLat-1]
	            if firstLat > lastLat:
		        maxLat = firstLat
		        minLat = lastLat
	            else:
		        maxLat = lastLat
		        minLat = firstLat	
	            interLat = (maxLat - minLat)/(nLat -1)
                    minLat_new = minLat - interLat/2 + self.latitude_interval/2  
                    nLat_new = math.ceil((maxLat - minLat + interLat) / self.latitude_interval)     

	        else: # the input var has a non-rectangular grid   
	  
                     # longitude needs special handling since it's cyclic
                     dataLon = self.vars[v].var.getLongitude().data
                  
                     right = self.vars[v].var.getLongitude().max()
                     left = self.vars[v].var.getLongitude().min()

                     lon_missing_value = self.vars[v].var.getLongitude().missing_value

                     nLon = int(abs(np.unravel_index(self.vars[v].var.getLongitude().argmax(), self.vars[v].var.getLongitude().shape)[1] - np.unravel_index(self.vars[v].var.getLongitude().argmin(), self.vars[v].var.getLongitude().shape)[1])) + 1

	             interLon = (right - left)/nLon

                     # special case 
                     for i in range(nLon-1):

                         if math.fabs(dataLon[0][i] - lon_missing_value) < 1 or math.fabs(dataLon[0][i+1] - lon_missing_value) < 1:
                             continue
                         if (dataLon[0][i] > 90 and dataLon[0][i+1] < -90) or (dataLon[0][i]  < -90 and dataLon[0][i+1] > 90):
                             right = dataLon[dataLon <= 0].max()
	                     left = dataLon[dataLon >= 0].min()
                             interLon = (-right + 180 - left)/nLon
		             break
              
             
                     minLon_new = left - interLon/2 + self.longitude_interval/2 
                     if minLon_new < -180: #special case
                         minLon_new = 180 - (-180 - minLon_new)                
                     nLon_new =  math.ceil(interLon * nLon / self.longitude_interval) 

        
                     # latitude
                     #dataLat = self.vars[v].var.getLatitude().data
                     maxLat = self.vars[v].var.getLatitude().max()
                     minLat = self.vars[v].var.getLatitude().min()
                     nLat = abs(np.unravel_index(self.vars[v].var.getLatitude().argmax(), self.vars[v].var.getLatitude().shape)[0] - np.unravel_index(self.vars[v].var.getLatitude().argmin(), self.vars[v].var.getLatitude().shape)[0]) + 1

                     #nLat = dataLat.shape[0]
         
	             interLat = (maxLat - minLat)/(nLat -1)
                     minLat_new = minLat - interLat/2 + self.latitude_interval/2   
                     nLat_new = math.ceil((maxLat - minLat + interLat) / self.latitude_interval)  


#                print minLat_new
#                print nLat_new
#                print self.latitude_interval
#                print minLon_new
#                print nLon_new
#                print self.longitude_interval


	        newgrid = cdms2.createUniformGrid(minLat_new, nLat_new, self.latitude_interval, minLon_new, nLon_new, self.longitude_interval, order="yx")
	        newgrid.getAxis(0).id='lat'
	        newgrid.getAxis(0).standard_name='latitude'
	        newgrid.getAxis(1).id='lon'
	        newgrid.getAxis(1).standard_name='longtitude'

	        outvar.var = self.vars[v].var.regrid(newgrid, regridTool=regridToolStr, regridMethod=regridMethodStr)
	        outvar.var.missing_value = self.vars[v].var.missing_value
	        outvar.var.id = self.vars[v].var.id

	    else: #if there is a template
	        outvar.var = self.vars[v].var.regrid(self.template_var.var.getGrid(), regridTool=regridToolStr, regridMethod=regridMethodStr)
	        outvar.var.missing_value = self.vars[v].var.missing_value
	        outvar.var.id = self.vars[v].var.id
	

            self.outvars.append(outvar)

        if len(self.vars) == 1: # only one output variable
            self.setResult("output_vars", self.outvars[0])
        else:  # a list of output variables
            self.setResult("output_vars", self.outvars)
    




class Mosaic(Module):

   """
Mosaic
====================

This module is used to mosaic multiple spatially adjacent variables into one variable.

Input
----------

input_vars: one CDMSVariable module, multiple CDMSVariable modules or a list of CDMSVariables attached to single CDMSVariable module


Output
-----------

The output is one CDMSVariable module that holds the result.


   """

    #input: a list of variables (attach to one CDMSVariable) or multiple CDMSVariables pointing to this module
    #output: one variable

    _input_ports = expand_port_specs([("input_vars", "gov.llnl.uvcdat.cdms:CDMSVariable")])

    _output_ports = expand_port_specs([("output_var", "gov.llnl.uvcdat.cdms:CDMSVariable")])

        
    def compute(self):

       	if not self.hasInputFromPort('input_vars'):
            raise ModuleError(self, "'input_vars' is mandatory.")
	else:
	    vars1 = self.getInputFromPort('input_vars')
            vars2 = self.getInputListFromPort('input_vars')
            if type(vars1) is list:  # the input is a list of variables
                self.vars = vars1
            else:  # the input is multiple CDMSVariables pointing to this module
                self.vars = vars2
 
        hasTime = False
        isXY = False
        isLatLon = False

        latAxis = -1 
        lonAxis = -1
        xAxis = -1
        yAxis = -1
        timeAxis = -1
        ntime = 0

        numOfAxis = len(self.vars[0].var.shape)  
        varid = self.vars[0].var.id


        for i in range(0, numOfAxis):
            if self.vars[0].var.getAxis(i).isLatitude():
                latAxis = i
            if self.vars[0].var.getAxis(i).isLongitude():
                lonAxis = i
            if self.vars[0].var.getAxis(i).id == 'x' or self.vars[0].var.getAxis(i).id == 'X':
                xAxis = i
            if self.vars[0].var.getAxis(i).id == 'y' or self.vars[0].var.getAxis(i).id == 'Y':
                yAxis = i
            if self.vars[0].var.getAxis(i).isTime():
                timeAxis = i
                ntime = self.vars[0].var.getAxis(i).shape[0]
          
        if timeAxis <> -1:
            hasTime = True
        if xAxis <> -1 and yAxis <> -1: # projected or arbitrary coordinate
	    isXY = True
        elif latAxis <> -1 and lonAxis <> -1: # lat, lon
            isLatLon = True
        else: #not supported
            raise Exception("The input netcdf files should have 'x','y' or 'lat', 'lon' axis")



        for i in range(1, len(self.vars)):      
            curLatAxis = -1 
            curLonAxis = -1
            curXAxis = -1
            curYAxis = -1
            curTimeAxis = -1   
            curnTime = 0

            numOfAxis = len(self.vars[i].var.shape)
            for j in range(numOfAxis):
                if self.vars[i].var.getAxis(j).isLatitude():
		    curLatAxis = j
                if self.vars[i].var.getAxis(j).isLongitude():
                    curLonAxis = j
                if self.vars[i].var.getAxis(j).id == 'x' or self.vars[i].var.getAxis(j).id == 'X':
                    curXAxis = j
                if self.vars[i].var.getAxis(j).id == 'y' or self.vars[i].var.getAxis(j).id == 'Y':
                    curYAxis = j
                if self.vars[i].var.getAxis(j).isTime():
                    curTimeAxis = j
                    curnTime = self.vars[i].var.getAxis(j).shape[0]


            if curTimeAxis <> timeAxis:
                raise Exception("The time axis of different input variables do not match.")


            if curnTime <> ntime:
		raise Exception("The time axis of different input variables do not match.")

            if curXAxis <> xAxis or curYAxis <> yAxis: # projected or arbitrary coordinates
	        raise Exception("The x or y axis of different input variables do not match.")

            if curLatAxis <> latAxis and curLonAxis <> lonAxis: # lat, lon
                 raise Exception("The latitude and longitude axis of different input variables do not match.")




        if isXY == True: # if curvilinear grid 
            #extentTop = sys.float_info.min
            extentTop = -999999999
            extentBottom = sys.float_info.max
            extentLeft = sys.float_info.max
	    extentRight = sys.float_info.min
     

            interXs = []
            interYs = []
            minXs = []
            minYs = []
            maxXs = []
            maxYs = []
            nys = []
            nxs = []
            firstXs = []
            firstYs = []
  
            for i in range(len(self.vars)):
                nx = self.vars[i].var.getAxis(xAxis).shape[0]
	        firstX = self.vars[i].var.getAxis(xAxis)[0]
                lastX = self.vars[i].var.getAxis(xAxis)[nx-1]  
                interXs.append(self.vars[i].var.getAxis(xAxis)[1] - self.vars[i].var.getAxis(xAxis)[0])
                if firstX > lastX:
                    maxX = firstX
                    minX = lastX
                else:
                    maxX = lastX
                    minX = firstX
                if maxX > extentRight:
                    extentRight = maxX
                if minX < extentLeft:
                    extentLeft = minX     
                maxXs.append(maxX)
                minXs.append(minX) 
                nxs.append(nx)   
                firstXs.append(firstX)

                ny = self.vars[i].var.getAxis(yAxis).shape[0]
	        firstY = self.vars[i].var.getAxis(yAxis)[0]
	        lastY = self.vars[i].var.getAxis(yAxis)[ny-1]
                interYs.append(self.vars[i].var.getAxis(yAxis)[1] - self.vars[i].var.getAxis(yAxis)[0])
	        if firstY > lastY:
		    maxY = firstY
	            minY = lastY
	        else:
		    maxY = lastY
		    minY = firstY

   
              

                if minY < extentBottom:
		    extentBottom = minY
                if maxY > extentTop:
		    extentTop = maxY
     
                minYs.append(minY)
                maxYs.append(maxY)
                nys.append(ny)
                firstYs.append(firstY)


            # calculate the bounding box of the output variable

            interY = abs(interYs[0])
            interX = abs(interXs[0])
            
            for i in range(1, len(self.vars)):
                if abs(interYs[i]) <> interY or abs(interXs[i]) <> interX:
                    raise Exception("The grid intervals of different input variables do not match.")
                    break

            ny = int((extentTop - extentBottom) / interY) + 1
            nx = int((extentRight - extentLeft) / interX) + 1


            if self.vars[0].var.missing_value != None:
                missing_value = self.vars[0].var.missing_value
            else:
                missing_value = -9999.0

            lat = MV2.ones((ny, nx)) * missing_value
            lon = MV2.ones((ny, nx)) * missing_value

            if hasTime == True:
                var = MV2.ones((ntime, ny, nx)) * missing_value  # initialize the result var
  
                for k in range(len(self.vars)):

                    tmpvar = MV2.ones((ntime, ny, nx)) * missing_value  # initialize the result var
            
                    print interYs[k] 
                    print interXs[k]

                    if interYs[k] > 0 and interXs[k] > 0:  
                        rowstart = int((firstYs[k] - extentBottom)/interYs[k])
                        colstart = int((firstXs[k] - extentLeft)/interXs[k])               
                        rowend = rowstart + nys[k]
                        colend = colstart + nxs[k]
                       
                        tmpvar[:, rowstart:rowend, colstart:colend] = self.vars[k].var
                        lat[rowstart:rowend, colstart:colend] = self.vars[k].var.getLatitude()
                        lon[rowstart:rowend, colstart:colend] = self.vars[k].var.getLongitude()

                    elif interYs[k] < 0 and interXs[k] < 0:
                        rowstart = -int((firstYs[k] - extentBottom)/interYs[k])
                        colstart = -int((firstXs[k] - extentLeft)/interXs[k])
                        rowend = rowstart - nys[k]
                        colend = colstart - nxs[k]
    
                        if rowend < 0 and colend < 0:
                            tmpvar[:, rowstart::-1, colstart::-1] = self.vars[k].var
                            lat[rowstart::-1, colstart::-1] = self.vars[k].var.getLatitude()
                            lon[rowstart::-1, colstart::-1] = self.vars[k].var.getLongitude()
                        elif rowend > 0 and colend < 0:
                            tmpvar[:, rowstart:rowend:-1, colstart::-1] = self.vars[k].var
                            lat[rowstart:rowend:-1, colstart::-1] = self.vars[k].var.getLatitude()
                            lon[rowstart:rowend:-1, colstart::-1] = self.vars[k].var.getLongitude()
                        elif rowend < 0 and colend > 0:
                            tmpvar[:, rowstart::-1, colstart:colend:-1] = self.vars[k].var
                            lat[rowstart::-1, colstart:colend:-1] = self.vars[k].var.getLatitude()
                            lon[rowstart::-1, colstart:colend:-1] = self.vars[k].var.getLongitude()
                        else:
                            tmpvar[:, rowstart:rowend:-1, colstart:colend:-1] = self.vars[k].var
                            lat[rowstart:rowend:-1, colstart:colend:-1] = self.vars[k].var.getLatitude()
                            lon[rowstart:rowend:-1, colstart:colend:-1] = self.vars[k].var.getLongitude()
       
 
                    elif interYs[k] > 0 and interXs[k] < 0:
                        rowstart = int((firstYs[k] - extentBottom)/interYs[k])
                        colstart = -int((firstXs[k] - extentLeft)/interXs[k])
                        rowend = rowstart + nys[k]
                        colend = colstart - nxs[k]


                        if colend > 0:
                            tmpvar[:, rowstart:rowend, colstart:colend:-1] = self.vars[k].var
                            lat[rowstart:rowend, colstart:colend:-1] = self.vars[k].var.getLatitude()
                            lon[rowstart:rowend, colstart:colend:-1] = self.vars[k].var.getLongitude()
                        else:
                            tmpvar[:, rowstart:rowend, colstart::-1] = self.vars[k].var
                            lat[rowstart:rowend, colstart::-1] = self.vars[k].var.getLatitude()
                            lon[rowstart:rowend, colstart::-1] = self.vars[k].var.getLongitude()


                    else:
                        rowstart = -int((firstYs[k] - extentBottom)/interYs[k])
                        colstart = int((firstXs[k] - extentLeft)/interXs[k]) 
                        rowend = rowstart - nys[k] 
                        colend = colstart + nxs[k]


                        print rowstart
                        print rowend
                        print colstart
                        print colend
                        print self.vars[k].var.shape
                        print tmpvar.shape
                        

                        print self.vars[k].var.shape
                        if rowend > 0:
                            print tmpvar[:,rowstart:rowend:-1, colstart:colend].shape                        

                            tmpvar[:,rowstart:rowend:-1, colstart:colend] = self.vars[k].var

                            lat[rowstart:rowend:-1, colstart:colend] = self.vars[k].var.getLatitude()
                            lon[rowstart:rowend:-1, colstart:colend] = self.vars[k].var.getLongitude()
                        else:
                            print tmpvar[:,rowstart::-1, colstart:colend].shape    
                            tmpvar[:,rowstart::-1, colstart:colend] = self.vars[k].var
                            lat[rowstart::-1, colstart:colend] = self.vars[k].var.getLatitude()
                            lon[rowstart::-1, colstart:colend] = self.vars[k].var.getLongitude()

                    #print self.vars[k].var
                    #print tmpvar
                    #MV2.masked_less(tmpvar, 0)
                    #print tmpvar
                    tmpvar.mask = None
                    var = MV2.where((tmpvar<>missing_value), tmpvar, var)
                    MV2.masked_equal(var, missing_value)
      
		
            else:
                var = MV2.ones((ny, nx)) * missing_value  # initialize the result var

               
                for k in range(len(self.vars)):

                    tmpvar = MV2.ones((ny, nx)) * missing_value  # initialize the result var
            
                    print interYs[k] 
                    print interXs[k]

                    if interYs[k] > 0 and interXs[k] > 0:  
                        rowstart = int((firstYs[k] - extentBottom)/interYs[k])
                        colstart = int((firstXs[k] - extentLeft)/interXs[k])               
                        rowend = rowstart + nys[k]
                        colend = colstart + nxs[k]
                       
                        tmpvar[rowstart:rowend, colstart:colend] = self.vars[k].var
                        lat[rowstart:rowend, colstart:colend] = self.vars[k].var.getLatitude()
                        lon[rowstart:rowend, colstart:colend] = self.vars[k].var.getLongitude()

                    elif interYs[k] < 0 and interXs[k] < 0:
                        rowstart = -int((firstYs[k] - extentBottom)/interYs[k])
                        colstart = -int((firstXs[k] - extentLeft)/interXs[k])
                        rowend = rowstart - nys[k]
                        colend = colstart - nxs[k]
    
                        if rowend < 0 and colend < 0:
                            tmpvar[rowstart::-1, colstart::-1] = self.vars[k].var
                            lat[rowstart::-1, colstart::-1] = self.vars[k].var.getLatitude()
                            lon[rowstart::-1, colstart::-1] = self.vars[k].var.getLongitude()
                        elif rowend > 0 and colend < 0:
                            tmpvar[rowstart:rowend:-1, colstart::-1] = self.vars[k].var
                            lat[rowstart:rowend:-1, colstart::-1] = self.vars[k].var.getLatitude()
                            lon[rowstart:rowend:-1, colstart::-1] = self.vars[k].var.getLongitude()
                        elif rowend < 0 and colend > 0:
                            tmpvar[rowstart::-1, colstart:colend:-1] = self.vars[k].var
                            lat[rowstart::-1, colstart:colend:-1] = self.vars[k].var.getLatitude()
                            lon[rowstart::-1, colstart:colend:-1] = self.vars[k].var.getLongitude()
                        else:
                            tmpvar[rowstart:rowend:-1, colstart:colend:-1] = self.vars[k].var
                            lat[rowstart:rowend:-1, colstart:colend:-1] = self.vars[k].var.getLatitude()
                            lon[rowstart:rowend:-1, colstart:colend:-1] = self.vars[k].var.getLongitude()
       
 
                    elif interYs[k] > 0 and interXs[k] < 0:
                        rowstart = int((firstYs[k] - extentBottom)/interYs[k])
                        colstart = -int((firstXs[k] - extentLeft)/interXs[k])
                        rowend = rowstart + nys[k]
                        colend = colstart - nxs[k]


                        if colend > 0:
                            tmpvar[rowstart:rowend, colstart:colend:-1] = self.vars[k].var
                            lat[rowstart:rowend, colstart:colend:-1] = self.vars[k].var.getLatitude()
                            lon[rowstart:rowend, colstart:colend:-1] = self.vars[k].var.getLongitude()
                        else:
                            tmpvar[rowstart:rowend, colstart::-1] = self.vars[k].var
                            lat[rowstart:rowend, colstart::-1] = self.vars[k].var.getLatitude()
                            lon[rowstart:rowend, colstart::-1] = self.vars[k].var.getLongitude()


                    else:
                        rowstart = -int((firstYs[k] - extentBottom)/interYs[k])
                        colstart = int((firstXs[k] - extentLeft)/interXs[k]) 
                        rowend = rowstart - nys[k] 
                        colend = colstart + nxs[k]

                        if rowend > 0:
                            tmpvar[rowstart:rowend:-1, colstart:colend] = self.vars[k].var
                            lat[rowstart:rowend:-1, colstart:colend] = self.vars[k].var.getLatitude()
                            lon[rowstart:rowend:-1, colstart:colend] = self.vars[k].var.getLongitude()
                        else:
                            print tmpvar[:,rowstart::-1, colstart:colend].shape    
                            tmpvar[rowstart::-1, colstart:colend] = self.vars[k].var
                            lat[rowstart::-1, colstart:colend] = self.vars[k].var.getLatitude()
                            lon[rowstart::-1, colstart:colend] = self.vars[k].var.getLongitude()

                      
                    var = MV2.where((tmpvar<>missing_value), tmpvar, var)
      


            xs = MV2.arange(extentLeft,extentLeft + nx * interX,interX,'f') 
            xs = cdms2.createAxis(xs)
            xs.id = 'x'

            ys = MV2.arange(extentBottom, extentBottom + ny *interY, interY,'f') 
            ys = cdms2.createAxis(ys)
            ys.id = 'y'



            #MV2.masked_equal(var, missing_value)
            #MV2.masked_equal(lat, missing_value)
            #MV2.masked_equal(lon, missing_value)

     
            lat.setAxisList((ys, xs))
            lon.setAxisList((ys, xs))

            lat.id = 'lat'
            lat.units = 'degrees_north'
            lat.missing_value = missing_value
            
            lon.id = 'lon'
            lon.units = 'degrees_east'
            lon.missing_value = missing_value
          

            var.coordinates = 'lat lon'

            var.id = varid
            var.missing_value = missing_value

            if hasTime == True:
                var.setAxisList((self.vars[0].var.getAxis(timeAxis), ys, xs))
            else:                
                var.setAxisList((ys, xs))

           
            f = cdms2.open('tmp.nc', 'w')
            f.write(var)
            f.write(lat)
            f.write(lon)
            f.close()
            var = None
            lat = None
            lon = None
            f = cdms2.open('tmp.nc')
            var = f(varid)
            os.remove('tmp.nc')
          
                
        else: #if regular grid
            #extentTop = sys.float_info.min
            extentTop = -90
            extentBottom = 90

            extentLeft = sys.float_info.max
	    extentRight = sys.float_info.min
     

            interLons = []
            interLats = []
     
            nLons = []
            nLats = []
         
            lefts = []
            rights = []


            for i in range(len(self.vars)):

               # dataLon = self.vars[i].var.getAxis(lonAxis)
                nLon = self.vars[i].var.getAxis(lonAxis).shape[0]
	        firstLon = self.vars[i].var.getAxis(lonAxis)[0]
                lastLon = self.vars[i].var.getAxis(lonAxis)[nLon-1]
                
      
                if self.vars[i].var.getAxis(lonAxis)[1]  > 90 and self.vars[i].var.getAxis(lonAxis)[0]  < -90: #special case 1
                    left = lastLon
	            right = firstLon
                    interLon = 180 - self.vars[i].var.getAxis(lonAxis)[1] + self.vars[i].var.getAxis(lonAxis)[0]  + 180
	   
	        elif self.vars[i].var.getAxis(lonAxis)[0] > 90 and self.vars[i].var.getAxis(lonAxis)[1] < -90: #special case 2
                    left = firstLon
                    right = lastLon
                    interLon = 180 - self.vars[i].var.getAxis(lonAxis)[0]  +  self.vars[i].var.getAxis(lonAxis)[1] + 180

                else:
                    interLon = self.vars[i].var.getAxis(lonAxis)[1] - self.vars[i].var.getAxis(lonAxis)[0] 
		    if interLon > 0:
		        left = firstLon
		        right = lastLon
                    else:
		        left = lastLon
                        right = firstLon
                        interLon = - interLon
         
 
                lefts.append(left)
                rights.append(right)
                nLons.append(nLon)
                interLons.append(interLon)

        

                nLat = self.vars[i].var.getAxis(latAxis).shape[0]
	        firstLat = self.vars[i].var.getAxis(latAxis)[0]
	        lastLat = self.vars[i].var.getAxis(latAxis)[nLat-1]
                interLats.append(self.vars[i].var.getAxis(latAxis)[1] - self.vars[i].var.getAxis(latAxis)[0])
	        if firstLat > lastLat:
		    maxLat = firstLat
	            minLat = lastLat
	        else:
		    maxLat = lastLat
		    minLat = firstLat

                if minLat < extentBottom:
		    extentBottom = minLat
                if maxLat > extentTop:
		    extentTop = maxLat

                nLats.append(nLat)
         

            # calculate the bounding box of the output variable
            interLon = interLons[0]
            interLat = abs(interLats[0])


            for i in range(1, len(self.vars)):
                if abs(interLats[i]) <> interLat or interLons[i] <> interLon:
                    raise Exception("The grid intervals of different input variables do not match.")
                    break

                  

            if rights > lefts:
               extentLeft = min(lefts)
               extentRight = max(rights)

            else:
               for t in len(lefts):
                   if lefts[t] > 0:
                       if lefts[t] < extentLeft:
                           extentLeft = lefts[t]
               for t in len(rights):
                   if rights[t] < extentLeft:
                       if rights[t] > extentRight:
                           extentRight = rights[t]

            if (extentLeft > 0 and extentRight < 0) or (extentLeft > 0 and extentRight >0 and extentRight < extentLeft):
                rangeLeftRight = (180 - extentLeft) + (extentRight + 180)
                #nLon = int((extentRight- extentLeft) / interLon) + 1
                nLon = int(rangeLeftRight /interLon) + 1
            
            else:
                nLon = int((extentRight- extentLeft) / interLon) + 1
          

            lons = MV2.zeros(nLon)

            for k in range(nLon):
               lons[k] = extentLeft + k * interLon

               if lons[k] > 180:
                   lons[k] = -180 + (lons[k] -180)
               
           
         
            nlat = int((extentTop - extentBottom) / interLat) + 1
            

            missing_value = self.vars[0].var.missing_value
            lats = MV2.arange(extentBottom, extentBottom + nLat *interLat, interLat,'f') 


            print extentBottom 
            print extentTop

            print extentLeft
            print extentRight



            if hasTime == True:
                var = MV2.ones((ntime, nLat, nLon)) * missing_value  # initialize the result var

                i = 0
                for lat in lats:
                    j = 0
                    for lon in lons:                    
              
                        sum = np.zeros(ntime)
                        num = 0


                        for k in range(len(self.vars)):             
                            row = int((lat - self.vars[k].var.getAxis(latAxis)[0])/interLats[k])

                            #print row                            

                            for t in range(nLons[k] -1):
                                if self.vars[k].var.getAxis(lonAxis)[t] > 90 and self.vars[k].var.getAxis(lonAxis)[t+1] < -90:
                                    if lon >= self.vars[k].var.getAxis(lonAxis)[t] and lon < 180:
                                        if (lon -self.vars[k].var.getAxis(lonAxis)[t])/interLon <= 0.5:
                                            col = t
                                        else:
                                            col = t+1
                                        break
                                    if lon <= self.vars[k].var.getAxis(lonAxis)[t+1] and lon> -180:
                                        if (self.vars[k].var.getAxis(lonAxis)[t+1] - lon)/interLon < 0.5:
                                            col = t+1
                                        else:
                                            col = t
                                        break

                                if self.vars[k].var.getAxis(lonAxis)[t] < -90 and self.vars[k].var.getAxis(lonAxis)[t+1] > 90:
                                    if lon > self.vars[k].var.getAxis(lonAxis)[t+1] and lon < 180:
                                        if (lon -self.vars[k].var.getAxis(lonAxis)[t+1])/interLon <= 0.5:
                                            col = t + 1
                                        else: 
                                            col = t
                                        break
                                    if lon < self.vars[k].var.getAxis(lonAxis)[t] and lon> -180:
                                        if (self.vars[k].var.getAxis(lonAxis)[t] - lon)/interLon <= 0.5:
                                            col = t
                                        else:
                                            col = t + 1
                                        break
                                    
                                if (lon -self.vars[k].var.getAxis(lonAxis)[t]) *(lon -self.vars[k].var.getAxis(lonAxis)[t+1]) <= 0:
                                    if math.fabs(lon -self.vars[k].var.getAxis(lonAxis)[t])/interLon <= 0.5:
                                        col = t
                                    else:
                                        col = t+1
                                    break

                            #print col
      
                                    
                            if row <0 or row >= nLats[k] or col <0 or col >= nLons[k]:
                                pass
                            else:   
                                values = self.vars[k].var[:,row,col]

                                if math.fabs(values[0] - missing_value) > 1:
                                    sum += values
                                    num += 1
                                                   
                        if num <> 0:
                            var.data[:,i,j] = sum/num
                        j+=1

                    i+=1
				


            else:
                var = MV2.ones((nLat, nLon)) * missing_value  # initialize the result var

                i = 0
                for lat in lats:
                    j = 0
                    for lon in lons:

                        sum = 0
                        num = 0
                        for k in range(len(self.vars)):             
                            row = int((lat - firstLats[k])/interLats[k])                            

                            for t in range(nLons -1):
                                if self.vars[k].getAxis(lonAxis)[t] > 90 and self.vars[k].getAxis(lonAxis)[t+1] < -90:
                                    if lon >= self.vars[k].getAxis(lonAxis)[t] and lon < 180:
                                        if (lon -self.vars[k].getAxis(lonAxis)[t])/interLon <= 0.5:
                                            col = t
                                        else:
                                            col = t+1
                                        break
                                    if lon <= self.vars[k].getAxis(lonAxis)[t+1] and lon> -180:
                                        if (self.vars[k].getAxis(lonAxis)[t+1] - lon)/interLon < 0.5:
                                            col = t+1
                                        else:
                                            col = t
                                        break

                                if self.vars[k].getAxis(lonAxis)[t] < -90 and self.vars[k].getAxis(lonAxis)[t+1] > 90:
                                    if lon > self.vars[k].getAxis(lonAxis)[t+1] and lon < 180:
                                        if (lon -self.vars[k].getAxis(lonAxis)[t+1])/interLon <= 0.5:
                                            col = t + 1
                                        else: 
                                            col = t
                                        break
                                    if lon < self.vars[k].getAxis(lonAxis)[t] and lon> -180:
                                        if (self.vars[k].getAxis(lonAxis)[t] - lon)/interLon <= 0.5:
                                            col = t
                                        else:
                                            col = t + 1
                                        break
                                    
                                if (lon -self.vars[k].getAxis(lonAxis)[t]) *(lon -self.vars[k].getAxis(lonAxis)[t+1]) <= 0:
                                    if math.fabs(lon -self.vars[k].getAxis(lonAxis)[t])/interLon <= 0.5:
                                        col = t
                                    else:
                                        col = t+1
                                    break

                                    
                            if row <0 or row >= nLats[k] or col <0 or col >= nLons[k]:
                                pass
                            else:   
                                value = self.vars[k].var[row,col]
                                if math.fabs(value - missing_value) > 1:
                                    sum += value
                                    num += 1
                                                   
                        if num <> 0:
                            var.data[:,row,j] = sum/num
                        
                        j+=1
                    i+=1



            lats = cdms2.createAxis(lats)
            lats.id = 'lat'
            lats.units = 'degrees_north'
            lats.missing_value = missing_value
            lats.designateLatitude()
            

            lons = cdms2.createAxis(lons)
            lons.id = 'lon'
            lons.units = 'degrees_east'
            lons.missing_value = missing_value
            lats.designateLongitude()


          
            #var.coordinates = 'lat lon'

            var.id = varid
            var.missing_value = missing_value

            if hasTime == True:
                var.setAxisList((self.vars[0].var.getAxis(timeAxis), lats, lons))
            else:                
                var.setAxisList((lats, lons))



        self.outvar = CDMSVariable(filename=None,name=varid)
        self.outvar.var = var
        self.outvar.var.missing_value = missing_value
        self.outvar.var.id = varid

        self.setResult("output_var", self.outvar)



_modules = [(GetDaymetTileList,	{'namespace':'data', 'name':'GetDaymetTileList'}),
(DownloadDaymetTiles, 		{'namespace':'data', 'name':'DownloadDaymetTiles'}),
(UnitConvertor, 			{'namespace':'processing', 'name':'UnitConvertor'}),
(Mosaic,				{'namespace':'processing', 'name':'Mosaic'}),
(Regrid,				{'namespace':'processing', 'name':'Regrid'}),
(SpatialSubset, 			{'namespace':'processing', 'name':'SpatialSubset'}),
(SaveVariablesToFiles,		{'namespace':'data', 'name':'SaveVariablesToFiles'}),
(ReadMultipleVariables,		{'namespace':'data', 'name':'ReadMultipleVariables'}),
(Statistics, 			{'namespace':'analysis', 'name':'Statistics'}),
(StatisticsAlongTemporalAxis, 	{'namespace':'analysis', 'name':'StatisticsAlongTemporalAxis'}),
(StatisticsAlongSpatialAxis,	{'namespace':'analysis', 'name':'StatisticsAlongSpatialAxis'}),
(TemporalAggregation, 		{'namespace':'analysis', 'name':'TemporalAggregation'}), 
(LongTermTemporalMean, 		{'namespace':'analysis', 'name':'LongTermTemporalMean'}),
(GetMatrixFromVariables, 		{'namespace':'data', 'name':'GetMatrixFromVariables'}), 
(Matrix,                {'namespace':'data', 'name':'Matrix'}),
#(ConfigReader,          {'namespace':'data', 'name':'ConfigReader'}),#
#(WriteVarsIntoDataFile, {'namespace':'data', 'name':'WriteVarsIntoDataFile'}),#
(ReadMatrixFromFile,	{'namespace':'data', 'name':'ReadMatrixFromFile'}),    
(SeriesPlot,            {'namespace':'visualization','name':'SeriesPlot'}),
(Dendrogram,            {'namespace':'visualization', 'name':'Dendrogram'}),
(TaylorDiagram,         {'namespace':'visualization', 'name':'TaylorDiagram'}),
(ParallelCoordinates,   {'namespace':'visualization', 'name':'ParallelCoordinates'}),
(BarChart,   		{'namespace':'visualization', 'name':'BarChart'}),
(HeatMap,   		{'namespace':'visualization', 'name':'HeatMap'}),
(Coordinator, 		{'namespace':'visualization', 'name':'Coordinator'})
]







#reg = get_module_registry()
#reg.add_module(Coordinator)
#reg.add_output_port(Coordinator, "self", Coordinator)


    
