"""
Octahedron Grid Generator Module.
This module provides functionality to generate octahedron faces for polyhedral projections.
Reference: https://github.com/paulojraposo/QTM/blob/master/qtmgenerator.py
"""

from shapely.geometry import Polygon, LinearRing
import json
import os
import geopandas as gpd


def constructGeometry(facet):
    """Construct geometry from facet coordinates."""
    vertexTuples = facet[:4]
    # Create a LinearRing with the vertices
    ring = LinearRing(
        [(vT[1], vT[0]) for vT in vertexTuples]
    )  # sequence: lon, lat (x,y)

    # Create a Polygon from the LinearRing
    poly = Polygon(ring)
    return poly


def octahedron():
    """
    Generate octahedron faces as GeoDataFrame.
    
    Returns:
        geopandas.GeoDataFrame: GeoDataFrame containing octahedron face geometries
    """
    # Define coordinate points for octahedron faces
    p90_n180, p90_n90, p90_p0, p90_p90, p90_p180 = (
        (90.0, -180.0),
        (90.0, -90.0),
        (90.0, 0.0),
        (90.0, 90.0),
        (90.0, 180.0),
    )
    p0_n180, p0_n90, p0_p0, p0_p90, p0_p180 = (
        (0.0, -180.0),
        (0.0, -90.0),
        (0.0, 0.0),
        (0.0, 90.0),
        (0.0, 180.0),
    )
    n90_n180, n90_n90, n90_p0, n90_p90, n90_p180 = (
        (-90.0, -180.0),
        (-90.0, -90.0),
        (-90.0, 0.0),
        (-90.0, 90.0),
        (-90.0, 180.0),
    )

    # Define initial facets for octahedron
    initial_facets = [
        [p0_n180, p0_n90, p90_n90, p90_n180, p0_n180, True],
        [p0_n90, p0_p0, p90_p0, p90_n90, p0_n90, True],
        [p0_p0, p0_p90, p90_p90, p90_p0, p0_p0, True],
        [p0_p90, p0_p180, p90_p180, p90_p90, p0_p90, True],
        [n90_n180, n90_n90, p0_n90, p0_n180, n90_n180, False],
        [n90_n90, n90_p0, p0_p0, p0_n90, n90_n90, False],
        [n90_p0, n90_p90, p0_p90, p0_p0, n90_p0, False],
        [n90_p90, n90_p180, p0_p180, p0_p90, n90_p90, False],
    ]

    # Create lists to store geometries and properties
    geometries = []
    cell_ids = []
    
    for i, facet in enumerate(initial_facets):
        geometry = constructGeometry(facet)
        geometries.append(geometry)
        cell_ids.append(str(i + 1))

    # Create GeoDataFrame
    gdf = gpd.GeoDataFrame(
        {"cell_id": cell_ids},
        geometry=geometries,
        crs="EPSG:4326"
    )
    
    return gdf


def octahedron_cli():
    """Command-line interface to generate and save octahedron faces as GeoJSON."""
    gdf = octahedron()
    
    # Define the GeoJSON file path
    geojson_path = "octahedron.geojson"
    
    # Save GeoDataFrame as GeoJSON
    gdf.to_file(geojson_path, driver="GeoJSON")

    print(f"Octahedron saved as {geojson_path}")


if __name__ == "__main__":
    octahedron_cli()
