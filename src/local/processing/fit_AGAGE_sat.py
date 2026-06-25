"""
Fit sat to AGAGE

"""
# TODO: deal with the huge amount of repetition

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import xarray as xr

plots_path = "/home/anna_lanteri/code/cmip-ghg-forcing/plots/"
data_path = Path("/home/anna_lanteri/data/ground_based_data/AGAGE/")
sat_path = "/home/anna_lanteri/data/satellite_data/OBS4MIPs/"


def simple_fit(sat, gb):
    """Perform simple fit"""
    # fit gb = sf * sat
    return (np.sum(sat * gb) / np.sum(sat**2)).values


# gb_fit = sf * sat
# epsilon = mlo_ch4_matched - gb_fit


def get_sat_data_at_ground_coords(gb_data, sat_data):
    """Return sat data overlapping with coordinates of ground data"""
    gb_lat = gb_data.attrs["inlet_latitude"]
    gb_lon = gb_data.attrs["inlet_longitude"]

    aligned = sat_data.sel(lat=gb_lat, lon=gb_lon, method="nearest")
    return set_sat_time_at_start_of_month(aligned)


def set_sat_time_at_start_of_month(sat_data):
    """Return sat data with timestamps at beginning of month"""
    return sat_data.assign_coords(
        time=pd.DatetimeIndex(sat_data.time.values).to_period("M").to_timestamp()
    )


def plot_fit(sat, gb, station_name):
    """Plot the fit"""
    sat = get_sat_data_at_ground_coords(gb, sat)

    gb_ch4, sat_ch4 = get_matching_data(gb, sat)
    gb_ch4 = gb_ch4.squeeze()
    sat_ch4 = sat_ch4.squeeze()

    sf = simple_fit(sat_ch4, gb_ch4)

    print(f"Scaling factor sf = {sf}")

    plt.scatter(sat_ch4, gb_ch4, label="measurements")

    x = np.linspace(sat_ch4.min().values, sat_ch4.max().values, 100)
    plt.plot(x, sf * x, "r-", label=f"fit: gb = {sf:.3f} * sat")

    plt.xlabel("Satellite XCH4")
    plt.ylabel(f"{station_name} CH4")
    plt.legend()
    plt.grid(True)

    plt.savefig(f"{plots_path}AGAGE_{station_name}_vs_sat_fit.png", dpi=300)
    plt.close()


def get_matching_data(gb_data, sat_data):
    """Return the datasets where they match in time"""
    valid_gb_times = gb_data.time.values[~np.isnan(gb_data["mf"].values)]

    valid_sat_times = sat_data.time.values[~np.isnan(sat_data["xch4"].values)]

    common_times = np.intersect1d(valid_gb_times, valid_sat_times)

    gb_matched = gb_data["mf"].sel(time=common_times) / 1e9

    sat_matched = sat_data["xch4"].sel(time=common_times)

    return gb_matched, sat_matched


def get_station_code(filename):
    """Return station code after first _"""
    return Path(filename).stem.split("_")[1]


if __name__ == "__main__":
    sat_default = 1.0e20

    # AGAGE datasets
    some_files = sorted(data_path.glob("*-20251230.nc"))
    some_files.append(
        Path(
            "/home/anna_lanteri/data/ground_based_data/AGAGE/agage_cgo_ch4_monthly-baseline-20250123.nc"
        )
    )

    # OBD4MIPs
    sat_data = xr.open_dataset(
        f"{sat_path}/200301_202312-C3S-L3_XCH4-GHG_PRODUCTS-MERGED-MERGED-OBS4MIPS-MERGED-v4.6.nc"
    )
    sat_data["xch4"] = sat_data["xch4"].where(sat_data["xch4"] != sat_default, np.nan)

    for file in some_files:
        ds = xr.open_dataset(file)
        ds["mf"] = ds["mf"].where(ds["mf"] > 0, np.nan)
        station = get_station_code(file)
        print(station)
        if station != "cmo":
            plot_fit(sat_data, ds, station)

        ds.close()
