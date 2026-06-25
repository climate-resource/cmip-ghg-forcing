"""
Download all datasets
"""

from pathlib import Path

from local.download import download

if __name__ == "__main__":
    download_path = Path("/home/anna_lanteri/data/ground_based_data/NOAA/")
    gas = "ch4"

    config = {"gas": gas, "folder": "in-situ", "sampling": "insitu"}

    download.NOAA_ground_based_data(download_path, config)
    download.AGAGE_ground_based_data(download_path)

    download.satellite_data(download_path, gas)
