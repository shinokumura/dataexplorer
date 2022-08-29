####################################################################
#
# This file is part of libraries-2021 dataexplorer, https://nds.iaea.org/dataexplorer/.
# Copyright (C) 2022 International Atomic Energy Agency (IAEA)
#
# Contact:    nds.contact-point@iaea.org
#
####################################################################

import pandas as pd
import numpy as np
import os

# import glob

from config import EXP_PATH_FY

# from file_utils import path_exists


def energy_range(energy):
    # energy unit in eV
    if energy == "eV":
        min_einc = 1.00e-10
        max_einc = 1.00e03  # less than 0.0253 eV
    elif energy == "keV":
        min_einc = 1.00e03
        max_einc = 1.00e06
    elif energy == "MeV":
        min_einc = 1.00e06
        max_einc = 1.00e08  # 100 MeV, just in case
    elif energy == "0":
        min_einc = 0.00
        max_einc = 1.00e-20
    else:
        min_einc = np.NaN
        max_einc = np.NaN

    return min_einc, max_einc


def read_index_fy(nuclide, slct_reac, mt, min_einc, max_einc):
    reac = slct_reac.split(",")

    listfile_a = "".join(
        [
            EXP_PATH_FY,
            reac[0],
            "/",
            nuclide,
            "/exfor/",
            mt,
            "/",
            reac[0],
            "-",
            nuclide,
            "-MT",
            mt,
            "-YA.list",
        ]
    )
    listfile_za = "".join(
        [
            EXP_PATH_FY,
            reac[0],
            "/",
            nuclide,
            "/exfor/",
            mt,
            "/",
            reac[0],
            "-",
            nuclide,
            "-MT",
            mt,
            ".list",
        ]
    )
    index_a_df = create_indexdf(listfile_a, min_einc, max_einc)
    index_za_df = create_indexdf(listfile_za, min_einc, max_einc)


    return index_a_df, index_za_df


def create_indexdf(listfile, min_einc, max_einc):
    cols = [
        "filename",
        "points",
        "emin",
        "emax",
        "inc",
        "target",
        "mt",
        "author",
        "entry",
        "year",
    ]
    index_df = pd.DataFrame(columns=cols)

    if os.path.exists(listfile):
        index_df = pd.read_csv(
            listfile,
            sep="\s+",
            index_col=None,
            header=None,
            usecols=[0, 1, 2, 3],
            comment="#",
            names=["filename", "points", "einc", "de"],
        )
        index_df[["inc", "target", "mt", "author", "entry", "tmp"]] = index_df[
            "filename"
        ].str.split("[-]", 5, expand=True)
        index_df["year"] = index_df["tmp"].str[10:14]
        index_df = index_df.astype(
            {"entry": "object", "einc": "float64", "de": "float64", "points": "int"}
        )
        index_df = index_df[["author", "entry", "year", "points", "einc", "de"]]
        index_df["einc"] *= 1e6
        index_df["de"] *= 1e6
        index_df = index_df.sort_values(by=["einc", "year"], ascending=True)

        index_df = index_df[
            (index_df["einc"] > min_einc) & (index_df["einc"] < max_einc)
        ]
        index_df = index_df.sort_values(by=["einc"], ascending=True).reset_index(drop=True)

    else:
        index_df = pd.DataFrame()


    return index_df

