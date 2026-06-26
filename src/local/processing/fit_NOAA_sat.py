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
    linear_fit_intercept,
    plot_fit_intercept,
)

gas = "co2"
data_path = Path(
    f"/home/anna_lanteri/data/ground_based_data/NOAA/{gas}_surface-insitu_ccgg_netCDF/"
)


if __name__ == "__main__":
    # NOAA datasets
    files = sorted(data_path.glob(f"{gas}_*_MonthlyData.nc"))
    print(gas)
    print(len(files))

    # OBD4MIPs
    sat = get_sat_data(gas)
    for file in files:
        station_name = get_station_code(file)
        print(station_name)

        gb = xr.open_dataset(file)
        gb["value"] = gb["value"].where(gb["value"] >= 0, np.nan)

        gb_matched, sat_matched, _ = get_matched_data(gb, sat, gas)

        # sf = linear_fit(gb_matched, sat_matched).values
        sf, intercept = linear_fit_intercept(gb_matched, sat_matched)

        print(f"Scaling factor sf = {sf}")
        print(f"Intercept: {intercept}")

        if not np.isnan(sf):
            # plot_fit(sat_matched, gb_matched, sf, gas, station_name)
            plot_fit_intercept(
                sat_matched, gb_matched, sf, intercept, gas, station_name
            )
