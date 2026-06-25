"""
Visualization tools for AGAGE data
"""
from pathlib import Path

import cartopy.crs as ccrs  # type: ignore
import cartopy.feature as cfeature  # type: ignore
import matplotlib.pyplot as plt
import xarray as xr

data_path = Path('/home/anna_lanteri/data/ground_based_data/AGAGE/')
plots_path = Path('/home/anna_lanteri/code/cmip-ghg-forcing/plots/')

def plot_trends(files, title, save_file_name):
    """Plot trends of AGAGE stations"""
    _, ax = plt.subplots(figsize=(12, 6))

    for file in files:
       ds = xr.open_dataset(file)
       label = file.stem

       ds['mf'].plot(ax=ax, label=label)

       ds.close()

    ax.set_title(title)
    ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()

    plt.savefig(plots_path / f"{save_file_name}.png", dpi=300)
    plt.close()

def plot_station_locations(files, title, save_file_name):
    """Plot location of stations"""
    stations = []

    for file in files:
        ds = xr.open_dataset(file)

        lat = float(ds.attrs.get('inlet_latitude'))
        lon = float(ds.attrs.get('inlet_longitude'))

        stations.append({
            'name': file.stem,
            'lat': lat,
            'lon': lon
        })

        ds.close()

    print(len(stations))

    #fig = plt.figure(figsize=(14, 7))
    ax = plt.axes(projection=ccrs.PlateCarree())

    ax.set_global()
    ax.coastlines()
    ax.add_feature(cfeature.BORDERS, linewidth=0.5)
    ax.add_feature(cfeature.LAND, facecolor='lightgray')
    ax.add_feature(cfeature.OCEAN, facecolor='white')

    for station in stations:
        ax.scatter(
            station['lon'],
            station['lat'],
            s=50,
            color='red',
            transform=ccrs.PlateCarree()
        )

        ax.text(
            station['lon'] + 2,
            station['lat'] + 2,
            station['name'],
            fontsize=12,
            transform=ccrs.PlateCarree()
        )

    plt.title(title)
    plt.savefig(plots_path / f"{save_file_name}.png",
                dpi=300, bbox_inches='tight')
    plt.close()

# We take only the most recent version of each of the stations.
# The only station excluded is cgo so I add it manually
some_files = sorted(data_path.glob('*-20251230.nc'))
some_files.append(Path('/home/anna_lanteri/data/ground_based_data/AGAGE/agage_cgo_ch4_monthly-baseline-20250123.nc'))

plot_trends(some_files, title = 'AGAGE trends', save_file_name = 'AGAGE_most_recent')

all_files = sorted(data_path.glob('*.nc'))
plot_trends(all_files, title = 'AGAGE trends', save_file_name = 'AGAGE_all')

plot_station_locations(some_files,
                      title='AGAGE station locations',
                      save_file_name='AGAGE_locations')

