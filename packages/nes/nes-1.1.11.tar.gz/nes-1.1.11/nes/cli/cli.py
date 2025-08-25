import traceback
from mpi4py import MPI
from configargparse import ArgParser
import argcomplete


def _add_nc2geostructure_subparser(subparsers):
    """
    Add the 'geostructure' subcommand to the NES CLI.

    This command extracts geospatial features from a NetCDF file and saves them as a geostructure.

    Parameters
    ----------
    subparsers : argparse._SubParsersAction
        The subparsers object returned by `add_subparsers()` on the main parser.
    """
    from nes.cli import nc2geostructure

    # TODO: TEST
    geo_parser = subparsers.add_parser("nc2geostructure", help="Convert NetCDF to geospatial structure (GeoJSON, shapefile) (TESTING PHASE)")
    geo_parser.add_argument("-i", "--input_file", required=True, help="Path to input NetCDF file")
    geo_parser.add_argument("-o", "--output_file", required=True, help="Path to output geostructure")
    geo_parser.add_argument(
        "--var-list", nargs="+",
        help="List of variable names to include in the geostructure. If omitted, all variables will be included."
    )
    geo_parser.add_argument("--time-step", type=int, default=0, help="Time step index to extract (default: 0)")
    geo_parser.add_argument("--level", type=int, default=0, help="Vertical level index to extract (default: 0)")
    geo_parser.set_defaults(func=nc2geostructure)


def _add_interpolate_subparser(subparsers):
    """
    Add the 'interpolate' subcommand to the NES CLI.

    Parameters
    ----------
    subparsers : argparse._SubParsersAction
        The subparsers object returned by `add_subparsers()` on the main parser.

    This subcommand supports interpolation of NetCDF data along either horizontal or vertical axes.
    Destination grid can be loaded from a file or created from projection parameters.
    """
    from nes.cli import interpolate

    # TODO: TEST
    interp_parser = subparsers.add_parser("interpolate", help="Interpolate data onto a different grid (TESTING PHASE)")

    # Main input/output
    general = interp_parser.add_argument_group("General options")
    general.add_argument("-i", "--input_file", required=True, help="Path to source NetCDF file")
    general.add_argument("-o", "--output_file", help="Path to output NetCDF file")
    general.add_argument("--axis", choices=["horizontal", "vertical"], default="horizontal",
                         help="Interpolation axis (default: horizontal)")

    dst_group = general.add_mutually_exclusive_group(required=True)
    dst_group.add_argument("-d", "--destination", help="Path to destination grid NetCDF file")
    dst_group.add_argument("--projection", help="Projection type to generate destination grid (e.g. regular, rotated, lcc)")

    # Horizontal interpolation options
    horizontal = interp_parser.add_argument_group("Horizontal interpolation options")
    horizontal.add_argument("--kind", choices=["NearestNeighbour", "Conservative"],
                            help="Interpolation method for horizontal axis")
    horizontal.add_argument("--n-neighbours", type=int, help="Number of neighbors (NearestNeighbour)")
    horizontal.add_argument("--flux", action="store_true", help="Treat variables as fluxes (Conservative only)")
    horizontal.add_argument("--keep-nan", action="store_true", help="Keep NaN values after interpolation")
    horizontal.add_argument("--fix-border", action="store_true", help="Fix border effects (NearestNeighbour only)")
    horizontal.add_argument("--weight-matrix-path", help="Path to weight matrix file")
    horizontal.add_argument("--only-create-wm", action="store_true", help="Only generate weight matrix")
    horizontal.add_argument("--to-providentia", action="store_true", help="Format output for Providentia")

    # Vertical interpolation options
    vertical = interp_parser.add_argument_group("Vertical interpolation options")
    vertical.add_argument("--method", help="Interpolation method for vertical axis (e.g. linear)")
    vertical.add_argument("--extrapolate", action="store_true", help="Allow extrapolation in vertical interpolation")

    # Grid creation arguments
    grid = interp_parser.add_argument_group("Grid creation options (for --projection)")
    grid.add_argument("--lat_orig", type=float, help="Latitude origin (regular/global)")
    grid.add_argument("--lon_orig", type=float, help="Longitude origin (regular/global)")
    grid.add_argument("--inc_lat", type=float, help="Latitude increment (regular/global)")
    grid.add_argument("--inc_lon", type=float, help="Longitude increment (regular/global)")
    grid.add_argument("--n_lat", type=int, help="Number of latitude points (regular/global)")
    grid.add_argument("--n_lon", type=int, help="Number of longitude points (regular/global)")

    grid.add_argument("--centre_lat", type=float, help="Rotated pole latitude (rotated)")
    grid.add_argument("--centre_lon", type=float, help="Rotated pole longitude (rotated)")
    grid.add_argument("--west_boundary", type=float, help="Western boundary (rotated)")
    grid.add_argument("--south_boundary", type=float, help="Southern boundary (rotated)")
    grid.add_argument("--inc_rlat", type=float, help="Latitude increment (rotated)")
    grid.add_argument("--inc_rlon", type=float, help="Longitude increment (rotated)")

    grid.add_argument("--parent_grid_path", help="Path to parent grid NetCDF (rotated_nested)")
    grid.add_argument("--parent_ratio", type=int, help="Parent ratio (rotated_nested)")
    grid.add_argument("--i_parent_start", type=int, help="Parent grid i index start (rotated_nested)")
    grid.add_argument("--j_parent_start", type=int, help="Parent grid j index start (rotated_nested)")
    grid.add_argument("--n_rlat", type=int, help="Number of lat points (rotated_nested)")
    grid.add_argument("--n_rlon", type=int, help="Number of lon points (rotated_nested)")

    grid.add_argument("--lat_1", type=float, help="First standard parallel (LCC projection)")
    grid.add_argument("--lat_2", type=float, help="Second standard parallel (LCC projection)")
    grid.add_argument("--lon_0", type=float, help="Central meridian (LCC projection)")
    grid.add_argument("--x_0", type=float, help="False easting (LCC projection)")
    grid.add_argument("--y_0", type=float, help="False northing (LCC projection)")
    grid.add_argument("--dx", type=float, help="Grid spacing in x direction (LCC projection)")
    grid.add_argument("--dy", type=float, help="Grid spacing in y direction (LCC projection)")
    grid.add_argument("--nx", type=int, help="Number of grid points in x (LCC projection)")
    grid.add_argument("--ny", type=int, help="Number of grid points in y (LCC projection)")

    grid.add_argument("--lat_ts", type=float, help="Latitude of true scale (Mercator projection)")

    interp_parser.set_defaults(func=interpolate)


def _add_check_subparser(subparsers):
    """
    Add the 'check' subcommand to the NES CLI.

    Parameters
    ----------
    subparsers : argparse._SubParsersAction
        The subparsers object returned by `add_subparsers()` on the main parser.

    This subcommand checks for the presence of NaN and Inf values in a NetCDF file.
    """
    from nes.cli import run_checks

    check_parser = subparsers.add_parser("check", help="Run checks on a NetCDF file")
    check_parser.add_argument("-i", "--input_file", required=True, help="Input NetCDF file path")
    check_parser.add_argument("--nan", dest="check_nan", action="store_true", help="Check for NaN values")
    check_parser.add_argument("--no-nan", dest="check_nan", action="store_false", help="Do not check NaN values")
    check_parser.add_argument("--inf", dest="check_inf", action="store_true", help="Check for Inf values")
    check_parser.add_argument("--no-inf", dest="check_inf", action="store_false", help="Do not check Inf values")
    check_parser.set_defaults(check_nan=True, check_inf=True)
    check_parser.set_defaults(func=run_checks)


def _add_reorder_subparser(subparsers):
    """
    Add the 'reorder' subcommand to the NES CLI.

    Parameters
    ----------
    subparsers : argparse._SubParsersAction
        The subparsers object returned by `add_subparsers()` on the main parser.

    This subcommand reorders longitudes in a NetCDF file to ensure standard representation.
    """
    from nes.cli import reorder_longitudes

    # TODO: Add support for parallel version
    reorder_parser = subparsers.add_parser("reorder", help="Reorder longitudes in a NetCDF file (ONLY SERIAL)")
    reorder_parser.add_argument("-i", "--input_file", required=True, help="Input NetCDF file path")
    reorder_parser.add_argument("-o", "--output_file", help="Output NetCDF file path")
    reorder_parser.set_defaults(func=reorder_longitudes)


def _filter_args(func, args_namespace):
    """
    Filters arguments from argparse to only include those relevant to the target function.

    Parameters
    ----------
    func : Callable
        The function to match arguments against.
    args_namespace : argparse.Namespace
        The full set of parsed CLI arguments.

    Returns
    -------
    dict
        A dictionary containing only the arguments accepted by the function.
    """
    import inspect
    sig = inspect.signature(func)
    arg_keys = set(sig.parameters.keys())
    args_dict = vars(args_namespace)
    filtered = {k: args_dict[k] for k in arg_keys if k in args_dict}

    return filtered


def main():
    """
    Main entry point for the NES command-line interface.

    Sets up the available subcommands, parses user input from the CLI,
    and dispatches execution to the appropriate subcommand handler.
    """
    parser = ArgParser(
        description="NES - NetCDF for Earth Science utilities",
        default_config_files=['~/.nes_config']
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Add subcommands
    _add_nc2geostructure_subparser(subparsers)
    _add_check_subparser(subparsers)
    _add_reorder_subparser(subparsers)
    _add_interpolate_subparser(subparsers)

    # Enable autocomplete
    argcomplete.autocomplete(parser)

    args = parser.parse_args()

    try:
        filtered_args = _filter_args(args.func, args)
        args.func(**filtered_args)
    except Exception as e:
        print(f"Process {MPI.COMM_WORLD.Get_rank()}: NES critical error detected {e}, aborting MPI.", flush=True)
        print(f"Process {MPI.COMM_WORLD.Get_rank()}: Traceback:\n{traceback.format_exc()}", flush=True)

        MPI.COMM_WORLD.Abort(1)

    return