"""
Cube Grid Generator Module.
This module provides functionality to generate cube faces for polyhedral projections.
"""

from shapely.geometry import Polygon, MultiPolygon, mapping
import json
import os
import geopandas as gpd
from vgrid.utils.antimeridian import fix_polygon


def construct_geometry(coords, is_multipolygon=False):
    """Construct geometry from coordinates with antimeridian fixing."""
    if is_multipolygon:
        polygon = MultiPolygon([Polygon(poly) for poly in coords])
    else:
        polygon = Polygon(coords)

    fixed_polygon = fix_polygon(polygon)
    return fixed_polygon


def cube():
    """
    Generate cube faces as GeoDataFrame.
    
    Returns:
        geopandas.GeoDataFrame: GeoDataFrame containing cube face geometries
    """
    # Define cube faces with coordinates and zone IDs
    facets = [
        {
            "cell_id": "1",
            "coordinates": [
                [-45, -35.264389682754654],
                [45, -35.264389682754654],
                [45, 35.264389682754654],
                [-45, 35.264389682754654],
                [-45, -35.264389682754654],
            ],
        },
        {
            "cell_id": "3",
            "coordinates": [
                [45, -35.264389682754654],
                [135, -35.264389682754654],
                [135, 35.264389682754654],
                [45, 35.264389682754654],
                [45, -35.264389682754654],
            ],
        },
        {
            "cell_id": "5",
            "coordinates": [
                [45, 35.264389682754654],
                [135, 35.264389682754654],
                [-135, 35.264389682754654],
                [-45, 35.264389682754654],
                [45, 35.264389682754654],
            ],
        },
        {
            "cell_id": "7",
            "coordinates": [
                [135, 35.264389682754654],
                [135, -35.264389682754654],
                [-135, -35.264389682754654],
                [-135, 35.264389682754654],
                [135, 35.264389682754654],
            ],
        },
        {
            "cell_id": "9",
            "coordinates": [
                [-135, 35.264389682754654],
                [-135, -35.264389682754654],
                [-45, -35.264389682754654],
                [-45, 35.264389682754654],
                [-135, 35.264389682754654],
            ],
        },
        {
            "cell_id": "b",
            "coordinates": [
                [-135, -35.264389682754654],
                [135, -35.264389682754654],
                [45, -35.264389682754654],
                [-45, -35.264389682754654],
                [-135, -35.264389682754654],
            ],
        },
    ]

    # Create lists to store geometries and properties
    geometries = []
    zone_ids = []
    
    for facet in facets:
        geometry = construct_geometry(facet["coordinates"])
        geometries.append(geometry)
        zone_ids.append(facet["cell_id"])

    # Create GeoDataFrame
    gdf = gpd.GeoDataFrame(
        {"cell_id": zone_ids},
        geometry=geometries,
        crs="EPSG:4326"
    )
    
    return gdf


def cube_cli():
    """Command-line interface to generate and save cube faces as GeoJSON."""
    gdf = cube()
    
    # Define the GeoJSON file path
    geojson_path = "cube.geojson"
    
    # Save GeoDataFrame as GeoJSON
    gdf.to_file(geojson_path, driver="GeoJSON")

    print(f"Cube saved as {geojson_path}")

if __name__ == "__main__":
    cube_cli()
