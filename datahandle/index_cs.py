####################################################################
#
# This file is part of libraries-2021 dataexplorer, https://nds.iaea.org/dataexplorer/.
# Copyright (C) 2022 International Atomic Energy Agency (IAEA)
#
# Contact:    nds.contact-point@iaea.org
#
####################################################################

import pandas as pd
import os

from config import EXP_PATH
from datahandle.list import elemtoz


def read_index(nuclide, slct_reac, mt):
    reac = slct_reac.split(",")

    # file path
    listfile = "".join(
        [
            EXP_PATH,
            reac[0],
            "/",
            nuclide,
            "/exfor/xs/",
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

    index_df = create_indexdf(listfile)

    return index_df


def read_index_rp(nuclide, inc_pt, rp_elem, rp_mass):
    rp_z = elemtoz(rp_elem)

    # file path
    listfile = "".join(
        [
            EXP_PATH,
            inc_pt,
            "/",
            nuclide,
            "/exfor/residual/",
            rp_z,
            rp_mass,
            "/",
            inc_pt,
            "-",
            nuclide,
            "-rp",
            rp_z,
            rp_mass,
            ".list",
        ]
    )

    index_df = create_indexdf(listfile)

    return index_df


def create_indexdf(listfile):
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
            names=["filename", "points", "emin", "emax"],
        )
        index_df[["inc", "target", "mt", "author", "entry", "year"]] = index_df[
            "filename"
        ].str.split("[-.]", expand=True)
        index_df = index_df.astype(
            {"emin": "float64", "emax": "float64", "points": "int"}, errors="ignore"
        )
        index_df = index_df[["author", "entry", "year", "points", "emin", "emax"]]
        index_df[["emin", "emax"]] *= 1e6
        index_df = index_df.sort_values(by=["year"], ascending=False).reset_index(
            drop=True
        )

    else:
        index_df = pd.DataFrame()

    return index_df
