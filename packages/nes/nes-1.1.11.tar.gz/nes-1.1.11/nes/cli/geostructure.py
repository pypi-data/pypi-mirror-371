"""
NES CLI Utility: Convert NetCDF to geospatial vector format (Shapefile, GeoJSON)

This script defines a function `nc2geostructure` that extracts a selected time step and level
from a NetCDF file and writes the corresponding geospatial structure as a shapefile,
optionally filtering specific variables.

Intended to be used as part of a CLI interface (e.g. via `nes geostructure`).
"""

from nes import open_netcdf

def nc2geostructure(input_file: str, output_file: str, var_list: list=None, time_step:int=0, level:int=0):
    """
    Extracts geospatial data from a NetCDF file and writes it as a shapefile.

    Parameters
    ----------
    input_file : str
        Path to the source NetCDF file.
    output_file : str
        Path where the output shapefile will be written.
    var_list : list, optional
        List of variable names to include in the shapefile. If None, all variables are used.
    time_step : int, default=0
        Index of the time step to extract.
    level : int, default=0
        Index of the vertical level to extract.

    Returns
    -------
    None
    """
    # Open the NetCDF file using NES
    nessy = open_netcdf(input_file)

    # If no variable list is provided, use all available variables in the file
    if var_list is None:
        var_list = nessy.variables.keys()

    # Select the desired time step and vertical level for extraction
    nessy.sel(
        time_min=nessy.time[time_step],  # Minimum time index to extract
        time_max=nessy.time[time_step],  # Maximum time index to extract (same as min for single step)
        lev_min=level,                 # Minimum vertical level to extract
        lev_max=level                  # Maximum vertical level to extract (same as min for single level)
    )

    # Filter to keep only the specified variables and load the data into memory
    nessy.keep_vars(var_list)
    nessy.load()

    # Create the base geospatial structure (shapefile) and attach the selected variables
    nessy.create_shapefile()
    nessy.add_variables_to_shapefile(idx_time=0, idx_lev=0, var_list=var_list)

    # Write the geospatial structure to the output shapefile
    nessy.write_shapefile(output_file)

    return None
