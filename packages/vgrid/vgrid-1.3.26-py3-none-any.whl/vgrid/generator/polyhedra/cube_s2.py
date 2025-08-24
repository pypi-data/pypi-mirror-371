"""
Cube S2 Grid Generator Module.
This module provides functionality to generate S2 cube.
Reference:
    https://github.com/aaliddell/s2cell,
    https://medium.com/@claude.ducharme/selecting-a-geo-representation-81afeaf3bf01
    https://github.com/sidewalklabs/s2
    https://github.com/google/s2geometry/tree/master/src/python
    https://github.com/google/s2geometry
    https://gis.stackexchange.com/questions/293716/creating-shapefile-of-s2-cells-for-given-level
    https://s2.readthedocs.io/en/latest/quickstart.html
"""

import json
import geopandas as gpd
from tqdm import tqdm
from shapely.geometry import mapping
from vgrid.conversion.dggs2geo.s22geo import s22geo
from vgrid.dggs import s2

def cube_s2(level=0):
    """
    Generate S2 cube faces as GeoDataFrame.
    
    Args:
        level (int): S2 resolution level (0-30, default: 0)
    
    Returns:
        geopandas.GeoDataFrame: GeoDataFrame containing S2 cell geometries
    """
    # Define the cell level (S2 uses a level system for zoom, where level 30 is the highest resolution)
    # Create a list to store the S2 cell IDs
    cell_ids = []

    # Define the cell covering
    coverer = s2.RegionCoverer()
    coverer.min_level = level
    coverer.max_level = level
    # coverer.max_cells = 1_000_000  # Adjust as needed

    # Define the region to cover (in this example, we'll use the entire world)
    region = s2.LatLngRect(
        s2.LatLng.from_degrees(-90, -180), s2.LatLng.from_degrees(90, 180)
    )

    # Get the covering cells
    covering = coverer.get_covering(region)

    # Convert the covering cells to S2 cell IDs
    for cell_id in covering:
        cell_ids.append(cell_id)

    # Create lists to store geometries and properties
    geometries = []
    s2_tokens = []
    
    for cell_id in tqdm(cell_ids, desc="Processing cells"):
        # Generate a Shapely Polygon
        polygon = s22geo(cell_id)
        
        # Store geometry and S2 token
        geometries.append(polygon)
        s2_tokens.append(cell_id.to_token())

    # Create GeoDataFrame
    gdf = gpd.GeoDataFrame(
        {"cell_id": s2_tokens},
        geometry=geometries,
        crs="EPSG:4326"
    )
    
    return gdf


def cube_s2_cli():
    """Command-line interface to generate and save S2 cube faces as GeoJSON."""
    gdf = cube_s2()
    
    # Define the GeoJSON file path
    geojson_path = "cube.geojson"
    
    # Save GeoDataFrame as GeoJSON
    gdf.to_file(geojson_path, driver="GeoJSON")

    print(f"Cube saved as {geojson_path}")


if __name__ == "__main__":
    cube_s2_cli()
