
Welcome to UVCDAT_IMIF Package's documentation!
================================


UVCDAT_IMIF package is a Vistrails package developed for climate model data inter-comparison.



How to use the package?

1. You need have UV-CDAT (http://uv-cdat.llnl.gov/) installed before using this package.


2. Put the uvcdat_imif folder to the .vistrails/userpackages subdirectory of your home directory. 


3. Open UV-CDAT. Open Vistrails from "Vistrails -> Builder"


4. Click on the Edit menu (or the VisTrails menu on Mac OS X), select the Preferences option and select the Module Packages tab. In the dialog, select the uvcdat_imif package, then click on Enable. This should move the package to the Enabled packages list. Close the dialog. 


5. The package should now be visible in the VisTrails builder.A list of modules are available in the package. 

Contents:

.. toctree::
   :maxdepth: 2

   Data
   	DownloadDaymetTiles
   	GetDaymetTileList
   	GetMatrixFromVariables
   	ReadMatrixFromFile
   	SaveVariablesToFiles
   	ReadMultipleVariables
   Processing
	UnitConvertor
   	Mosaic
   	Regrid
   	SpatialSubset
   Analysis
        TemporalAggregation
        LongTermTemporalMean
   	UnaryVariableStatistics
   	StatisticsAlongSpatialAxis
   	StatisticsAlongTemporalAxis
   Visualization
        SeriesPlot
   	Dendrogram
   	TaylorDiagram
   	ParallelCoordinates
  	BarChart   		
   	HeatMap   		
  	Coordinator 	





