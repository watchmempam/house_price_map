# Trafford House Price Map

This project generates a mobile friendly web page showing property transactions in Trafford on an interactive Leaflet map.

## Requirements
- Python 3 with the packages `pandas`, `folium` and `pgeocode` installed.

## Usage
Run the script to build the website:

```bash
python map_website.py
```

This loads the data from `trafford prices.csv`, geocodes the postcodes and creates `site/index.html` with the map. The file automatically opens in your default browser so you can zoom and pan around the data points on desktop or mobile.
