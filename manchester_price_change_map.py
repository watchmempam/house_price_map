import argparse
from pathlib import Path
import pandas as pd
import folium
import pgeocode

INCREASE_START = (144, 238, 144)  # light green
INCREASE_END = (0, 100, 0)       # dark green
DECREASE_START = (255, 204, 204) # light red
DECREASE_END = (139, 0, 0)       # dark red


def interp_color(start, end, ratio: float) -> str:
    """Interpolate between two RGB colors and return hex string."""
    ratio = max(0.0, min(1.0, ratio))
    r = int(start[0] + (end[0] - start[0]) * ratio)
    g = int(start[1] + (end[1] - start[1]) * ratio)
    b = int(start[2] + (end[2] - start[2]) * ratio)
    return f"#{r:02x}{g:02x}{b:02x}"


def trimmed_mean(series, proportion: float = 0.1):
    """Return the mean of `series` excluding the top and bottom proportion."""
    if series.empty:
        return None
    low = series.quantile(proportion)
    high = series.quantile(1 - proportion)
    trimmed = series[(series >= low) & (series <= high)]
    return trimmed.mean() if not trimmed.empty else None


def load_data(path: Path) -> pd.DataFrame:
    cols = [
        "transaction_id",
        "price",
        "date",
        "postcode",
        "property_type",
        "old_new",
        "duration",
        "paon",
        "saon",
        "street",
        "locality",
        "town",
        "district",
        "county",
        "ppd_cat",
        "record",
    ]
    df = pd.read_csv(path, header=None, names=cols)
    df["price"] = df["price"].astype(float)
    df["date"] = pd.to_datetime(df["date"])
    df["year"] = df["date"].dt.year
    df["prefix"] = df["postcode"].str.split().str[0]
    return df


def geocode_prefixes(df: pd.DataFrame) -> dict:
    nomi = pgeocode.Nominatim("gb")
    sample = df.groupby("prefix")["postcode"].first().to_dict()
    coords = {}
    for prefix, pc in sample.items():
        row = nomi.query_postal_code(pc)
        coords[prefix] = (row["latitude"], row["longitude"])
    return coords


def create_map(df: pd.DataFrame, coords: dict, year1: int, year2: int) -> folium.Map:
    avg = df.groupby(["prefix", "year"])["price"].apply(trimmed_mean).unstack()
    change = avg[year2] - avg[year1]
    percent = change / avg[year1] * 100
    inc_max = percent.max() if (percent > 0).any() else 0
    dec_min = percent.min() if (percent < 0).any() else 0

    m = folium.Map(location=[53.4808, -2.2426], zoom_start=10)
    for prefix, pct in percent.dropna().items():
        lat, lon = coords.get(prefix, (53.4808, -2.2426))
        diff = change.get(prefix, 0)
        if pct >= 0:
            ratio = 0 if inc_max == 0 else pct / inc_max
            color = interp_color(INCREASE_START, INCREASE_END, ratio)
        else:
            ratio = 0 if dec_min == 0 else pct / dec_min  # dec_min is negative
            color = interp_color(DECREASE_START, DECREASE_END, ratio)
        folium.CircleMarker(
            location=[lat, lon],
            radius=8,
            color=color,
            fill=True,
            fill_color=color,
            popup=f"{prefix}: £{diff:+.0f} ({pct:+.2f}%)",
        ).add_to(m)
    return m


def main():
    parser = argparse.ArgumentParser(description="Generate Manchester price change map")
    parser.add_argument("year1", type=int, help="First year")
    parser.add_argument("year2", type=int, help="Second year")
    parser.add_argument(
        "--csv",
        default="2019 to today manc.csv",
        help="CSV file with price data",
    )
    parser.add_argument(
        "--output",
        default="manchester_price_change_map.html",
        help="Output HTML file",
    )
    args = parser.parse_args()

    data_path = Path(args.csv)
    if not data_path.exists():
        raise SystemExit(f"CSV not found: {data_path}")

    df = load_data(data_path)

    available_years = sorted(df["year"].unique())
    if args.year1 not in available_years or args.year2 not in available_years:
        raise SystemExit(f"Years must be within {available_years}")

    coords = geocode_prefixes(df)
    m = create_map(df, coords, args.year1, args.year2)
    m.save(args.output)
    print(f"Map saved to {args.output}")


if __name__ == "__main__":
    main()
