from nes.load_nes import open_netcdf
from numpy import isinf, isnan


def run_checks(input_file: str, check_nan: bool = True, check_inf: bool = True):
    """
    Check for NaN and/or Inf values in all variables of a NetCDF file.

    Parameters
    ----------
    input_file : str
        Path to the input NetCDF file.
    check_nan : bool, optional
        Whether to check for NaN (Not a Number) values. Default is True.
    check_inf : bool, optional
        Whether to check for infinite (Inf) values. Default is True.

    Raises
    ------
    ValueError
        If any variable contains NaN or Inf values, a ValueError is raised
        indicating the variable name.

    Notes
    -----
    This function uses the NES `open_netcdf()` interface to load the file and
    reads all variables into memory before performing the checks.
    """
    # Open the NetCDF file with NES (metadata only)
    dataset = open_netcdf(input_file)

    # Load all variable data into memory
    dataset.load()

    # Loop over all variables in the dataset
    for var_name, var_info in dataset.variables.items():
        # Check for Inf values, if requested
        has_inf = isinf(var_info["data"]).any() if check_inf else False

        # Check for NaN values, if requested
        has_nan = isnan(var_info["data"]).any() if check_nan else False

        # Raise an error if problematic values are found
        if has_nan or has_inf:
            raise ValueError(f"Variable '{var_name}' contains NaN or Inf values.")

    return True