#######################################################################
## Import Libraries
#######################################################################

#import ee
import pandas as pd
import geopandas as gpd
import numpy as np

# Initialize the Earth Engine library.
#ee.Authenticate()
ee.Initialize()

# Load your AOI from the GeoJSON file
aoi_gdf = gpd.read_file('/home/srao/Documents/GitHub/sentinel/boundary.json')
aoi_geom = aoi_gdf.geometry.iloc[0]  # Assuming your GeoJSON has only one feature/geometry
aoi = ee.Geometry.Polygon(aoi_geom.__geo_interface__['coordinates']);

# Collection definition
start_date = '2023-01-01';
end_date = '2023-06-30';
collection = ee.ImageCollection('COPERNICUS/S1_GRD') \
    .filterBounds(aoi) \
    .filterDate(ee.Date(start_date), ee.Date(end_date)) \
    .filter(ee.Filter.eq('orbitProperties_pass', 'DESCENDING'))

# Generate 50 random points in the AOI
points = ee.FeatureCollection.randomPoints(aoi, 50)

# Helper function to fetch data for a given image and append to the DataFrame
def fetch_data(image, df, day_counter):
    # Getting date of acquisition
    date_of_acquisition = image.date().format('YYYY-MM-dd').getInfo()

    # Fetching backscatter values
    reduced = image.reduceRegions(collection=points, reducer=ee.Reducer.first(), scale=10)
    data_list = reduced.getInfo()['features']

    # Temporary list to store data rows
    temp_data = []

    for feature in data_list:
        coords = feature['geometry']['coordinates']
        properties = feature['properties']

        # Appending data to the temporary list
        data = {
            'date_of_acquisition': date_of_acquisition,
            'latitude': coords[1],
            'longitude': coords[0],
            'day': day_counter
        }

        # Adding available polarizations
        for pol in ['VV', 'VH','angle']:
            data[pol] = properties.get(pol, np.nan)  # Assigns NaN if polarization isn't available

        temp_data.append(data)

    # Concatenate the temp_data to the main DataFrame
    df = pd.concat([df, pd.DataFrame(temp_data)], ignore_index=True)

    return df

# Create an empty DataFrame with an additional 'day' column
columns = ['date_of_acquisition', 'day','latitude', 'longitude', 'VV', 'VH', 'angle']
df = pd.DataFrame(columns=columns)

# A day counter to differentiate the data points
day_counter = 0

# Get the unique dates from the collection
unique_dates = set([item['properties']['system:time_start'] for item in collection.getInfo()['features']])
unique_dates = sorted(unique_dates)

# Iterate over each unique date and then over each image of that date
for unique_date in unique_dates:
    date_images = collection.filterDate(ee.Date(unique_date), ee.Date(unique_date).advance(1, 'day'))
    info = date_images.getInfo()
    for image_info in info['features']:
        image = ee.Image(image_info['id'])
        df = fetch_data(image, df, day_counter)
    day_counter += 1  # Increase the day counter after processing all images of a certain date

print(df.head())

# Save the dataframe to a CSV file later
df.to_csv('sentinel_data.csv', index=False)
