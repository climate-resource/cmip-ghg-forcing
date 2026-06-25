""""

Calculate scaling factor for all ground based datasets
"""
import numpy as np

from local.processing.utils import (
    get_agage_files,
    get_all_matched_data,
    get_noaa_files,
    get_sat_data,
    linear_fit,
    linear_fit_lat,
    plot_fit,
    plot_fit_to_obs,
    plot_residual,
)

if __name__ == "__main__":
    specie = 'ch4'

    sat_data = get_sat_data(specie)
    agage_files = get_agage_files(specie)
    noaa_files = get_noaa_files(specie)

    all_AGAGE_sat, all_AGAGE_gb, all_AGAGE_lat = get_all_matched_data(agage_files,
                                                                      sat_data,
                                                                      specie)
    all_NOAA_sat, all_NOAA_gb, all_NOAA_lat = get_all_matched_data(noaa_files,
                                                                   sat_data,
                                                                   specie)
    all_sat = np.concatenate([all_AGAGE_sat, all_NOAA_sat])
    all_gb = np.concatenate([all_AGAGE_gb, all_NOAA_gb])
    all_lat = np.concatenate([all_AGAGE_lat, all_NOAA_lat])

    mask = np.isfinite(all_sat) & np.isfinite(all_gb)
    all_sat = all_sat[mask]
    all_gb = all_gb[mask]
    all_lat = all_lat[mask]

    ## Linear fit dependent only on gas value
    sf_agage = linear_fit(all_AGAGE_gb, all_AGAGE_sat)
    sf_noaa = linear_fit(all_NOAA_gb, all_NOAA_sat)
    sf = linear_fit(all_gb, all_sat)

    print(f"Global scaling factor for AGAGE = {sf_agage}")
    print(f"Global scaling factor for NOAA = {sf_noaa}")
    print(f"Global scaling factor for AGAGE and NOAA = {sf}")

    plot_fit(all_AGAGE_sat, all_AGAGE_gb, sf_agage, "AGAGE_all")
    plot_fit(all_NOAA_sat, all_NOAA_gb, sf_noaa, "NOAA_all")
    plot_fit(all_sat, all_gb, sf, "all")

    # Checking the residuals to see if lat matters
    plot_residual(all_gb, all_sat, all_lat, sf, title_appendix = 'all')

    ## Fit depending on lat
    a, b = linear_fit_lat(
        all_gb,
        all_sat,
        all_lat,
    )

    print(f"sf(lat) = {a:.6f} + {b:.6e} * lat")

    residual_old = (
        all_gb
        - sf_agage * all_sat
    )

    residual_new = (
        all_gb
        - (a + b*all_lat) * all_sat
    )

    print(np.std(residual_old))
    print(np.std(residual_new))

    gb_fit = (a + b * all_lat) * all_sat

    plot_fit_to_obs(all_gb, gb_fit, title = 'observed_vs_fitted_latfit')



