"""
This module provides functions for generating comprehensive statistics across multiple DGGS types.
"""

import pandas as pd
import numpy as np
import geopandas as gpd
from typing import List, Optional
import shutil
import subprocess
import sys
import re

# Import all the individual inspect functions
from vgrid.stats.h3stats import h3inspect
from vgrid.stats.s2stats import s2inspect
from vgrid.stats.a5stats import a5inspect
from vgrid.stats.rhealpixstats import rhealpixinspect
from vgrid.stats.isea4tstats import isea4tinspect
from vgrid.utils.constants import DGGAL_TYPES


def dggsinspect(minres: int, maxres: int) -> gpd.GeoDataFrame:
    """
    Generate comprehensive inspection data for multiple DGGS types across a range of resolutions.
    
    This function calls the individual inspect functions for H3, S2, A5, rHEALPix, and ISEA4T
    DGGS types and combines them into a single unique GeoDataFrame with a dggs_type column
    to distinguish between different DGGS implementations.
    
    Args:
        minres: Minimum resolution level to inspect
        maxres: Maximum resolution level to inspect (inclusive)
    
    Returns:
        geopandas.GeoDataFrame: Combined DataFrame containing inspection data from all DGGS types
            with columns:
            - dggs_type: Type of DGGS (h3, s2, a5, rhealpix, isea4t)
            - resolution: Resolution level
            - cell_id: Cell identifier (h3, s2, a5, rhealpix, isea4t)
            - geometry: Cell geometry
            - cell_area: Cell area in square meters
            - cell_perimeter: Cell perimeter in meters
            - crossed: Whether cell crosses the dateline
            - norm_area: Normalized area (cell_area / mean_area)
            - ipq: Isoperimetric Quotient compactness
            - zsc: Zonal Standardized Compactness
            - is_pentagon: Whether cell is a pentagon (H3 only, NaN for others)
    
    Raises:
        ValueError: If minres > maxres or if resolution ranges are invalid for specific DGGS types
    """
    if minres > maxres:
        raise ValueError("minres must be less than or equal to maxres")
    
    # Define DGGS type configurations with their valid resolution ranges
    dggs_configs = {
        'h3': {'inspect_func': h3inspect, 'min_res': 0, 'max_res': 15},
        's2': {'inspect_func': s2inspect, 'min_res': 0, 'max_res': 30},
        'a5': {'inspect_func': a5inspect, 'min_res': 0, 'max_res': 20},
        'rhealpix': {'inspect_func': rhealpixinspect, 'min_res': 0, 'max_res': 20},
        'isea4t': {'inspect_func': isea4tinspect, 'min_res': 0, 'max_res': 20}
    }
    
    all_gdfs = []
    
    for dggs_type, config in dggs_configs.items():
        # Determine the valid resolution range for this DGGS type
        valid_min = max(minres, config['min_res'])
        valid_max = min(maxres, config['max_res'])
        
        if valid_min > valid_max:
            print(f"Warning: No valid resolutions for {dggs_type} in range {minres}-{maxres}")
            continue
        
        print(f"Processing {dggs_type} for resolutions {valid_min}-{valid_max}")
        
        for res in range(valid_min, valid_max + 1):
            try:
                # Call the specific inspect function
                gdf = config['inspect_func'](res)
                
                # Add dggs_type column
                gdf['dggs_type'] = dggs_type
                
                # Rename the cell ID column to a generic name
                cell_id_col = dggs_type  # h3, s2, a5, rhealpix, isea4t
                if cell_id_col in gdf.columns:
                    gdf = gdf.rename(columns={cell_id_col: 'cell_id'})
                
                # Ensure all expected columns exist, add NaN for missing ones
                expected_columns = [
                    'dggs_type', 'resolution', 'cell_id', 'geometry', 
                    'cell_area', 'cell_perimeter', 'crossed', 'norm_area', 
                    'ipq', 'zsc', 'is_pentagon'
                ]
                
                for col in expected_columns:
                    if col not in gdf.columns:
                        if col == 'is_pentagon':
                            # Only H3 has pentagons, others get NaN
                            gdf[col] = np.nan
                        else:
                            gdf[col] = None
                
                # Reorder columns to match expected format
                gdf = gdf[expected_columns]
                
                all_gdfs.append(gdf)
                
            except Exception as e:
                print(f"Error processing {dggs_type} at resolution {res}: {e}")
                continue
    
    if not all_gdfs:
        raise ValueError("No valid DGGS data could be generated for the specified resolution range")
    
    # Combine all GeoDataFrames
    combined_gdf = pd.concat(all_gdfs, ignore_index=True)
    
    # Ensure it's a GeoDataFrame
    if not isinstance(combined_gdf, gpd.GeoDataFrame):
        combined_gdf = gpd.GeoDataFrame(combined_gdf, geometry='geometry')
    
    return combined_gdf


def dggsinspect_cli():
    """
    Command-line interface for multi-DGGS cell inspection.
    
    CLI options:
      --minres: Minimum resolution level (default: 0)
      --maxres: Maximum resolution level (default: 10)
      --output: Output file path for GeoParquet file (default: dggs_inspection.parquet)
    """
    import argparse
    import os
    from datetime import datetime
    
    parser = argparse.ArgumentParser(description="Multi-DGGS inspection tool")
    parser.add_argument('--minres', type=int, default=0, 
                       help='Minimum resolution level (default: 0)')
    parser.add_argument('--maxres', type=int, default=10, 
                       help='Maximum resolution level (default: 10)')
    parser.add_argument('--output', type=str, default=None,
                       help='Output file path for GeoParquet file (default: dggs_inspection_min{minres}_max{maxres}.parquet)')
    
    args = parser.parse_args()
    
    try:
        result = dggsinspect(args.minres, args.maxres)
        print(f"Generated inspection data for {len(result)} cells across multiple DGGS types")
        print(f"DGGS types included: {result['dggs_type'].unique()}")
        print(f"Resolution range: {result['resolution'].min()}-{result['resolution'].max()}")
        
        # Generate output filename if not provided
        if args.output is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            args.output = f"dggs_inspection_min{args.minres}_max{args.maxres}_{timestamp}.parquet"
        
        # Save as GeoParquet file
        print(f"Saving GeoDataFrame to: {args.output}")
        result.to_parquet(args.output, index=False)
        print(f"Successfully saved {len(result)} records to {args.output}")
        
        return result
    except Exception as e:
        print(f"Error: {e}")
        return None

if __name__ == "__main__":
    dggsinspect_cli()