"""

Point selection

Brutal selection of points that have both satellite value and
ground based measurements from NOAA

"""

from pathlib import Path

import numpy as np
import xarray as xr

from local.processing.utils import (
    get_sat_data,
    get_station_code,
    plot_matching_data,
    scatter_plot,
)

gas = "co2"
sat_gas = "x" + gas

data_path = Path(
    f"/home/anna_lanteri/data/ground_based_data/NOAA/{gas}_surface-insitu_ccgg_netCDF/"
)

if __name__ == "__main__":

    sat_data = get_sat_data(gas)

    ## Plot the comparison plots
    files = sorted(data_path.glob(f"{gas}_*_MonthlyData.nc"))

    for file in files:
        gb = xr.open_dataset(file)

        gb["value"] = gb["value"].where(gb["value"] > 0, np.nan)

        station_name = get_station_code(file)
        print(station_name)
        plot_matching_data(gb, sat_data, gas, station_name=station_name)
        print("scatter")
        scatter_plot(gb, sat_data, gas, station_name=station_name)
