
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
            
    dggrid_polygons = []
    for dggrid_id in dggrid_ids:
        try:
            dggrid_cell = dggrid_instance.grid_cell_polygons_from_cellids(
                [dggrid_id], dggs_type, resolution, split_dateline=True
            )
            gdf = dggrid_cell.set_geometry("geometry")
            # Check and set CRS to EPSG:4326 if needed
            if gdf.crs is None:
                gdf.set_crs(epsg=4326, inplace=True)
            elif not gdf.crs.equals("EPSG:4326"):
                gdf = gdf.to_crs(epsg=4326)
            
            # Get the first (and should be only) polygon from the GeoDataFrame
            if not gdf.empty:
                polygon = gdf.iloc[0].geometry
                dggrid_polygons.append(polygon)
        except Exception:
            continue
    
    if len(dggrid_polygons) == 1:
        return dggrid_polygons[0]
    return dggrid_polygons

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
    
    dggrid_features = []
    for dggrid_id in dggrid_ids:
        try:
            cell_polygon = dggrid2geo(dggrid_instance, dggrid_id, dggs_type, resolution)
            # Determine number of edges based on DGGS type
            num_edges = 6  # Default for most DGGS types
            if "ISEA4" in dggs_type:
                num_edges = 4
            elif "ISEA3" in dggs_type:
                num_edges = 3
            
            dggrid_feature = geodesic_dggs_to_feature(
                "dggrid", str(dggrid_id), resolution, cell_polygon, num_edges
            )
            dggrid_features.append(dggrid_feature)
        except Exception:
            continue
    
    return {"type": "FeatureCollection", "features": dggrid_features}


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