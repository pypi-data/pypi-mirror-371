#!/usr/bin/env python3
"""
Script to create a seaborn boxplot from an existing DGGS inspection parquet file.
"""

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import geopandas as gpd

# Read the existing parquet file
parquet_file = "dggs_inspection_min2_max6_20250814_154405.parquet"
gdf = gpd.read_parquet(parquet_file)

# Convert to regular DataFrame (drop geometry column for plotting)
df = pd.DataFrame(gdf.drop(columns=['geometry']))

print(f"Loaded data with {len(df)} cells across DGGS types: {df['dggs_type'].unique()}")
print(f"Resolution range: {df['resolution'].min()}-{df['resolution'].max()}")

# Create the boxplot exactly as in your example
plt.figure(figsize=(9,9))

# Use modern seaborn style (seaborn-whitegrid is deprecated)
plt.style.use('default')
sns.set_style("whitegrid")

# Define design of the outliers
outlier_design = dict(marker='o', markerfacecolor='black', markersize=1,
                  linestyle='none', markeredgecolor='black')

# Plot the boxplots - NOTE: use 'dggs_type' column, not 'dggs'
chart = sns.boxplot(x='dggs_type', y="norm_area", data=df, palette="viridis", saturation=0.9, showfliers=True, flierprops = outlier_design)

plt.xticks(
    rotation=90,
    horizontalalignment='center',
    fontweight='light',
    fontsize='xx-large', 
)

plt.xlabel('', fontsize='x-large')

plt.yticks(
    rotation=0, 
    horizontalalignment='right',
    fontweight='light',
    fontsize='xx-large',
)

plt.ylabel('normalized area', fontsize='xx-large')

# Set min and max values for y-axis
plt.ylim(0.5, 1.3)

plt.tight_layout()
plt.savefig("box_plot_area.png", bbox_inches="tight", dpi=300)

plt.show()

print("Boxplot created successfully!")
print(f"Data contains {len(df)} cells across DGGS types: {df['dggs_type'].unique()}")
print(f"Resolution range: {df['resolution'].min()}-{df['resolution'].max()}")

# Print some summary statistics
print("\nSummary statistics by DGGS type:")
summary = df.groupby('dggs_type')['norm_area'].agg(['count', 'mean', 'std', 'min', 'max'])
print(summary)
