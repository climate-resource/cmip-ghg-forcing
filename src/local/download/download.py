"""

Download ground based data from NOOA
"""

import logging
import os
from pathlib import Path

import httpx
import pandas as pd
import requests

# pip install ecmwf-api-client ecmwf-datastores-client
from ecmwf.datastores import Client  # type: ignore

client = Client()
logging.basicConfig(level="INFO")


base_url = "https://gml.noaa.gov/aftp/data/greenhouse_gases/"


def NOAA_ground_based_data(download_path, config):
    """Download NOAA ground-based data"""
    download_path = Path(download_path).expanduser().absolute()
    os.makedirs(download_path, exist_ok=True)
    print(f"Downloading to: {download_path!s}")

    gas = config["gas"]
    folder = config["folder"]
    sampling = config["sampling"]

    url = f"{base_url}{gas}/{folder}/surface/{gas}_surface-{sampling}_ccgg_netCDF.zip"

    response = requests.get(url, timeout=10)
    print(f"Request URL: {url}")
    print(f"Response status code: {response.status_code}")
    response.raise_for_status()

    with open(download_path / f"noaa_{gas}_surface_{sampling}.zip", "wb") as f:
        f.write(response.content)

    logging.info(f"downloaded NOAA-zip ({gas}-{sampling}) to {download_path!s}")


def AGAGE_ground_based_data(save_to_path: Path) -> None:
    """
    Download methane concentrations from (A)GAGE database

    Parameters
    ----------
    save_to_path:
        path where data should be stored

    """
    os.makedirs(save_to_path, exist_ok=True)

    r_compounds = httpx.get(
        "https://www-air.larc.nasa.gov/missions/agage/api/data/compounds"
    )
    # check response
    r_compounds.raise_for_status()
    # get id for methane
    r_compunds_dict = pd.DataFrame(r_compounds.json())
    compound_id = r_compunds_dict[r_compunds_dict.compound_name == "Methane"][
        "id"
    ].values[0]

    # Get files available for extracted id
    r_files = []
    page_number = 1
    while True:
        try:
            httpx.get(
                f"https://www-air.larc.nasa.gov/missions/agage/api/data/{page_number}",
                params={
                    "recommended": True,
                    "compound": compound_id,
                    "data_frequency": 2,
                    "product_type": 1,
                },
            ).raise_for_status()

        except httpx.HTTPStatusError:
            break
        else:
            # data_frequency: 2 stands for "monthly"
            # product_type: 1 stands for "mole fraction"
            r_file = httpx.get(
                f"https://www-air.larc.nasa.gov/missions/agage/api/data/{page_number}",
                params={
                    "recommended": True,
                    "compound": compound_id,
                    "data_frequency": 2,
                    "product_type": 1,
                },
            )
            page_number += 1

        r_files.append(pd.DataFrame(r_file.json()))

    file_ids = pd.concat(r_files)

    # check that all files are included
    if len(file_ids) != file_ids["count"].unique()[0]:
        raise ValueError(  # noqa: TRY003
            "length of extracted data files does not correspond to database-counts"
        )

    # download netCDF zip.files
    for file_id, file_name in zip(file_ids.id, file_ids.file_name):
        response = requests.get(
            f"https://www-air.larc.nasa.gov/missions/agage/api/data/download/{file_id}",
            timeout=10,
        )

        with open(save_to_path / file_name.replace(".nc", ".zip"), "wb") as f:
            f.write(response.content)

    logging.info(
        f"downloaded AGAGE-zip to {save_to_path / file_name.replace('.nc', '.zip')!s}"
    )


def satellite_data(download_path: Path, gas: str):
    """Download satellite data from ECMWF"""
    download_path = Path(download_path).expanduser().absolute()
    print(f"Downloading to: {download_path!s}")

    os.makedirs(download_path, exist_ok=True)

    request = {
        "processing_level": ["level_3"],
        "variable": f"x{gas}",
        "sensor_and_algorithm": "merged_obs4mips",
        "version": ["4_6"],
    }

    if not client.check_authentication():
        raise ValueError("Authentification failed. Load website and agree to terms")  # noqa: TRY003

    target = download_path / f"obs4mips_x{gas}.zip"
    dataset = "satellite-methane"
    client.retrieve(dataset, request, target=str(target))

    return logging.info(f"downloaded OBS4MIPs {gas} data to {target!s}")
