import json

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
    "source": [
        "# Install dependencies if running in a fresh environment\n",
        "import sys, subprocess\n",
        "for pkg in ['pandas','folium','pgeocode','numpy']:\n",
        "    if pkg not in sys.modules:\n",
        "        try:\n",
        "            __import__(pkg)\n",
        "        except ImportError:\n",
        "            subprocess.check_call([sys.executable, '-m', 'pip', 'install', pkg])\n"
    ]
})

cells.append({
    "cell_type": "code",
    "execution_count": None,
    "metadata": {},
    "outputs": [],
    "source": [
        "import pandas as pd\n",
        "import folium\n",
        "import pgeocode\n",
        "import numpy as np\n"
    ]
})

cells.append({
    "cell_type": "code",
    "execution_count": None,
    "metadata": {},
    "outputs": [],
    "source": [
        "# Load the CSV file\n",
        "columns = ['transaction_id', 'price', 'date', 'postcode', 'property_type', 'old_new', 'duration', ",
        "'paon', 'saon', 'street', 'locality', 'town', 'district', 'county', 'ppd_cat', 'record_status']\n",
        "df = pd.read_csv('ppd_data (2).csv', header=None, names=columns)\n",
        "df['price'] = df['price'].astype(float)\n",
        "\n",
        "# Geocode postcodes to get latitude and longitude\n",
        "nomi = pgeocode.Nominatim('gb')\n",
        "df[['lat', 'lon']] = df['postcode'].apply(lambda x: nomi.query_postal_code(x)[['latitude','longitude']])\n",
        "df = df.dropna(subset=['lat','lon'])\n",
        "\n",
        "# Bin prices into 5 quantiles\n",
        "quantiles = pd.qcut(df['price'], 5, labels=False)\n",
        "colours = ['blue', 'green', 'yellow', 'orange', 'red']\n",
        "df['colour'] = quantiles.apply(lambda x: colours[int(x)])\n",
        "\n",
        "# Create the map centred on the mean location\n",
        "m = folium.Map(location=[df['lat'].mean(), df['lon'].mean()], zoom_start=10)\n",
        "\n",
        "# Plot each property\n",
        "for _, row in df.iterrows():\n",
        "    popup_text = f\"{row['street']} {row['postcode']}<br>£{row['price']:,}<br>{row['date']}\"\n",
        "    folium.CircleMarker(\n",
        "        location=[row['lat'], row['lon']],\n",
        "        radius=5,\n",
        "        color=row['colour'],\n",
        "        fill=True,\n",
        "        fill_color=row['colour'],\n",
        "        popup=folium.Popup(popup_text, max_width=250)\n",
        "    ).add_to(m)\n",
        "\n",
        "# Add a legend\n",
        "legend_html = '''<div style=\"position: fixed; bottom: 50px; left: 50px; width: 150px;\n",
        "height: 130px; border:2px solid grey; background-color:white; z-index:9999; font-size:14px;\">\n",
        "&nbsp;<b>Price Range</b><br>\n",
        "&nbsp;<i style=\"background:blue;\">&nbsp;&nbsp;&nbsp;&nbsp;</i>&nbsp;Lowest<br>\n",
        "&nbsp;<i style=\"background:green;\">&nbsp;&nbsp;&nbsp;&nbsp;</i><br>\n",
        "&nbsp;<i style=\"background:yellow;\">&nbsp;&nbsp;&nbsp;&nbsp;</i><br>\n",
        "&nbsp;<i style=\"background:orange;\">&nbsp;&nbsp;&nbsp;&nbsp;</i><br>\n",
        "&nbsp;<i style=\"background:red;\">&nbsp;&nbsp;&nbsp;&nbsp;</i>&nbsp;Highest\n",
        "</div>'''\n",
        "m.get_root().html.add_child(folium.Element(legend_html))\n",
        "\n",
        "m.save('house_price_map.html')\n",
        "m\n"
    ]
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

with open('house_price_map.ipynb', 'w') as f:
    json.dump(notebook, f, indent=2)
