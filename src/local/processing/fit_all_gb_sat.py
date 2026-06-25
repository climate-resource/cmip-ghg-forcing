""""

Calculate scaling factor for all ground based datasets
"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import xarray as xr

plots_path = "/home/anna_lanteri/code/cmip-ghg-forcing/plots/"
AGAGE_data_path = Path("/home/anna_lanteri/data/ground_based_data/AGAGE/")
NOAA_data_path = Path(
    "/home/anna_lanteri/data/ground_based_data/NOAA/ch4_surface-insitu_ccgg_netCDF/"
)
sat_path = "/home/anna_lanteri/data/satellite_data/OBS4MIPs/"

def extract_ground_data(gb):
    """Return (times, values) regardless of dataset structure."""
    if "mf" in gb:
        # AGAGE style
        times = gb.time.values
        values = gb["mf"].values / 1e9

    elif "value" in gb:
        # obs dimension style
        times = gb["time"].values
        values = gb["value"].values / 1e9

    else:
        raise ValueError("Unknown ground dataset format")  # noqa: TRY003

    return times, values

def simple_fit(gb, sat):
    """Perform simple fit"""
    # fit gb = sf * sat
    return (np.sum(sat * gb) / np.sum(sat**2))

def lat_fit(gb, sat, lat):
    """
    Fit:

        gb = (a + b*lat) * sat

    Returns
    -------
    a, b
    """
    X = np.column_stack([
        sat,
        sat * lat,
    ])

    coef, *_ = np.linalg.lstsq(X, gb, rcond=None)

    return coef

def get_sat_data_at_ground_coords(gb_data,
                                  sat_data,
                                  lat_name = 'inlet_latitude',
                                  lon_name = 'inlet_longitude'):
    """Return sat data overlapping with coordinates of ground data"""
    gb_lat = gb_data.attrs[lat_name]
    gb_lon = gb_data.attrs[lon_name]

    aligned = sat_data.sel(lat=gb_lat, lon=gb_lon, method="nearest")
    return set_sat_time_at_start_of_month(aligned)


def set_sat_time_at_start_of_month(sat_data):
    """Return sat data with timestamps at beginning of month"""
    return sat_data.assign_coords(
        time=pd.DatetimeIndex(sat_data.time.values).to_period("M").to_timestamp()
    )

def plot_fit(sat, gb, sf, station_name):
    """Plot the fit"""
    plt.scatter(sat, gb, label="measurements")

    x = np.linspace(sat.min(), sat.max(), 100)
    plt.plot(x, sf * x, "r-", label=f"fit: gb = {sf:.3f} * sat")

    plt.xlabel("Satellite XCH4")
    plt.ylabel(f"{station_name} CH4")
    plt.legend()
    plt.grid(True)

    plt.savefig(f"{plots_path}{station_name}_vs_sat_fit.png", dpi=300)
    plt.close()


def get_matching_data(gb_data, sat_data):
    """Return the datasets where they match in time"""
    valid_gb_times = gb_data.time.values[~np.isnan(gb_data["mf"].values)]

    valid_sat_times = sat_data.time.values[~np.isnan(sat_data["xch4"].values)]

    common_times = np.intersect1d(valid_gb_times, valid_sat_times)

    gb_matched = gb_data["mf"].sel(time=common_times) / 1e9

    sat_matched = sat_data["xch4"].sel(time=common_times)

    return gb_matched, sat_matched

def get_matching_data_generic(gb, sat):
    """Return matched satellite and ground observations."""
    sat_ground = get_sat_data_at_ground_coords(gb, sat)

    gb_times, gb_values = extract_ground_data(gb)

    valid_sat = np.isfinite(sat_ground["xch4"].values)

    sat_times = sat_ground.time.values[valid_sat]
    sat_values = sat_ground["xch4"].values[valid_sat]

    common_times = np.intersect1d(gb_times, sat_times)

    gb_mask = np.isin(gb_times, common_times)
    sat_mask = np.isin(sat_times, common_times)

    return sat_values[sat_mask], gb_values[gb_mask]

def get_all_matched_data(files, sat_data):
    """Get all matched satellite and ground obs"""
    all_sat = []
    all_gb = []
    all_lat = []

    for file in files:
        ds = xr.open_dataset(file)

        try:
            station = get_station_code(file)

            if station == "cmo":
                continue

            sat_ch4, gb_ch4 = get_matching_data_generic(ds, sat_data)

            all_sat.append(np.asarray(sat_ch4).ravel())
            all_gb.append(np.asarray(gb_ch4).ravel())

            n = len(sat_ch4)
            station_lat = float(ds.attrs["inlet_latitude"])

            all_lat.append(
                np.full(n, station_lat)
            )

        finally:
            ds.close()

    all_sat = np.concatenate(all_sat)
    all_gb = np.concatenate(all_gb)
    all_lat = np.concatenate(all_lat)

    mask = np.isfinite(all_sat) & np.isfinite(all_gb)

    return all_sat[mask], all_gb[mask], all_lat[mask]


def get_all_NOAA_matched_data(gb_files, sat):
    """Get all matched satellite and ground obs"""
    all_sat = []
    all_gb = []
    all_lat = []

    for file in gb_files:
        gb = xr.open_dataset(file)

        try:
            sat_ground = get_sat_data_at_ground_coords(gb, sat,
                                                lat_name='site_latitude',
                                                lon_name='site_longitude')
            mask_ground = make_sat_times_mask(gb, sat_ground)
            gb_matched = gb["value"][mask_ground] / 1e9

            mask_sat = make_ground_times_mask(gb, sat_ground)
            sat_matched = sat_ground["xch4"][mask_sat].dropna(dim="time").squeeze().values
            all_gb.append(np.asarray(gb_matched).ravel())
            all_sat.append(np.asarray(sat_matched).ravel())

            n = len(sat_matched)
            station_lat = float(gb.attrs["site_latitude"])

            all_lat.append(
                np.full(n, station_lat)
            )

        finally:
            gb.close()

    all_sat = np.concatenate(all_sat)
    all_gb = np.concatenate(all_gb)
    all_lat = np.concatenate(all_lat)

    mask = np.isfinite(all_sat) & np.isfinite(all_gb)

    return all_sat[mask], all_gb[mask], all_lat[mask]

def make_sat_times_mask(gb_data, sat_data):
    """Return mask of valid times with sat values"""
    valid_sat_times = sat_data.time.values[~np.isnan(sat_data["xch4"].values)]
    gb_time = gb_data["time"]

    return np.isin(gb_time, valid_sat_times)


def make_ground_times_mask(gb_data, sat_data):
    """Return mask of valid times with ground values"""
    valid_ground_times = gb_data.time.values[~np.isnan(gb_data["time"].values)]
    sat_time = sat_data["time"]

    return np.isin(sat_time, valid_ground_times)


def get_station_code(filename):
    """Return station code after first _"""
    return Path(filename).stem.split("_")[1]


def plot_fit_to_obs(obs, fit, title = 'observed_vs_fitted_latfit'):
    """Plot fit against observations"""
    plt.figure()
    plt.scatter(
        obs,
        fit,
        s=5,
        alpha=0.5,
    )
    lims = [
        min(obs.min(), fit.min()),
        max(obs.max(), fit.max()),
    ]
    plt.plot(
        lims,
        lims,
        "k--",
    )
    plt.xlabel("Observed GB")
    plt.ylabel("Fitted GB")
    plt.savefig(
        f"{plots_path}{title}.png",
        dpi=300,
    )
    plt.close()


if __name__ == "__main__":
    sat_default = 1.0e20

    # OBD4MIPs
    sat_data = xr.open_dataset(
        f"{sat_path}/200301_202312-C3S-L3_XCH4-GHG_PRODUCTS-MERGED-MERGED-OBS4MIPS-MERGED-v4.6.nc"
    )
    sat_data["xch4"] = sat_data["xch4"].where(sat_data["xch4"] != sat_default, np.nan)

    # AGAGE datasets
    agage_files = sorted(AGAGE_data_path.glob("*-20251230.nc"))
    agage_files.append(
        Path(
            "/home/anna_lanteri/data/ground_based_data/AGAGE/agage_cgo_ch4_monthly-baseline-20250123.nc"
        )
    )
    # NOAA dataset
    noaa_files = sorted(NOAA_data_path.glob("ch4_*_MonthlyData.nc"))

    all_AGAGE_sat, all_AGAGE_gb, all_AGAGE_lat = get_all_matched_data(agage_files, sat_data)

    sf = simple_fit(all_AGAGE_gb, all_AGAGE_sat)
    if not np.isnan(sf):
        plot_fit(all_AGAGE_sat, all_AGAGE_gb, sf, "AGAGE_all")
    print(f"Global scaling factor for AGAGE = {sf}")

    all_NOAA_sat, all_NOAA_gb, all_NOAA_lat = get_all_NOAA_matched_data(noaa_files, sat_data)

    sf_noaa = simple_fit(all_NOAA_gb, all_NOAA_sat)
    if not np.isnan(sf_noaa):
        plot_fit(all_NOAA_sat, all_NOAA_gb, sf_noaa, "NOAA_all")
    print(f"Global scaling factor for AGAGE = {sf_noaa}")

    all_sat_combined = np.concatenate([all_AGAGE_sat, all_NOAA_sat])

    # All data combined

    all_gb_combined = np.concatenate([all_AGAGE_gb, all_NOAA_gb])

    mask = np.isfinite(all_sat_combined) & np.isfinite(all_gb_combined)

    all_sat_combined = all_sat_combined[mask]
    all_gb_combined = all_gb_combined[mask]

    sf = simple_fit(all_gb_combined, all_sat_combined)
    if not np.isnan(sf):
        plot_fit(all_sat_combined, all_gb_combined, sf, "all")
    print(f"Global scaling factor for AGAGE and NOAA = {sf}")

    # Checking the residuals to see if lat matters
    all_lat = np.concatenate([all_AGAGE_lat, all_NOAA_lat])
    all_lat = np.concatenate([all_AGAGE_lat, all_NOAA_lat])[mask]

    residual_all = all_gb_combined - sf * all_sat_combined

    plt.scatter(all_lat, residual_all)
    plt.xlabel("Latitude")
    plt.ylabel("Residual")
    plt.savefig(f"{plots_path}residuals_lineat_fit_all_gb_lat.png", dpi=300)
    plt.close()

    ## Fit depending on lat


    a, b = lat_fit(
        all_gb_combined,
        all_sat_combined,
        all_lat,
    )

    print(f"sf(lat) = {a:.6f} + {b:.6e} * lat")

    residual_old = (
        all_gb_combined
        - sf * all_sat_combined
    )

    residual_new = (
        all_gb_combined
        - (a + b*all_lat) * all_sat_combined
    )

    print(np.std(residual_old))
    print(np.std(residual_new))

    gb_fit = (a + b * all_lat) * all_sat_combined

    plot_fit(all_gb_combined, gb_fit, title = 'observed_vs_fitted_latfit')



