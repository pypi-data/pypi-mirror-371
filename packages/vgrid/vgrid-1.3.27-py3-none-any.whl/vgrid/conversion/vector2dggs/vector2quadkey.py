"""
Vector to Quadkey DGGS Grid Conversion Module
"""

import sys
import os
import argparse
from tqdm import tqdm
from shapely.geometry import Polygon, MultiPoint, MultiLineString, MultiPolygon
import geopandas as gpd
from vgrid.dggs import tilecode
from vgrid.dggs import mercantile
from vgrid.utils.geometry import graticule_dggs_to_geoseries
from vgrid.conversion.dggscompact.quadkeycompact import quadkeycompact
from vgrid.utils.geometry import (
    check_predicate,
    shortest_point_distance,
    shortest_polyline_distance,
    shortest_polygon_distance,
)
from math import sqrt
from vgrid.utils.io import validate_quadkey_resolution, process_input_data_vector, convert_to_output_format
from vgrid.utils.constants import OUTPUT_FORMATS, STRUCTURED_FORMATS


def point2quadkey(
    resolution,
    point,
    feature_properties=None,
    predicate=None,
    compact=False,
    topology=False,
    include_properties=True,
    all_points=None,
):
    """
    Convert a point geometry to a Quadkey grid cell.

    Args:
        resolution (int): Quadkey resolution [0..29]
        point (shapely.geometry.Point): Point geometry to convert
        feature_properties (dict, optional): Properties to include in output features
        predicate (str, optional): Spatial predicate to apply (not used for points)
        compact (bool, optional): Enable Quadkey compact mode (not used for points)
        topology (bool, optional): Enable topology preserving mode (not used for points)
        include_properties (bool, optional): Whether to include properties in output
        all_points (list, optional): List of points for topology preservation

    Returns:
        list: List of GeoDataFrame format dictionaries representing Quadkey cells containing the point
    """
    if topology:
        if all_points is None:
            raise ValueError("all_points parameter is required when topology=True")
        shortest_distance = shortest_point_distance(all_points)
        quadkey_cell_sizes = [40075016.68557849 / (2**z) for z in range(30)]
        for res in range(0, 30):
            cell_diameter = quadkey_cell_sizes[res] * sqrt(2) * 2
            if cell_diameter < shortest_distance:
                resolution = res
                break
        else:
            resolution = 29
    quadkey_rows = []
    quadkey_id = tilecode.latlon2quadkey(point.y, point.x, resolution)
    quadkey_cell = mercantile.tile(point.x, point.y, resolution)
    bounds = mercantile.bounds(quadkey_cell)
    if bounds:
        min_lat, min_lon = bounds.south, bounds.west
        max_lat, max_lon = bounds.north, bounds.east
        cell_polygon = Polygon(
            [
                [min_lon, min_lat],
                [max_lon, min_lat],
                [max_lon, max_lat],
                [min_lon, max_lat],
                [min_lon, min_lat],
            ]
        )
        quadkey_row = graticule_dggs_to_geoseries("quadkey", quadkey_id, resolution, cell_polygon)
        if include_properties and feature_properties:
            quadkey_row.update(feature_properties)
        quadkey_rows.append(quadkey_row)
    return quadkey_rows


def polyline2quadkey(
    resolution,
    feature,
    feature_properties=None,
    predicate=None,
    compact=False,
    topology=False,
    include_properties=True,
    all_polylines=None,
):
    """
    Convert line geometries (LineString, MultiLineString) to Quadkey grid cells.

    Args:
        resolution (int): Quadkey resolution [0..29]
        feature (shapely.geometry.LineString or shapely.geometry.MultiLineString): Line geometry to convert
        feature_properties (dict, optional): Properties to include in output features
        predicate (str, optional): Spatial predicate to apply (not used for lines)
        compact (bool, optional): Enable Quadkey compact mode to reduce cell count
        topology (bool, optional): Enable topology preserving mode (not used for lines)
        include_properties (bool, optional): Whether to include properties in output
        all_polylines (list, optional): List of polylines for topology preservation

    Returns:
        list: List of GeoDataFrame format dictionaries representing Quadkey cells intersecting the line
    """
    if topology:
        if all_polylines is None:
            raise ValueError("all_polylines parameter is required when topology=True")
        shortest_distance = shortest_polyline_distance(all_polylines)
        quadkey_cell_sizes = [40075016.68557849 / (2**z) for z in range(30)]
        for res in range(0, 30):
            cell_diameter = quadkey_cell_sizes[res] * sqrt(2) * 4
            if cell_diameter < shortest_distance:
                resolution = res
                break
        else:
            resolution = 29
    quadkey_rows = []
    if feature.geom_type in ("LineString"):
        polylines = [feature]
    elif feature.geom_type in ("MultiLineString"):
        polylines = list(feature.geoms)
    else:
        return []
    for polyline in polylines:
        min_lon, min_lat, max_lon, max_lat = polyline.bounds
        tiles = mercantile.tiles(min_lon, min_lat, max_lon, max_lat, resolution)
        for tile in tiles:
            z, x, y = tile.z, tile.x, tile.y
            bounds = mercantile.bounds(x, y, z)
            if bounds:
                min_lat, min_lon = bounds.south, bounds.west
                max_lat, max_lon = bounds.north, bounds.east
                quadkey_id = mercantile.quadkey(tile)
                cell_polygon = Polygon(
                    [
                        [min_lon, min_lat],
                        [max_lon, min_lat],
                        [max_lon, max_lat],
                        [min_lon, max_lat],
                        [min_lon, min_lat],
                    ]
                )
                if cell_polygon.intersects(polyline):
                    quadkey_row = graticule_dggs_to_geoseries("quadkey", quadkey_id, resolution, cell_polygon)
                    if include_properties and feature_properties:
                        quadkey_row.update(feature_properties)
                    quadkey_rows.append(quadkey_row)

    return quadkey_rows


def polygon2quadkey(
    resolution,
    feature,
    feature_properties=None,
    predicate=None,
    compact=False,
    topology=False,
    include_properties=True,
    all_polygons=None,
):
    """
    Convert polygon geometries (Polygon, MultiPolygon) to Quadkey grid cells.

    Args:
        resolution (int): Quadkey resolution [0..29]
        feature (shapely.geometry.Polygon or shapely.geometry.MultiPolygon): Polygon geometry to convert
        feature_properties (dict, optional): Properties to include in output features
        predicate (str, optional): Spatial predicate to apply ('intersect', 'within', 'centroid_within', 'largest_overlap')
        compact (bool, optional): Enable Quadkey compact mode to reduce cell count
        topology (bool, optional): Enable topology preserving mode (not used for polygons)
        include_properties (bool, optional): Whether to include properties in output
        all_polygons (list, optional): List of polygons for topology preservation

    Returns:
        list: List of GeoDataFrame format dictionaries representing Quadkey cells based on predicate
    """
    if topology:
        if all_polygons is None:
            raise ValueError("all_polygons parameter is required when topology=True")
        shortest_distance = shortest_polygon_distance(all_polygons)
        quadkey_cell_sizes = [40075016.68557849 / (2**z) for z in range(30)]
        for res in range(0, 30):
            cell_diameter = quadkey_cell_sizes[res] * sqrt(2) * 4
            if cell_diameter < shortest_distance:
                resolution = res
                break
        else:
            resolution = 29
    quadkey_rows = []
    if feature.geom_type in ("Polygon"):
        polygons = [feature]
    elif feature.geom_type in ("MultiPolygon"):
        polygons = list(feature.geoms)
    else:
        return []
    for polygon in polygons:
        min_lon, min_lat, max_lon, max_lat = polygon.bounds
        tiles = mercantile.tiles(min_lon, min_lat, max_lon, max_lat, resolution)
        for tile in tiles:
            z, x, y = tile.z, tile.x, tile.y
            bounds = mercantile.bounds(x, y, z)
            if bounds:
                min_lat, min_lon = bounds.south, bounds.west
                max_lat, max_lon = bounds.north, bounds.east
                quadkey_id = mercantile.quadkey(tile)
                cell_polygon = Polygon(
                    [
                        [min_lon, min_lat],
                        [max_lon, min_lat],
                        [max_lon, max_lat],
                        [min_lon, max_lat],
                        [min_lon, min_lat],
                    ]
                )
                if check_predicate(cell_polygon, polygon, predicate):
                    quadkey_row = graticule_dggs_to_geoseries("quadkey", quadkey_id, resolution, cell_polygon)
                    if include_properties and feature_properties:
                        quadkey_row.update(feature_properties)
                    quadkey_rows.append(quadkey_row)

    return quadkey_rows


def geometry2quadkey(
    geometries,
    resolution,
    properties_list=None,
    predicate=None,
    compact=False,
    topology=False,
    include_properties=True,
):
    """
    Convert a list of geometries to Quadkey grid cells.

    Args:
        geometries (shapely.geometry.BaseGeometry or list): Single geometry or list of geometries
        resolution (int): Quadkey resolution [0..29]
        properties_list (list, optional): List of property dictionaries for each geometry
        predicate (str, optional): Spatial predicate to apply for polygons
        compact (bool, optional): Enable Quadkey compact mode for polygons and lines
        topology (bool, optional): Enable topology preserving mode
        include_properties (bool, optional): Whether to include properties in output

    Returns:
        geopandas.GeoDataFrame: GeoDataFrame with Quadkey grid cells
    """
    # Handle single geometry or list of geometries
    if not isinstance(geometries, list):
        geometries = [geometries]

    # Handle properties
    if properties_list is None:
        properties_list = [{} for _ in geometries]
    elif not isinstance(properties_list, list):
        properties_list = [properties_list for _ in geometries]

    # Collect all points, polylines, and polygons for topology preservation if needed
    all_points = None
    all_polylines = None
    all_polygons = None
    if topology:
        points_list = []
        polylines_list = []
        polygons_list = []
        for i, geom in enumerate(geometries):
            if geom is None:
                continue
            if geom.geom_type == "Point":
                points_list.append(geom)
            elif geom.geom_type == "MultiPoint":
                points_list.extend(list(geom.geoms))
            elif geom.geom_type == "LineString":
                polylines_list.append(geom)
            elif geom.geom_type == "MultiLineString":
                polylines_list.extend(list(geom.geoms))
            elif geom.geom_type == "Polygon":
                polygons_list.append(geom)
            elif geom.geom_type == "MultiPolygon":
                polygons_list.extend(list(geom.geoms))
        if points_list:
            all_points = MultiPoint(points_list)
        if polylines_list:
            all_polylines = MultiLineString(polylines_list)
        if polygons_list:
            all_polygons = MultiPolygon(polygons_list)

    quadkey_rows = []
    for i, geom in enumerate(tqdm(geometries, desc="Processing features")):
        if geom is None:
            continue
        props = properties_list[i] if i < len(properties_list) else {}
        if not include_properties:
            props = {}
        if geom.geom_type == "Point":
            quadkey_rows.extend(
                point2quadkey(
                    resolution,
                    geom,
                    props,
                    predicate,
                    compact,
                    topology,
                    include_properties,
                    all_points,  # Pass all points for topology preservation
                )
            )
        elif geom.geom_type == "MultiPoint":
            for pt in geom.geoms:
                quadkey_rows.extend(
                    point2quadkey(
                        resolution,
                        pt,
                        props,
                        predicate,
                        compact,
                        topology,
                        include_properties,
                        all_points,  # Pass all points for topology preservation
                    )
                )
        elif geom.geom_type in ("LineString", "MultiLineString"):
            quadkey_rows.extend(
                polyline2quadkey(
                    resolution,
                    geom,
                    props,
                    predicate,
                    compact,
                    topology,
                    include_properties,
                    all_polylines,  # Pass all polylines for topology preservation
                )
            )
        elif geom.geom_type in ("Polygon", "MultiPolygon"):
            quadkey_rows.extend(
                polygon2quadkey(
                    resolution,
                    geom,
                    props,
                    predicate,
                    compact,
                    topology,
                    include_properties,
                    all_polygons=all_polygons,  # Pass all polygons for topology preservation
                )
            )
    # Convert to GeoDataFrame
    return gpd.GeoDataFrame(quadkey_rows, geometry="geometry", crs="EPSG:4326")


def dataframe2quadkey(
    df,
    resolution,
    predicate=None,
    compact=False,
    topology=False,
    include_properties=True,
):
    """
    Convert a pandas DataFrame with geometry column to Quadkey grid cells.

    Args:
        df (pandas.DataFrame): DataFrame with geometry column
        resolution (int): Quadkey resolution [0..29]
        predicate (str, optional): Spatial predicate to apply for polygons
        compact (bool, optional): Enable Quadkey compact mode for polygons and lines
        topology (bool, optional): Enable topology preserving mode
        include_properties (bool, optional): Whether to include properties in output

    Returns:
        geopandas.GeoDataFrame: GeoDataFrame with Quadkey grid cells
    """
    geometries = []
    properties_list = []
    for idx, row in df.iterrows():
        geom = row.geometry if "geometry" in row else row["geometry"]
        if geom is not None:
            geometries.append(geom)
            props = row.to_dict()
            if "geometry" in props:
                del props["geometry"]
            properties_list.append(props)

    return geometry2quadkey(
        geometries,
        resolution,
        properties_list,
        predicate,
        compact,
        topology,
        include_properties,
    )


def geodataframe2quadkey(
    gdf,
    resolution,
    predicate=None,
    compact=False,
    topology=False,
    include_properties=True,
):
    """
    Convert a GeoDataFrame to Quadkey grid cells.

    Args:
        gdf (geopandas.GeoDataFrame): GeoDataFrame to convert
        resolution (int): Quadkey resolution [0..29]
        predicate (str, optional): Spatial predicate to apply for polygons
        compact (bool, optional): Enable Quadkey compact mode for polygons and lines
        topology (bool, optional): Enable topology preserving mode
        include_properties (bool, optional): Whether to include properties in output

    Returns:
        geopandas.GeoDataFrame: GeoDataFrame with Quadkey grid cells
    """
    geometries = []
    properties_list = []
    for idx, row in gdf.iterrows():
        geom = row.geometry
        if geom is not None:
            geometries.append(geom)
            props = row.to_dict()
            if "geometry" in props:
                del props["geometry"]
            properties_list.append(props)
    return geometry2quadkey(
        geometries,
        resolution,
        properties_list,
        predicate,
        compact,
        topology,
        include_properties,
    )


def vector2quadkey(
    data,
    resolution,
    predicate=None,
    compact=False,
    topology=False,
    output_format="gpd",
    include_properties=True,
    **kwargs,
):
    """
    Convert vector data to Quadkey grid cells from various input formats.
    If output_format is a file-based format (csv, geojson, shapefile, gpkg, parquet, geoparquet),
    the output will be saved to a file in the current directory with a default name based on the input.
    Otherwise, returns a Python object (GeoDataFrame, dict, etc.) depending on output_format.
    The internal processing always uses GeoDataFrame format for consistency.
    """
    resolution = validate_quadkey_resolution(resolution)
    gdf = process_input_data_vector(data, **kwargs)
    geometries = list(gdf.geometry)
    properties_list = [row.drop(labels=["geometry"]).to_dict() for idx, row in gdf.iterrows()]
    result = geometry2quadkey(
        geometries,
        resolution,
        properties_list,
        predicate,
        compact,
        topology,
        include_properties,
    )
    if compact:
        result = quadkeycompact(result, quadkey_id="quadkey", output_format="gpd")
        
    file_formats = [
        "csv",
        "geojson",
        "json",
        "shapefile",
        "shp",
        "gpkg",
        "geopackage",
        "parquet",
        "geoparquet",
    ]
    output_name = None
    if output_format in file_formats:
        if isinstance(data, str):
            base = os.path.splitext(os.path.basename(data))[0]
            output_name = f"{base}2quadkey_{resolution}"
        else:
            output_name = f"quadkey_{resolution}"
    return convert_to_output_format(result, output_format, output_name)


def vector2quadkey_cli():
    """
    Command-line interface for vector2quadkey conversion.
    """
    parser = argparse.ArgumentParser(
        description="Convert vector data to Quadkey grid cells"
    )
    parser.add_argument("-i", "--input", help="Input file path, URL")
    parser.add_argument(
        "-r",
        "--resolution",
        type=int,
        choices=range(0, 30),
        metavar="[0-29]",
        help="Quadkey resolution [0..29] (0=coarsest, 29=finest)",
    )
    parser.add_argument(
        "-p",
        "--predicate",
        choices=["intersect", "within", "centroid_within", "largest_overlap"],
        help="Spatial predicate: intersect, within, centroid_within, largest_overlap for polygons",
    )
    parser.add_argument(
        "-c",
        "--compact",
        action="store_true",
        help="Enable Quadkey compact mode for polygons",
    )
    parser.add_argument(
        "-t", "--topology", action="store_true", help="Enable topology preserving mode"
    )
    parser.add_argument(
        "-np",
        "-no-props",
        dest="include_properties",
        action="store_false",
        help="Do not include original feature properties.",
    )
    parser.add_argument(
        "-f",
        "--output_format",
        type=str,
        choices=OUTPUT_FORMATS,
        default="gpd",
    )
    args = parser.parse_args()
    args.resolution = validate_quadkey_resolution(args.resolution)
    data = args.input
    try:
        result = vector2quadkey(
            data,
            args.resolution,
            predicate=args.predicate,
            compact=args.compact,
            topology=args.topology,
            output_format=args.output_format,
            include_properties=args.include_properties,
        )
        if args.output_format in STRUCTURED_FORMATS:
            print(result)
        # For file outputs, the utility prints the saved path
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    vector2quadkey_cli()
