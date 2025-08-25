
"""
DGGRID to Geographic Coordinate Conversion Module

This module provides functionality to convert DGGRID cell IDs to geographic coordinates
and various geometric representations. DGGRID is a Discrete Global Grid System
implementation that supports multiple DGGS types.

The module includes functions to:
- Convert DGGRID cell IDs to Shapely Polygon objects
- Convert DGGRID cell IDs to GeoJSON FeatureCollection format
- Provide command-line interfaces for both conversion types

Key Functions:
    dggrid2geo: Convert DGGRID cell IDs to Shapely Polygons
    dggrid2geojson: Convert DGGRID cell IDs to GeoJSON FeatureCollection
    dggrid2geo_cli: Command-line interface for polygon conversion
    dggrid2geojson_cli: Command-line interface for GeoJSON conversion
"""

import json
import argparse

from dggrid4py import DGGRIDv7, dggs_types
from dggrid4py import tool
from vgrid.utils.geometry import geodesic_dggs_to_feature

def dggrid2geo(dggrid_instance, dggrid_ids, dggs_type, resolution):
    """
    Convert a list of DGGRID cell IDs to Shapely geometry objects.
    Accepts a single dggrid_id (string/int) or a list of dggrid_ids.
    Skips invalid or error-prone cells.
    Returns a list of Shapely Polygon objects, or a single Polygon if only one input.
    """
    if isinstance(dggrid_ids, (str, int)):
        dggrid_ids = [dggrid_ids]
            
    dggrid_cells = dggrid_instance.grid_cell_polygons_from_cellids(
                dggrid_ids, dggs_type, resolution, split_dateline=True
            )    
   
    return dggrid_cells

def dggrid2geo_cli():
    """
    Command-line interface for dggrid2geo supporting multiple DGGRID cell IDs.
    """
    parser = argparse.ArgumentParser(
        description="Convert DGGRID cell ID(s) to Shapely Polygons. \
                                     Usage: dggrid2geo <SEQNUM> <dggs_type> <res>. \
                                     Ex: dggrid2geo 783229476878 ISEA7H 13"
    )
    parser.add_argument(
        "dggrid",
        nargs="+",
        help="Input DGGRID cell ID(s) in SEQNUM format"
    )
    parser.add_argument(
        "type",
        choices=dggs_types,
        help="Select a DGGS type from the available options.",
    )
    parser.add_argument("res", type=int, help="resolution")

    args = parser.parse_args()
    dggrid_exec = tool.get_portable_executable(".")
    dggrid_instance = DGGRIDv7(executable=dggrid_exec, working_dir='.', capture_logs=False, silent=True, has_gdal=False, tmp_geo_out_legacy=True, debug=False)
    polys = dggrid2geo(dggrid_instance, args.dggrid, args.type, args.res)
    return polys

def dggrid2geojson(dggrid_instance, dggrid_ids, dggs_type, resolution):
    """
    Convert a list of DGGRID cell IDs to a GeoJSON FeatureCollection.
    Accepts a single dggrid_id (string/int) or a list of dggrid_ids.
    Skips invalid or error-prone cells.
    """
    if isinstance(dggrid_ids, (str, int)):
        dggrid_ids = [dggrid_ids]
    
    # Get the GeoDataFrame from dggrid2geo
    gdf = dggrid2geo(dggrid_instance, dggrid_ids, dggs_type, resolution)
    
    # Convert GeoDataFrame to GeoJSON dictionary
    geojson_dict = json.loads(gdf.to_json())
    
    return geojson_dict


def dggrid2geojson_cli():
    """
    Command-line interface for dggrid2geojson supporting multiple DGGRID cell IDs.
    """
    parser = argparse.ArgumentParser(
        description="Convert DGGRID cell ID(s) to GeoJSON. \
                                     Usage: dggrid2geojson <SEQNUM> <dggs_type> <res>. \
                                     Ex: dggrid2geojson 783229476878 ISEA7H 13"
    )
    parser.add_argument(
        "dggrid",
        nargs="+",
        help="Input DGGRID cell ID(s) in SEQNUM format"
    )
    parser.add_argument(
        "type",
        choices=dggs_types,
        help="Select a DGGS type from the available options.",
    )
    parser.add_argument("res", type=int, help="resolution")

    args = parser.parse_args()
    dggrid_exec = tool.get_portable_executable(".")
    dggrid_instance = DGGRIDv7(executable=dggrid_exec, working_dir='.', capture_logs=False, silent=True, has_gdal=False, tmp_geo_out_legacy=True, debug=False)
    geojson_data = json.dumps(dggrid2geojson(dggrid_instance, args.dggrid, args.type, args.res))
    print(geojson_data)

if __name__ == "__main__":
    dggrid2geojson_cli()