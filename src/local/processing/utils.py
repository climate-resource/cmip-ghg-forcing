"""
Utils for processing data
"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import xarray as xr

plots_path = "/home/anna_lanteri/code/cmip-ghg-forcing/plots/"

#########################
## DATA PROCESSING UTILS
#########################
sat_default = 1.0e20


def get_sat_data(gas:str):
    """Get sat data of given specie"""
    sat_path = "/home/anna_lanteri/data/satellite_data/OBS4MIPs/"
    file_end = "-GHG_PRODUCTS-MERGED-MERGED-OBS4MIPS-MERGED-v4.6.nc"

    gas = "x" + gas
    if gas == "xch4":
        specie_file_name = "XCH4"
    elif gas == "xco2":
        specie_file_name = "XCO2"

    sat_data = xr.open_dataset(
        f"{sat_path}/200301_202312-C3S-L3_{specie_file_name}{file_end}"
    )
    sat_data[gas] = sat_data[gas].where(sat_data[gas] != sat_default, np.nan)
    sat_data[gas] = sat_data[gas].where(sat_data[gas] > 0, np.nan)

    return sat_data


def get_agage_files(gas:str):
    """Get AGAGE data for a given specie"""
    agage_data_path = Path("/home/anna_lanteri/data/ground_based_data/AGAGE/")

    agage_files = sorted(agage_data_path.glob("*" + gas + "*-20251230.nc"))
    agage_files.append(
        agage_data_path / f"agage_cgo_{gas}_monthly-baseline-20250123.nc"
    )
    return agage_files


def get_noaa_files(gas:str):
    """Get NOAA data for a given specie"""
    NOAA_data_path = Path(
        f"/home/anna_lanteri/data/ground_based_data/NOAA/{gas}_surface-insitu_ccgg_netCDF/"
    )
    return sorted(NOAA_data_path.glob(f"{gas}_*_MonthlyData.nc"))

def get_noaa_flask_files(gas:str):
    """Get NOAA flask data for a given specie"""
    method = "flask"

    data_path = Path(
        f"/home/anna_lanteri/data/ground_based_data/NOAA/{gas}_surface-{method}_ccgg_netCDF/"
    )

    return sorted(data_path.glob(f"{gas}_*_event.nc"))

def filter_qc(
    ds,
    filter_config,
    qc_var="qcflag"
):
    """
    Filter an xarray Dataset based on NOAA 3-character QC flags.
    """
    # Convert bytes -> unicode strings if needed
    flags = ds[qc_var].astype(str)

    mask = xr.ones_like(flags, dtype=bool)

    if filter_config['reject']:
        mask &= flags.str[0] == "."

    if filter_config['selection']:
        mask &= flags.str[1] == "."

    if filter_config['information']:
        mask &= flags.str[2] == "."

    return ds.where(mask, drop=True)


filter_config = {
    'reject':True,
    'selection':False,
    'information':False,
}



def get_scaling(gas:str):
    """Scaling factor for the gas between satellite and gb"""
    if gas == "ch4":
        scaling = 1e9
    elif gas == "co2":
        scaling = 1e6
    else:
        raise ValueError("gas_not_supported")
    return scaling


def get_matched_data(gb:xr.Dataset, sat:xr.Dataset, gas:str, flask:bool= False):
    """Get matched data for one set of gb data"""
    scaling = get_scaling(gas)

    sat["x" + gas] = sat["x" + gas].where(sat["x" + gas] >= 0, np.nan)
    sat["x" + gas] = sat["x" + gas].where(sat["x" + gas] != sat_default, np.nan)

    if "mf" in gb:
        # AGAGE style
        lat_name = "inlet_latitude"
        sat_matched, gb_matched = get_matching_data(gb, sat, gas=gas)
        station_lat = float(gb.attrs[lat_name])

        return (
            gb_matched,
            sat_matched.squeeze(),
            station_lat,
        )
    elif "value" in gb and not flask:
        # NOAA gb style
        gb["value"] = gb["value"].where(gb["value"] >= 0, np.nan)

        lat_name = "site_latitude"
        station_lat = float(gb.attrs[lat_name])

        sat_ground = get_sat_data_at_ground_coords(gb, sat)

        mask_ground = make_sat_times_mask(gb, sat_ground, gas)
        gb_matched = gb["value"][mask_ground] / scaling
        mask_sat = make_ground_times_mask(gb, sat_ground)
        sat_matched = (
            sat_ground["x" + gas][mask_sat].dropna(dim="time").squeeze().values
        )
        print("checking selection: should be the same")
        print(sat_matched.size)
        print(gb_matched.size)

        return (
            gb_matched.values,
            sat_matched,
            station_lat,
        )
    elif "value" in gb and flask:
        # NOAA flask data
        gb["value"] = gb["value"].where(gb["value"] > 0, np.nan)
        gb = filter_qc(gb, filter_config, qc_var="qcflag")

        lat_name = "site_latitude"
        station_lat = float(gb.attrs[lat_name])

        sat_ground = get_sat_data_at_ground_coords(gb, sat)

        # Monthly mean of ground observations
        gb_monthly = (
            gb["value"]
            .assign_coords(time=gb["time"])
            .resample(time="MS")
            .mean()
            / scaling
        )

        sat_monthly = sat_ground["x" + gas]

        gb_monthly, sat_monthly = xr.align(
            gb_monthly,
            sat_monthly,
            join="inner",
        )

        valid = (~gb_monthly.isnull()) & (~sat_monthly.isnull())

        gb_matched = gb_monthly.where(valid, drop=True)
        sat_matched = sat_monthly.where(valid, drop=True)

        print("checking selection: should be the same")
        print(sat_matched.size)
        print(gb_matched.size)

        return (
            gb_matched.values,
            sat_matched.values.squeeze(),
            station_lat,
        )

    else:
        return np.nan, np.nan, np.nan


def get_all_matched_data(files:list[str], sat:xr.Dataset, gas:str, flask:bool = False):
    """Get all matched satellite and ground obs"""
    all_sat = []
    all_gb = []
    all_lat = []

    for file in files:
        gb = xr.open_dataset(file)
        if flask:
            print('FLASK')
            gb = filter_qc(gb, filter_config)
        try:
            gb_matched, sat_matched, station_lat = get_matched_data(gb, sat, gas, flask)

            if not sat_matched.size == 0:
                all_sat.append(np.asarray(sat_matched).ravel())
                all_gb.append(np.asarray(gb_matched).ravel())
                n = len(sat_matched)
                all_lat.append(np.full(n, station_lat))

        finally:
            gb.close()

    all_sat = np.concatenate(all_sat)
    all_gb = np.concatenate(all_gb)
    all_lat = np.concatenate(all_lat)

    mask = np.isfinite(all_sat) & np.isfinite(all_gb)

    return all_sat[mask], all_gb[mask], all_lat[mask]


def make_sat_times_mask(gb:xr.Dataset, sat:xr.Dataset, gas):
    """Return mask of valid times with sat values"""
    valid_sat_times = sat.time.values[~np.isnan(sat["x" + gas].values)]
    gb_time = gb["time"]

    return np.isin(gb_time, valid_sat_times)


def make_ground_times_mask(gb, sat):
    """Return mask of valid times with ground values"""
    valid_ground_times = gb.time.values[~np.isnan(gb["time"].values)]
    sat_time = sat["time"]

    return np.isin(sat_time, valid_ground_times)


def get_matching_data(gb, sat, gas):
    """Return matched satellite and ground observations."""
    sat_ground = get_sat_data_at_ground_coords(gb, sat)

    gb_times, gb_values = extract_ground_data(gb, gas)

    valid_sat = np.isfinite(sat_ground["x" + gas].values)

    sat_times = sat_ground.time.values[valid_sat]
    sat_values = sat_ground["x" + gas].values[valid_sat]

    common_times = np.intersect1d(gb_times, sat_times)

    gb_mask = np.isin(gb_times, common_times)
    sat_mask = np.isin(sat_times, common_times)

    gb_matched = gb_values[gb_mask]
    sat_matched = sat_values[sat_mask]

    valid = np.isfinite(gb_matched) & np.isfinite(sat_matched)

    return sat_matched[valid], gb_matched[valid]


def get_sat_data_at_ground_coords(gb:xr.Dataset, sat:xr.Dataset):
    """Return sat data overlapping with coordinates of ground data"""
    if "mf" in gb:
        lat_name = 'inlet_latitude'
        lon_name = 'inlet_longitude'
    elif "value" in gb:
        lat_name = 'site_latitude'
        lon_name = 'site_longitude'

    gb_lat = gb.attrs[lat_name]
    gb_lon = gb.attrs[lon_name]

    aligned = sat.sel(lat=gb_lat, lon=gb_lon, method="nearest")
    return set_time_at_start_of_month(aligned)


def set_time_at_start_of_month(ds:xr.Dataset):
    """Return sat data with timestamps at beginning of month"""
    return ds.assign_coords(
        time=pd.DatetimeIndex(ds.time.values).to_period("M").to_timestamp()
    )

def extract_ground_data(gb:xr.Dataset, gas: str):
    """Return (times, values) regardless of dataset structure."""
    scaling = get_scaling(gas)

    if "mf" in gb:
        # AGAGE style
        times = gb.time.values
        values = gb["mf"].values / scaling

    elif "value" in gb:
        # obs dimension style
        times = gb["time"].values
        values = gb["value"].values / scaling

    else:
        raise ValueError("Unknown ground dataset format")  # noqa: TRY003

    return times, values


def get_station_code(filename:str):
    """Return station code after first _"""
    return Path(filename).stem.split("_")[1]


#########################
## FIT UTILS
#########################


def linear_fit(gb:xr.Dataset, sat:xr.Dataset):
    """
    Fit:

    gb = sf * sat
    """
    return np.sum(sat * gb) / np.sum(sat**2)


def linear_fit_intercept(gb:xr.Dataset, sat:xr.Dataset):
    """
    Fit:

    gb = sf * sat + inter
    """
    x = sat
    y = gb

    x_mean = np.mean(x)
    y_mean = np.mean(y)

    sf = np.sum((x - x_mean) * (y - y_mean)) / np.sum((x - x_mean) ** 2)
    intercept = y_mean - sf * x_mean

    return sf.values, intercept.values


def linear_fit_lat(gb:xr.Dataset, sat:xr.Dataset, lat:xr.Dataset):
    """
    Fit:

    gb = (a + b*lat) * sat
    """
    X = np.column_stack(
        [
            sat,
            sat * lat,
        ]
    )

    coef, *_ = np.linalg.lstsq(X, gb, rcond=None)

    return coef


#########################
## PLOT UTILS
#########################


def plot_fit(sat:xr.Dataset, gb:xr.Dataset, sf:float, gas:str, station_name:str):
    """Plot the fit against scatterplot"""
    if gas == "co2":
        uppercase_gas = "CO2"
    elif gas == "ch4":
        uppercase_gas = "CH4"
    else:
        raise ValueError("gas_not_supported")

    plt.scatter(sat, gb, label="measurements")

    x = np.linspace(sat.min(), sat.max(), 100)
    plt.plot(x, sf * x, "r-", label=f"fit: gb = {sf} * sat")

    plt.xlabel(f"Satellite X{uppercase_gas}")
    plt.ylabel(f"{station_name} {uppercase_gas}")
    plt.legend()
    plt.grid(True)

    plt.savefig(f"{plots_path}{station_name}_vs_sat_fit_{gas}.png", dpi=300)
    plt.close()


def plot_fit_intercept(sat:xr.Dataset, gb:xr.Dataset, sf:float, intercept:float, gas:str, station_name:str):  # noqa: E501, PLR0913
    """Plot the fit with the intercept"""
    if gas == "co2":
        uppercase_gas = "CO2"
    elif gas == "ch4":
        uppercase_gas = "CH4"
    else:
        raise ValueError("gas_not_supported")

    plt.scatter(sat, gb, label="measurements")

    x = np.linspace(sat.min(), sat.max(), 100)
    y = sf * x + intercept

    plt.plot(
        x,
        y,
        "r-",
        label=f"fit: gb = {sf:.3f} * sat + {intercept:.3f}",
    )

    plt.xlabel(f"Satellite X{uppercase_gas}")
    plt.ylabel(f"{station_name} {uppercase_gas}")
    plt.legend()
    plt.grid(True)

    plt.savefig(f"{plots_path}{station_name}_vs_sat_fit_{gas}.png", dpi=300)
    plt.close()


def plot_fit_to_obs(obs, fit, title="observed_vs_fitted_latfit"):
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


def plot_residual(all_gb, all_sat, all_lat, sf, title_appendix):
    """Plot residuals dependence on latitude"""
    residual_all = all_gb - sf * all_sat

    plt.scatter(all_lat, residual_all)
    plt.xlabel("Latitude")
    plt.ylabel("Residual")
    plt.savefig(f"{plots_path}residuals_lineat_fit_{title_appendix}.png", dpi=300)
    plt.close()

def scatter_plot(gb, sat, gas, station_name):
    """Plot scatter plot ground vs sat"""
    gb["value"] = gb["value"].where(gb["value"] >= 0, np.nan)
    sat[f"x{gas}"] = sat[f"x{gas}"].where(sat[f"x{gas}"] >= 0, np.nan)

    gb_matched, sat_matched = get_matching_data(gb, sat, gas)

    plt.scatter(gb_matched, sat_matched, alpha=0.7)

    plt.xlabel(f"{station_name} {gas}")
    plt.ylabel(f"Satellite x{gas}")
    plt.title(f"Satellite vs {station_name} {gas}")
    plt.grid(True)
    plt.savefig(f"{plots_path}sat_vs_AGAGE_{station_name}_scatter_{gas}.png", dpi=300)
    plt.close()

def plot_matching_data(gb, sat, gas, station_name):
    """Plot matching points in over time"""
    scaling = get_scaling(gas)

    sat = get_sat_data_at_ground_coords(gb, sat)

    mask = make_sat_times_mask(gb, sat, gas)

    gb_time = gb["time"][mask]
    gb_gas = gb["value"][mask] / scaling

    sat[f"x{gas}"].plot(
        label=f"sat over {station_name} coords",
        marker="o",
        linestyle="None",
    )
    plt.plot(
        gb_time,
        gb_gas,
        label=f"{station_name}",
        marker="o",
        linestyle="None",
    )
    plt.legend()
    plt.title(f"Comparing OBS4MIPs over {station_name} coords and ground based data")
    plt.savefig(f"{plots_path}sat_over_{station_name}_and_gb_AGAGE_{gas}.png", format="png")
    plt.close()
