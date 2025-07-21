# Trafford House Price Map

This project generates a mobile friendly web page showing property transactions in Trafford on an interactive Leaflet map.

## Requirements
- Python 3 with the packages `pandas`, `folium` and `pgeocode` installed.

## Usage
Run the script to build the website locally:

```bash
python map_website.py
```

This loads the data from `trafford prices.csv`, geocodes the postcodes and creates `site/index.html` with the map. Open this file in a web browser (desktop or mobile) to view and interact with the map. You can zoom and pan around the data points.

## GitHub Pages

The repository includes a workflow that automatically runs `map_website.py` and
publishes the contents of the `site/` directory to GitHub Pages whenever changes
are pushed to the `main` branch. After pushing, visit your repository's Pages
URL to see the interactive map online.
