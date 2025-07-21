import os
import pandas as pd
import folium
from folium.plugins import MarkerCluster, Fullscreen
import pgeocode

COLUMNS = [
    'transaction_id','price','date','postcode','property_type','old_new',
    'duration','paon','saon','street','locality','town','district',
    'county','ppd_category','record_status'
]

CSV_FILE = 'trafford prices.csv'


def load_data(csv_file=CSV_FILE):
    df = pd.read_csv(csv_file, header=None, names=COLUMNS)
    df['price'] = df['price'].astype(float)
    df['date'] = pd.to_datetime(df['date'])
    nomi = pgeocode.Nominatim('gb')
    df[['lat','lon']] = df['postcode'].apply(lambda x: nomi.query_postal_code(x)[['latitude','longitude']])
    df = df.dropna(subset=['lat','lon'])
    quantiles = pd.qcut(df['price'], 5, labels=False)
    colours = ['blue','green','yellow','orange','red']
    df['colour'] = quantiles.apply(lambda x: colours[int(x)])
    return df


def create_map(df):
    m = folium.Map(
        location=[df['lat'].mean(), df['lon'].mean()],
        zoom_start=11,
        tiles='cartodbpositron',
        control_scale=True,
    )
    Fullscreen().add_to(m)
    marker_cluster = MarkerCluster().add_to(m)
    for _, row in df.iterrows():
        popup_text = f"{row['street']} {row['postcode']}<br>£{row['price']:,}<br>{row['date'].date()}"
        folium.CircleMarker(
            location=[row['lat'], row['lon']],
            radius=5,
            color=row['colour'],
            fill=True,
            fill_color=row['colour'],
            popup=folium.Popup(popup_text, max_width=250)
        ).add_to(marker_cluster)
    return m


def main():
    df = load_data()
    m = create_map(df)
    output_dir = 'site'
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, 'index.html')
    m.save(output_path)
    print(f"Map saved to {output_path}")


if __name__ == '__main__':
    main()
