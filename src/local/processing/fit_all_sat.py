"""

Calculate scaling factor for all ground based datasets and flask data
"""

import numpy as np

from local.processing.utils import (
    get_agage_files,
    get_all_matched_data,
    get_noaa_files,
    get_noaa_flask_files,
    get_sat_data,
    linear_fit,
    plot_fit,
)

if __name__ == "__main__":
    gas = "ch4"

    sat_data = get_sat_data(gas)
    agage_files = get_agage_files(gas)
    noaa_gb_files = get_noaa_files(gas)
    noaa_flask_files = get_noaa_flask_files(gas)

    all_AGAGE_sat, all_AGAGE_gb, all_AGAGE_lat = get_all_matched_data(
        agage_files, sat_data, gas
    )
    all_NOAA_gb_sat, all_NOAA_gb, all_NOAA_gb_lat = get_all_matched_data(
        noaa_gb_files, sat_data, gas
    )
    all_NOAA_flask_sat, all_NOAA_flask, all_NOAA_flask_lat = get_all_matched_data(
        noaa_flask_files[:10], sat_data, gas, flask=True
    )

    all_sat = np.concatenate([all_AGAGE_sat, all_NOAA_gb_sat, all_NOAA_flask_sat])
    all_gb = np.concatenate([all_AGAGE_gb, all_NOAA_gb, all_NOAA_flask])
    all_lat = np.concatenate([all_AGAGE_lat, all_NOAA_gb_lat, all_NOAA_flask_lat])

    mask = np.isfinite(all_sat) & np.isfinite(all_gb)
    all_sat = all_sat[mask]
    all_gb = all_gb[mask]
    all_lat = all_lat[mask]

    sf_agage = linear_fit(all_AGAGE_gb, all_AGAGE_sat)
    sf_noaa = linear_fit(all_NOAA_gb, all_NOAA_gb_sat)
    sf_flask = linear_fit(all_NOAA_flask, all_NOAA_flask_sat)
    sf = linear_fit(all_gb, all_sat)

    print(f"Global scaling factor for AGAGE = {sf_agage}")
    print(f"Global scaling factor for NOAA = {sf_noaa}")
    print(f"Global scaling factor for NOAA flask = {sf_flask}")
    print(f"Global scaling factor for AGAGE and NOAA = {sf}")

    plot_fit(all_AGAGE_sat, all_AGAGE_gb, sf_agage, gas, "AGAGE_all")
    plot_fit(all_NOAA_gb_sat, all_NOAA_gb, sf_noaa, gas, "NOAA_gb")
    plot_fit(all_NOAA_flask_sat, all_NOAA_flask, sf_noaa,  gas, "NOAA_flask")
    plot_fit(all_sat, all_gb, sf, gas, "all")


# todo tomorrow: clean up that monstruosity that is the get_all_matched_data function
# todo tomorrow: gotta try more complex fits for all data, there really looks to be two clumps of data, let's go