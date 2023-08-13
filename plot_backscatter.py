#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Aug 13 22:08:42 2023

@author: srao
"""
import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
from scipy.interpolate import griddata
import pandas as pd

# Load the CSV data into a DataFrame
df_sentinel = pd.read_csv('/home/srao/Documents/GitHub/sentinel/sentinel_data.csv');
# Load the GeoJSON file into a GeoDataFrame
gdf_boundary = gpd.read_file('/home/srao/Documents/GitHub/sentinel/boundary.json');

# Convert the DataFrame to a GeoDataFrame
gdf_sentinel = gpd.GeoDataFrame(df_sentinel, geometry=gpd.points_from_xy(df_sentinel.longitude, df_sentinel.latitude))

# Define a function for the visualization
def visualize_backscatter(gdf_sentinel, gdf_boundary, polarization, date):
    # Filter by date
    gdf_filtered = gdf_sentinel[gdf_sentinel['date_of_acquisition'] == date]
    
    # Determine global min and max for consistent color scaling
    vmin = gdf_sentinel[polarization].min()
    vmax = gdf_sentinel[polarization].max()
    
    # Plot
    fig, ax = plt.subplots(figsize=(12, 12))
    ax.set_aspect('equal')
    
    # Plot boundary
    gdf_boundary.boundary.plot(ax=ax, color='black', linewidth=1.5)
    
    # Scatter plot of backscatter values with solid circles
    sc = ax.scatter(gdf_filtered['longitude'], gdf_filtered['latitude'], c=gdf_filtered[polarization], 
                    cmap='viridis', s=100, vmin=vmin, vmax=vmax)
    
    # Color bar
    fig.colorbar(sc, ax=ax, orientation='vertical', label='Backscatter (dB)')
    
    # Set title and display plot
    ax.set_title(f'Backscatter for {date}')
    plt.show()

# Visualize HH (VV) backscatter for the first date in the dataset (as an example)
date_example = df_sentinel['date_of_acquisition'].iloc[0]
visualize_backscatter(gdf_sentinel, gdf_boundary, 'VV', date_example)