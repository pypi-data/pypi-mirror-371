============
CHANGELOG
============

.. start-here

1.1.11
============

* Release date: 2025/07/07
* Changes and new features:

  * New Command Line Interface nes with:

    * nes nc2geostructure
    * nes check
    * nes reorder
    * nes interpolate

1.1.10
============

* Release date: 2025/07/03
* Changes and new features:

  * Expand & Contract
  * Bugfix on Coordinates metadata conventions.
  * New entry point to check NaN and Inf values: `nes_check`

1.1.9
============

* Release date: 2025/04/22
* Changes and new features:

  * Add additional names for the time variable
  * Added MOCAGE format
  * Bugfix on vertical interpolation.
  * Selecting function allows now to select negative latitudes on 0-360 ones.
  * Reorder functionality (0 360 to -180 180) as entry point
  * Coordinates metadata conventions.


1.1.8
============

* Release date: 2024/10/07
* Changes and new features:

  * Update installation instructions
  * Rename project from NES to nes


1.1.7.post2
============

* Release date: 2024/10/02
* Changes and new features:

  * Remove mpich requirement

1.1.7.post1
============

* Release date: 2024/09/27
* Changes and new features:

  * Remove import errors on installation using pip


1.1.7
============

* Release date: 2024/09/25
* Changes and new features:

  * Final setup to upload package to PyPI


1.1.6
============

* Release date: 2024/09/25
* Changes and new features:

  * Tests to upload package to PyPI


1.1.5
============

* Release date: 2024/09/20
* Changes and new features:

  * to_netcdf function changes the type argument to nc_type
  * Memory usage optimization
  * Bugfixes

1.1.4
============

* Release date: 2024/05/31
* Changes and new features:

  * Statistics:

    * Rolling mean

  * Documentation
  * Removed negative values on the horizontal interpolation due to unmapped NaNs values.
  * Improved load_nes.py removing redundant code
  * Direct access to variable data. (`#77 <https://earth.bsc.es/gitlab/es/nes/-/issues/77>`_)
  * New functionalities for vertical extrapolation. (`#74 <https://earth.bsc.es/gitlab/es/nes/-/issues/74>`_)
  * Removed cfunits and psutil dependencies.
  * Updated the requirements and environment.yml for the Conda environment created in MN5 (`#78 <https://earth.bsc.es/gitlab/es/nes/-/issues/78>`_)
  * Bugfix:

    * Vertical interpolation for descendant level values (Pressure) (`#71 <https://earth.bsc.es/gitlab/es/nes/-/issues/71>`_)
    * Removed lat-lon dimension on the NetCDF projections that not need them (`#72 <https://earth.bsc.es/gitlab/es/nes/-/issues/72>`_)
    * Fixed the bug when creating the spatial bounds after selecting a region (`#68 <https://earth.bsc.es/gitlab/es/nes/-/issues/68>`_)
    * Fixed the bug related to Shapely deprecated function TopologicalError(`#76 <https://earth.bsc.es/gitlab/es/nes/-/issues/76>`_)
    * Fixed the bug related to NumPy deprecated np.object(`#76 <https://earth.bsc.es/gitlab/es/nes/-/issues/76>`_)
    * Removed DeprecationWarnings from shapely and pyproj libraries, needed for the porting to MN5 (`#78 <https://earth.bsc.es/gitlab/es/nes/-/issues/78>`_)

1.1.3
============

* Release date: 2023/06/16
* Changes and new features:

  * Rotated nested projection
  * Improved documentation
  * New function get_fids()
  * Climatology options added
  * Milliseconds, seconds, minutes and days time units accepted
  * Option to change the time units' resolution.
  * Bugs fixing:

    * The input arguments in function new() have been corrected
    * Months to day time units fixed

1.1.2
============

* Release date: 2023/05/15
* Changes and new features:

  * Minor bug fixes
  * Tutorial updates
  * Writing formats (CMAQ, MONARCH, and WRF_CHEM added) (`#63 <https://earth.bsc.es/gitlab/es/nes/-/issues/63>`_)

1.1.1
============

* Release date: 2023/04/12
* Changes and new features:

  * Sum of Nes objects (`#48 <https://earth.bsc.es/gitlab/es/nes/-/issues/48>`_)
  * Write 2D string data to save variables from shapefiles after doing a spatial join (`#49 <https://earth.bsc.es/gitlab/es/nes/-/issues/49>`_)
  * Horizontal Interpolation Conservative: Improvement on memory usage when calculating the weight matrix (`#54 <https://earth.bsc.es/gitlab/es/nes/-/issues/54>`_)
  * Improved time on **concatenate_netcdfs** function (`#55 <https://earth.bsc.es/gitlab/es/nes/-/issues/55>`_)
  * Write by time step to avoid memory issues (`#57 <https://earth.bsc.es/gitlab/es/nes/-/issues/57>`_)
  * Flux conservative horizontal interpolation (`#60 <https://earth.bsc.es/gitlab/es/nes/-/issues/60>`_)
  * Bugs fixing:

    * Bug on `cell_methods` serial write (`#53 <https://earth.bsc.es/gitlab/es/nes/-/issues/53>`_)
    * Bug on avoid_first_hours that where not filtered after read the dimensions (`#59 <https://earth.bsc.es/gitlab/es/nes/-/issues/59>`_)
    * Bug while reading masked data.
    * grid_mapping NetCDF variable as integer instead of character.

1.1.0
============

* Release date: 2023/03/02
* Changes and new features:

  * Improve Lat-Lon to Cartesian coordinates method (used in Providentia).
  * Horizontal interpolation: Conservative
  * Function to_shapefile() to create shapefiles from a NES object without losing data from the original grid and being able to select the time and level.
  * Function from_shapefile() to create a new grid with data from a shapefile after doing a spatial join.
  * Function create_shapefile() can now be used in parallel.
  * Function calculate_grid_area() to calculate the area of each cell in a grid.
  * Function calculate_geometry_area() to calculate the area of each cell given a set of geometries.
  * Function get_spatial_bounds_mesh_format() to get the lon-lat boundaries in a mesh format (used in pcolormesh).
  * Bugs fixing:

    * Correct the dimensions of the resulting points datasets from any interpolation.
    * Amend the interpolation method to take into account the cases in which the distance among points equals zero.
    * Correct the way we retrieve the level positive value.
    * Correct how to calculate the spatial bounds of LCC and Mercator grids: the dimensions were flipped.
    * Correct how to calculate the spatial bounds for all grids: use read axis limits instead of write axis limits.
    * Calculate centroids from coordinates in the creation of shapefiles, instead of using the geopandas function 'centroid', that raises a warning for possible errors.
    * Enable selection of variables on the creation of shapefiles.
    * Correct read and write parallel limits.
    * Correct data type in the parallelization of points datasets.
    * Correct error that appear when trying to select coordinates and write the file.

1.0.0
============

* Release date: 2022/11/24
* Changes and new features:

  * First beta release
  * Open:

    * NetCDF:

      * Regular Latitude-Longitude
      * Rotated Lat-Lon
      * Lambert Conformal Conic
      * Mercator
      * Points
      * Points in GHOST format
      * Points in PROVIDENTIA format

  * Parallelization:

    * Balanced / Unbalanced
    * By time axis
    * By Y axis
    * By X axis

  * Create: 

    * NetCDF:
  
      * Regular Latitude-Longitude
      * Rotated Lat-Lon
      * Lambert Conformal Conic
      * Mercator
      * Points

    * Shapefile

  * Write:

    * NetCDF
  
      * CAMS REANALYSIS format
  
    * Grib2
    * Shapefile
  
  * Interpolation:
  
    * Vertical interpolation
    * Horizontal interpolation
  
      * Nearest Neighbours
  
    * Providentia interpolation
  
  * Statistics:
  
    * Daily_mean
    * Daily_max
    * Daily_min
    * Last time step
  
  * Methods:
  
    * Concatenate (variables of the same period in different files)
    