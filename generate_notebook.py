import json
import argparse
import os

parser = argparse.ArgumentParser(description="Generate house price notebook")
parser.add_argument(
    "--csv",
    default="trafford prices.csv",
    help="Input CSV file"
)
parser.add_argument("--output", default="house_price_map.ipynb", help="Output notebook")
args = parser.parse_args()

csv_file = args.csv
output_notebook = args.output

cells = []

cells.append({
    "cell_type": "markdown",
    "metadata": {},
    "source": [
        "# House Price Map\n",
        "\n",
        "This notebook loads property transaction data from the Land Registry CSV,\n",
        "geocodes the postcodes to latitude/longitude and plots them on a map using Folium.\n",
        "Marker colours indicate relative price bands. Click a marker to see details about the property."
    ]
})

cells.append({
    "cell_type": "code",
    "execution_count": None,
    "metadata": {},
    "outputs": [],
    "source": """# Install dependencies if running in a fresh environment
import sys, subprocess
for pkg in ['pandas','folium','pgeocode','numpy','matplotlib']:
    if pkg not in sys.modules:
        try:
            __import__(pkg)
        except ImportError:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', pkg])
"""
})

cells.append({
    "cell_type": "code",
    "execution_count": None,
    "metadata": {},
    "outputs": [],
    "source": """import pandas as pd
import folium
from folium.plugins import HeatMapWithTime, MarkerCluster, Fullscreen
import pgeocode
import numpy as np
import matplotlib.pyplot as plt
"""
})

load_and_map_code = f"""# Load the CSV file
columns = ['transaction_id','price','date','postcode','property_type','old_new','duration','paon','saon','street','locality','town','district','county','ppd_cat','record_status']
df = pd.read_csv('{csv_file}', header=None, names=columns)
df['price'] = df['price'].astype(float)
df['date'] = pd.to_datetime(df['date'])

# Geocode postcodes
nomi = pgeocode.Nominatim('gb')
df[['lat','lon']] = df['postcode'].apply(lambda x: nomi.query_postal_code(x)[['latitude','longitude']])
df = df.dropna(subset=['lat','lon'])

# Bin prices into 5 quantiles
quantiles = pd.qcut(df['price'], 5, labels=False)
colours = ['blue','green','yellow','orange','red']
df['colour'] = quantiles.apply(lambda x: colours[int(x)])

legend_html = '''<div style="position: fixed; bottom: 50px; left: 50px; width: 150px;
height: 130px; border:2px solid grey; background-color:white; z-index:9999; font-size:14px;">
&nbsp;<b>Price Range</b><br>
&nbsp;<i style=\"background:blue;\">&nbsp;&nbsp;&nbsp;&nbsp;</i>&nbsp;Lowest<br>
&nbsp;<i style=\"background:green;\">&nbsp;&nbsp;&nbsp;&nbsp;</i><br>
&nbsp;<i style=\"background:yellow;\">&nbsp;&nbsp;&nbsp;&nbsp;</i><br>
&nbsp;<i style=\"background:orange;\">&nbsp;&nbsp;&nbsp;&nbsp;</i><br>
&nbsp;<i style=\"background:red;\">&nbsp;&nbsp;&nbsp;&nbsp;</i>&nbsp;Highest
</div>'''

def create_map(data):
    m = folium.Map(location=[data['lat'].mean(), data['lon'].mean()], zoom_start=10)
    Fullscreen().add_to(m)
    marker_cluster = MarkerCluster().add_to(m)
    for _, row in data.iterrows():
        popup_text = f"{{row['street']}} {{row['postcode']}}<br>£{{row['price']:,}}<br>{{row['date'].date()}}"
        folium.CircleMarker(
            location=[row['lat'], row['lon']],
            radius=5,
            color=row['colour'],
            fill=True,
            fill_color=row['colour'],
            popup=folium.Popup(popup_text, max_width=250)
        ).add_to(marker_cluster)
    m.get_root().html.add_child(folium.Element(legend_html))
    return m

m = create_map(df)
m.save(os.path.splitext(output_notebook)[0] + '.html')
m
"""

cells.append({
    "cell_type": "code",
    "execution_count": None,
    "metadata": {},
    "outputs": [],
    "source": load_and_map_code
})

cells.append({
    "cell_type": "code",
    "execution_count": None,
    "metadata": {},
    "outputs": [],
    "source": """# Heatmap with timeline slider
df['year_month'] = df['date'].dt.to_period('M')
time_index = sorted(df['year_month'].unique().astype(str))
heat_data = []
for period in time_index:
    subset = df[df['year_month'] == period]
    heat_data.append(subset[['lat','lon','price']].values.tolist())

m_heat = folium.Map(location=[df['lat'].mean(), df['lon'].mean()], zoom_start=10)
HeatMapWithTime(heat_data, index=time_index, auto_play=False, max_opacity=0.7).add_to(m_heat)
m_heat
"""
})

cells.append({
    "cell_type": "code",
    "execution_count": None,
    "metadata": {},
    "outputs": [],
    "source": """# Line graph showing average monthly price trend
df_monthly = df.set_index('date').resample('M')['price'].mean()
ax = df_monthly.plot(marker='o', figsize=(8,4))
ax.set_ylabel('Average Price (£)')
ax.set_title('Average Property Price Over Time')
ax.figure
"""
})

notebook = {
    "cells": cells,
    "metadata": {
        "kernelspec": {
            "display_name": "Python 3",
            "language": "python",
            "name": "python3"
        },
        "language_info": {
            "name": "python",
            "version": "3.11"
        }
    },
    "nbformat": 4,
    "nbformat_minor": 2
}

with open(output_notebook, 'w') as f:
    json.dump(notebook, f, indent=2)
