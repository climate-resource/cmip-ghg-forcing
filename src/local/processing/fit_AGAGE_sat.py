"""
Fit sat to AGAGE

"""

from pathlib import Path

import numpy as np
import xarray as xr

from local.processing.utils import (
    get_matching_data,
    get_sat_data,
    get_station_code,
    linear_fit,
    plot_fit,
)

agage_data_path = Path("/home/anna_lanteri/data/ground_based_data/AGAGE/")

if __name__ == "__main__":
    specie = "co2"  # ch4

    agage_files = sorted(agage_data_path.glob("*" + specie + "*-20251230.nc"))
    agage_files.append(
        agage_data_path / f"agage_cgo_{specie}_monthly-baseline-20250123.nc"
    )

    sat_data = get_sat_data(specie)

    for file in agage_files:
        gb = xr.open_dataset(file)
        gb["mf"] = gb["mf"].where(gb["mf"] > 0, np.nan)
        station = get_station_code(file)
        if station != "cmo":
            print(station)

            sat_matched, gb_matched = get_matching_data(gb, sat_data, specie)
            gb_matched = gb_matched.squeeze()
            sat_matched = sat_matched.squeeze()

            sf = linear_fit(gb_matched, sat_matched)
            print(f"Scaling factor sf = {sf}")
            print("gb size:", gb_matched.size)
            print("sat size:", sat_matched.size)

            plot_fit(sat_matched, gb_matched, sf, station)

        gb.close()
