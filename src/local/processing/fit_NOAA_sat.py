"""
Calculate the scaling factor in the simplest way

"""

from pathlib import Path

import numpy as np
import xarray as xr

from local.processing.utils import (
    get_matched_data,
    get_sat_data,
    get_station_code,
    linear_fit,
    plot_fit,
)

data_path = Path(
    "/home/anna_lanteri/data/ground_based_data/NOAA/ch4_surface-insitu_ccgg_netCDF/"
)

if __name__ == "__main__":
    specie = "ch4"

    # NOAA datasets
    files = sorted(data_path.glob(f"{specie}_*_MonthlyData.nc"))

    # OBD4MIPs
    sat_data = get_sat_data(specie)
    for file in files:
        gb = xr.open_dataset(file)
        gb_matched, sat_matched, _ = get_matched_data(gb, sat_data, specie)
        sf = linear_fit(gb_matched, sat_matched).values
        print(f"Scaling factor sf = {sf}")

        station_name = get_station_code(file)
        if not np.isnan(sf):
            plot_fit(sat_matched, gb_matched, sf, station_name)
