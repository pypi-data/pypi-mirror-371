"""
DGGRID Statistics Module

This module provides functions to calculate and display statistics for DGGRID
Discrete Global Grid System (DGGS) types. It supports both command-line interface
and direct function calls.

Key Functions:
- dggrid_stats: Calculate and display statistics for a given DGGRID DGGS type and resolution
- main: Command-line interface for dggrid_stats
"""

import argparse
from dggrid4py import tool, DGGRIDv7, dggs_types

def dggridstats(dggrid_instance, dggs_type, resolution):
    """
    Calculate and display statistics for a given DGGRID DGGS type and resolution
    """
    dggrid_metrics = dggrid_instance.grid_stats_table(dggs_type, resolution)
    print(dggrid_metrics)


def dggridstats_cli():
    """
    Command-line interface for generating DGGRID DGGS statistics.
    """
    parser = argparse.ArgumentParser(description="Export or display DGGRID stats.")
    parser.add_argument(
        "-t",
        "--dggs_type",
        choices=dggs_types,
        help="Select a DGGS type from the available options.",
    )
    parser.add_argument(
        "-r", "--resolution", type=int, required=True, help="resolution"
    )
    args = parser.parse_args()

    # dggrid_instance = DGGRIDv7(
    #     executable="/usr/local/bin/dggrid",
    #     working_dir=".",
    #     capture_logs=False,
    #     silent=True,
    #     tmp_geo_out_legacy=False,
    #     debug=False,
    # )
    dggrid_exec = tool.get_portable_executable(".")
    dggrid_instance = DGGRIDv7(executable=dggrid_exec, working_dir='.', capture_logs=False, silent=True, has_gdal=False, tmp_geo_out_legacy=True, debug=False)

    dggs_type = args.dggs_type
    resolution = args.resolution
    try:
        dggridstats(dggrid_instance, dggs_type, resolution)
    except Exception:
        print(
            "Please ensure that the -r <resolution> are set appropriately, and there is an excutable DGGRID located at /usr/local/bin/dggrid. Please install DGGRID following instructions from https://github.com/sahrk/DGGRID/blob/master/INSTALL.md"
        )


if __name__ == "__main__":
    dggridstats_cli()
