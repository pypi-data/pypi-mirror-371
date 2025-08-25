"""
Tetrahedron Grid Generator Module.
This module provides functionality to generate tetrahedron faces for polyhedral projections.
"""

from shapely.geometry import Polygon
import json
import os
import geopandas as gpd


def constructGeometry(facet):
    """Create a Polygon with the vertices (longitude, latitude)."""
    poly = Polygon([(v[0], v[1]) for v in facet])  # (lon, lat)
    return poly


def tetrahedron():
    """
    Generate tetrahedron faces as GeoDataFrame.
    
    Returns:
        geopandas.GeoDataFrame: GeoDataFrame containing tetrahedron face geometries
    """

    # Define facets with coordinates and cell_ids
    facets = [
        {
            "cell_id": "0",
            "coordinates": [
                [-180.0, 0.0],
                [-180.0, 90.0],
                [-90.0, 90.0],
                [0.0, 90.0],
                [0.0, 0.0],
                [-90.0, 0.0],
                [-180.0, 0.0],
            ],
        },
        {
            "cell_id": "1",
            "coordinates": [
                [0.0, 0.0],
                [0.0, 90.0],
                [90.0, 90.0],
                [180.0, 90.0],
                [180.0, 0.0],
                [90.0, 0.0],
                [0.0, 0.0],
            ],
        },
        {
            "cell_id": "2",
            "coordinates": [
                [-180.0, -90.0],
                [-180.0, 0.0],
                [-90.0, 0.0],
                [0.0, 0.0],
                [0.0, -90.0],
                [-90.0, -90.0],
                [-180.0, -90.0],
            ],
        },
        {
            "cell_id": "3",
            "coordinates": [
                [0.0, -90.0],
                [0.0, 0.0],
                [90.0, 0.0],
                [180.0, 0.0],
                [180.0, -90.0],
                [90.0, -90.0],
                [0.0, -90.0],
            ],
        },
    ]

    # Create lists to store geometries and properties
    geometries = []
    zone_ids = []
    
    for facet in facets:
        geometry = Polygon(facet["coordinates"])
        geometries.append(geometry)
        zone_ids.append(facet["cell_id"])

    # Create GeoDataFrame
    gdf = gpd.GeoDataFrame(
        {"cell_id": zone_ids},
        geometry=geometries,
        crs="EPSG:4326"
    )
    
    return gdf


def tetrahedron_cli():
    """Command-line interface to generate and save tetrahedron faces as GeoJSON."""
    gdf = tetrahedron()
    
    # Define the GeoJSON file path
    geojson_path = "tetrahedron.geojson"
    
    # Save GeoDataFrame as GeoJSON
    gdf.to_file(geojson_path, driver="GeoJSON")

    print(f"Tetrahedron saved as {geojson_path}")


if __name__ == "__main__":
    tetrahedron_cli()
