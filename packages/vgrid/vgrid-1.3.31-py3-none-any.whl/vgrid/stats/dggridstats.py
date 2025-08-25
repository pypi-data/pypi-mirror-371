"""
DGGRID Statistics Module

This module provides functions to calculate and display statistics for DGGRID
Discrete Global Grid System (DGGS) types. It supports both command-line interface
and direct function calls.

Key Functions:
- dggrid_stats: Calculate and display statistics for a given DGGRID DGGS type and resolution
- dggridinspect: Generate detailed inspection data for a given DGGRID DGGS type and resolution
- main: Command-line interface for dggrid_stats
"""

import argparse
import numpy as np
import geopandas as gpd
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable
from matplotlib.colors import TwoSlopeNorm

from vgrid.utils.geometry import check_crossing_geom, geod
from vgrid.utils.constants import VMIN_QUAD, VMAX_QUAD, VCENTER_QUAD, VMIN_HEX, VMAX_HEX, VCENTER_HEX
from vgrid.generator.dggridgen import dggridgen
from dggrid4py import tool, DGGRIDv7, dggs_types
from pyproj import Geod
from vgrid.utils.io import  validate_dggrid_resolution, validate_dggrid_type
from vgrid.utils.constants import DGGRID_TYPES, AUTHALIC_AREA   

geod = Geod(ellps="WGS84")

def dggridstats(dggrid_instance: DGGRIDv7, dggs_type: str):
    """
    Calculate and display statistics for a given DGGRID DGGS type and resolution
    """
    dggs_type = validate_dggrid_type(dggs_type)
    max_res = DGGRID_TYPES[dggs_type]["max_res"]
    dggrid_info = dggrid_instance.grid_stats_table(dggs_type, max_res)
    return dggrid_info

def dggridstats_cli():
    """
    Command-line interface for generating DGGRID DGGS statistics.
    """
    parser = argparse.ArgumentParser(description="Export or display DGGRID stats.")
    parser.add_argument(
        "-dggs",
        "--dggs_type",
        choices=dggs_types,
        help="Select a DGGS type from the available options.",
    )
    args = parser.parse_args()

    dggrid_exec = tool.get_portable_executable(".")
    dggrid_instance = DGGRIDv7(executable=dggrid_exec, working_dir='.', capture_logs=False, silent=True, has_gdal=False, 
                                tmp_geo_out_legacy=True, debug=False)

    dggs_type = args.dggs_type
    try:
        print(dggridstats(dggrid_instance, dggs_type))
    except Exception:
        print(
            "Please ensure that the -r <resolution> are set appropriately, and there is an excutable DGGRID located at /usr/local/bin/dggrid. Please install DGGRID following instructions from https://github.com/sahrk/DGGRID/blob/master/INSTALL.md"
        )

def dggridinspect(dggrid_instance, dggs_type: str, res: int, crs: str | None = None) -> gpd.GeoDataFrame:
    """
    Generate detailed inspection data for a DGGRID DGGS type at a given resolution.

    Args:
        dggs_type: DGGS type supported by DGGRID (see dggs_types)
        res: Resolution level
        crs: Coordinate reference system (optional)

    Returns:
        geopandas.GeoDataFrame: DataFrame containing inspection data with columns:
          - name (cell identifier from DGGRID)
          - resolution
          - geometry
          - cell_area (m^2)
          - cell_perimeter (m)
          - crossed (bool)
          - norm_area (area/mean_area)
          - ipq (4πA/P²)
          - zsc (sqrt(4πA - A²/R²)/P), with R=WGS84 a
    """
            
    # Generate grid using dggridgen
    dggrid_gdf = dggridgen(dggrid_instance, dggs_type, res, output_format="gpd")

    # Determine whether current CRS is geographic; compute metrics accordingly
    if dggrid_gdf.crs.is_geographic:
        dggrid_gdf["cell_area"] = dggrid_gdf.geometry.apply(lambda g: abs(geod.geometry_area_perimeter(g)[0]))
        dggrid_gdf["cell_perimeter"] = dggrid_gdf.geometry.apply(lambda g: abs(geod.geometry_area_perimeter(g)[1]))
        dggrid_gdf["crossed"] = dggrid_gdf.geometry.apply(check_crossing_geom)
    else:
        dggrid_gdf["cell_area"] = dggrid_gdf.geometry.area
        dggrid_gdf["cell_perimeter"] = dggrid_gdf.geometry.length
        dggrid_gdf["crossed"] = False

    # Add resolution column
    dggrid_gdf["resolution"] = res

    # Calculate normalized area
    mean_area = dggrid_gdf["cell_area"].mean()
    dggrid_gdf["norm_area"] = dggrid_gdf["cell_area"] / mean_area if mean_area and mean_area != 0 else np.nan
    
    # Calculate compactness metrics (robust formulas avoiding division by zero)
    dggrid_gdf['ipq'] = 4 * np.pi * dggrid_gdf['cell_area'] / (dggrid_gdf['cell_perimeter'] ** 2)
    dggrid_gdf['zsc'] = np.sqrt(4*np.pi*dggrid_gdf['cell_area'] - np.power(dggrid_gdf['cell_area'],2)/np.power(6378137,2))/dggrid_gdf['cell_perimeter']
    
    return dggrid_gdf


def dggrid_norm_area(gdf, dggs_type="DGGRID", crs='proj=moll'):
    """
    Plot normalized area map for DGGRID cells.
    """
    fig, ax = plt.subplots(figsize=(10,5))
    divider = make_axes_locatable(ax)
    cax = divider.append_axes("bottom", size="5%", pad=0.1)
    vmin, vmax, vcenter = gdf['norm_area'].min(), gdf['norm_area'].max(), 1
    norm = TwoSlopeNorm(vmin=vmin, vcenter=vcenter, vmax=vmax)
    gdf = gdf[~gdf['crossed']] # remove cells that cross the dateline
    gdf.to_crs(crs).plot(column='norm_area', ax=ax, norm=norm, legend=True, cax=cax, cmap='RdYlBu_r', legend_kwds={'label': "cell area/mean cell area",'orientation': "horizontal"})
    world_countries = gpd.read_file('https://raw.githubusercontent.com/opengeoshub/vopendata/refs/heads/main/shape/world_countries.geojson')
    world_countries.boundary.to_crs(crs).plot(color=None, edgecolor='black', linewidth=0.2, ax=ax)
    ax.axis('off')
    cb_ax = fig.axes[1] 
    cb_ax.tick_params(labelsize=14)
    cb_ax.set_xlabel(xlabel=f"{dggs_type.upper()} Normalized Area", fontsize=14)
    ax.margins(0)
    ax.tick_params(left=False, labelleft=False, bottom=False, labelbottom=False)
    plt.tight_layout()


def dggrid_compactness(gdf: gpd.GeoDataFrame, dggs_type: str = "DGGRID", crs: str | None = 'proj=moll'):
    """
    Plot IPQ compactness map for DGGRID cells.
    """
    fig, ax = plt.subplots(figsize=(10, 5))
    divider = make_axes_locatable(ax)
    cax = divider.append_axes("bottom", size="5%", pad=0.1)
    
    # Determine compactness bounds based on topology
    vmin, vmax, vcenter = VMIN_QUAD, VMAX_QUAD, VCENTER_QUAD
    
    dggs_type_norm = str(dggs_type).strip().lower()
    if any(hex_type in dggs_type_norm for hex_type in ["3h", "4h", "7h", "43h"]):
        vmin, vmax, vcenter = VMIN_HEX, VMAX_HEX, VCENTER_HEX
    
    norm = TwoSlopeNorm(vmin=vmin, vcenter=vcenter, vmax=vmax)
    # Only filter out antimeridian-crossed cells when plotting in EPSG:4326
    gdf = gdf[~gdf['crossed']]
    gdf_plot = gdf.to_crs(crs) if crs else gdf
    gdf_plot.plot(column='ipq', ax=ax, norm=norm, legend=True, cax=cax,
                  cmap='viridis', legend_kwds={'orientation': "horizontal"})
    world_countries = gpd.read_file('https://raw.githubusercontent.com/opengeoshub/vopendata/refs/heads/main/shape/world_countries.geojson')
    wc_plot = world_countries.boundary.to_crs(crs)
    wc_plot.plot(color=None, edgecolor='black', linewidth=0.2, ax=ax)
    ax.axis('off')
    cb_ax = fig.axes[1]
    cb_ax.tick_params(labelsize=14)
    cb_ax.set_xlabel(xlabel=f"{dggs_type.upper()} IPQ Compactness", fontsize=14)
    ax.margins(0)
    ax.tick_params(left=False, labelleft=False, bottom=False, labelbottom=False)
    plt.tight_layout()


def dggridinspect_cli():
    """
    Command-line interface for DGGRID cell inspection.

    CLI options:
      -t, --dggs_type: DGGS type from dggs_types
      -r, --resolution: Resolution level
    """
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('-dggs', '--dggs_type', dest='dggs_type', choices=dggs_types, required=True)
    parser.add_argument('-r', '--resolution', dest='resolution', type=int, default=None)
    parser.add_argument('-crs', dest='crs', type=str, default=None, help="CRS to pass to DGGRID; omit for WGS84")
    args, _ = parser.parse_known_args()
    res = args.resolution if args.resolution is not None else 0
    
    dggrid_exec = tool.get_portable_executable(".")
    dggrid_instance = DGGRIDv7(executable=dggrid_exec, working_dir='.', capture_logs=False, silent=True, 
                                has_gdal=False, tmp_geo_out_legacy=True, debug=False)

    print(dggridinspect(dggrid_instance, args.dggs_type, res, crs=args.crs))


if __name__ == "__main__":
    dggridstats_cli()
