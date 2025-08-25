from nes.load_nes import open_netcdf
from mpi4py import MPI


def reorder_longitudes(input_file: str, output_file: str):
    """
    Convert longitudes in a NetCDF file to the [-180, 180] range and save the modified file.

    Parameters
    ----------
    input_file : str
        Path to the input NetCDF file.
    outfile : str
        Path where the reordered NetCDF file will be saved.

    Raises
    ------
    ValueError
        If the script is run using more than one MPI process.

    Notes
    -----
    This function must be executed in serial mode only.
    It uses `convert_longitudes()` from the NES API, which updates coordinate values
    and ensures variables depending on longitude are shifted accordingly.
    """
    # Enforce serial execution (1 MPI process)
    comm = MPI.COMM_WORLD
    if comm.Get_size() > 1:
        raise ValueError("This script must be run with a single process (serial mode only).")

    # Open the input NetCDF file
    nc = open_netcdf(input_file)

    # Load data into memory
    nc.load()

    # Reorder longitudes from [0, 360] to [-180, 180]
    nc.convert_longitudes()

    # Save the result to the output path
    nc.to_netcdf(outfile)

    return True