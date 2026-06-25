"""

Point selection

Brutal selection of points that have both satellite value and
ground based measurements from NOAA

"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import xarray as xr

plots_path = "/home/anna_lanteri/code/cmip-ghg-forcing/plots/"
data_path = Path(
    "/home/anna_lanteri/data/ground_based_data/NOAA/ch4_surface-insitu_ccgg_netCDF/"
)
sat_path = "/home/anna_lanteri/data/satellite_data/OBS4MIPs/"

## Mauna Loa, Hawaii, 01/1987
## Mauna Kea, Hawaii, 12/2022
# American Samoa, 04/2025
# Utqiaġvik, Alaska, 04/1987


def get_sat_data_at_ground_coords(gb_data: xr.Dataset, sat_data):
    """Return sat data at ground coords"""
    gb_lat = gb_data.attrs["site_latitude"]
    gb_lon = gb_data.attrs["site_longitude"]

    aligned = sat_data.sel(lat=gb_lat, lon=gb_lon, method="nearest")
    return set_sat_time_at_start_of_month(aligned)


def set_sat_time_at_start_of_month(sat_data):
    """Set timestamp of satellite at the beginning of the month"""
    return sat_data.assign_coords(
        time=pd.DatetimeIndex(sat_data.time.values).to_period("M").to_timestamp()
    )


def make_sat_times_mask(gb_data, sat_data):
    """Maybe not useful"""
    valid_sat_times = sat_data.time.values[~np.isnan(sat_data["xch4"].values)]
    gb_time = gb_data["time"]

    return np.isin(gb_time, valid_sat_times)


def make_ground_times_mask(gb_data, sat_data):
    """Like I thin kI have a better way to do this somewhere"""
    valid_ground_times = gb_data.time.values[~np.isnan(gb_data["time"].values)]
    sat_time = sat_data["time"]

    return np.isin(sat_time, valid_ground_times)


def plot_matching_data(gb_data, sat_data, station_name):
    """Plot matching data of sat and ground based obs"""
    sat_data = get_sat_data_at_ground_coords(gb_data, sat_data)

    mask = make_sat_times_mask(gb_data, sat_data)

    gb_time = gb_data["time"][mask]
    gb_ch4 = gb_data["value"][mask] / 1e9

    sat_data["xch4"].plot(
        label=f"sat over {station_name} coords",
        marker="o",
        linestyle="None",
    )
    plt.plot(
        gb_time,
        gb_ch4,
        label=f"{station_name}",
        marker="o",
        linestyle="None",
    )
    plt.legend()
    plt.title(f"Comparing OBS4MIPs over {station_name} coords and ground based data")
    plt.savefig(f"{plots_path}sat_over_{station_name}_and_gb.png", format="png")
    plt.close()


# TODO: fix it so it can run for NOAA data, with time not a coordinate
def get_matching_data(gb_data, sat_data):
    """Return the datasets where they match in time"""
    valid_gb_times = gb_data["time"].values[~np.isnan(gb_data["value"].values)]

    valid_sat_times = sat_data.time.values[~np.isnan(sat_data["xch4"].values)]

    common_times = np.intersect1d(valid_gb_times, valid_sat_times)

    gb_matched = gb_data["value"].sel(time=common_times) / 1e9

    sat_matched = sat_data["xch4"].sel(time=common_times)

    return gb_matched, sat_matched


def scatter_plot(gb_data, sat_data, station_name):
    """Scatter plot of sat vs gd data"""
    sat_data = get_sat_data_at_ground_coords(gb_data, sat_data)

    # mask_ground = make_sat_times_mask(gb_data, sat_data)
    # gb_ch4 = gb_data["value"][mask_ground].dropna(dim="obs") / 1e9

    # mask_sat = make_ground_times_mask(gb_data, sat_data)
    # sat_data = sat_data["xch4"][mask_sat].dropna(dim="time")
    gb_ch4, sat_ch4 = get_matching_data(gb_data, sat_data)

    plt.scatter(gb_ch4, sat_ch4, alpha=0.7)

    plt.xlabel(f"{station_name} CH4")
    plt.ylabel("Satellite XCH4")
    plt.title(f"Satellite vs {station_name} CH4")
    plt.grid(True)
    plt.savefig(f"{plots_path}sat_vs_{station_name}_scatter.png", dpi=300)
    plt.close()


def get_station_code(filename):
    """Return station code after first _"""
    return Path(filename).stem.split("_")[1]


if __name__ == "__main__":
    sat_default = 1.0e20

    # OBD4MIPs
    sat_data = xr.open_dataset(
        f"{sat_path}/200301_202312-C3S-L3_XCH4-GHG_PRODUCTS-MERGED-MERGED-OBS4MIPS-MERGED-v4.6.nc"
    )
    sat_data["xch4"] = sat_data["xch4"].where(sat_data["xch4"] != sat_default, np.nan)

    ## Plot the comparison plots
    files = sorted(data_path.glob("ch4_*_MonthlyData.nc"))

    for file in files:
        ds = xr.open_dataset(file)
        station_name = get_station_code(file)
        plot_matching_data(ds, sat_data, station_name=station_name)
        scatter_plot(ds, sat_data, station_name=station_name)
