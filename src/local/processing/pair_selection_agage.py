"""

Select points

Brutal selection of points that have both satellite value and
ground based measurements from AGAGE

"""

import numpy as np
import xarray as xr

from local.processing.utils import (
    get_agage_files,
    get_sat_data,
    get_station_code,
    plot_matching_data,
    scatter_plot,
)

if __name__ == "__main__":
    gas = 'ch4'

    agage_files = get_agage_files(gas)
    sat_data = get_sat_data(gas)

    for file in agage_files:
        gb = xr.open_dataset(file)
        gb["mf"] = gb["mf"].where(gb["mf"] > 0, np.nan)
        station = get_station_code(file)

        plot_matching_data(gb, sat_data, gas, station)
        scatter_plot(gb, sat_data, gas, station)

        gb.close()

