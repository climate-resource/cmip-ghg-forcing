"""
Download all datasets
"""

from pathlib import Path

from local.download import download

if __name__ == "__main__":
    gb_download_path = Path("/home/anna_lanteri/data/ground_based_data/")
    sat_download_path = Path("/home/anna_lanteri/data/satellite_data/")

    gas = "co2" # ch4

    config = {"gas": gas, "folder": "in-situ", "sampling": "insitu"}

    #print('Downloading NOAA data')
    #download.NOAA_ground_based_data(gb_download_path + "NOAA/", config)
    #print('Done')

    # AGAE does not have co2
    #download.AGAGE_ground_based_data(gb_download_path + "AGAGE/", gas)

    download.satellite_data(sat_download_path, gas)

