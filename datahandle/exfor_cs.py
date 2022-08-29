####################################################################
#
# This file is part of libraries-2021 dataexplorer, https://nds.iaea.org/dataexplorer/.
# Copyright (C) 2022 International Atomic Energy Agency (IAEA)
#
# Contact:    nds.contact-point@iaea.org
#
####################################################################

import os
import re
import pandas as pd

from config import EXP_PATH
from datahandle.list import elemtoz


def read_exfor(nuclide, slct_reac, mt, slctd_e):
    reac = slct_reac.split(",")

    # file path
    path = "".join([EXP_PATH, reac[0], "/", nuclide, "/exfor/xs/", mt, "/"])

    # Data read
    try:
        exfiles = os.listdir(path)

    except:
        exfiles = []

    if exfiles:
        exfor_df = create_exfordf(path, exfiles, slctd_e)
    else:
        exfor_df = pd.DataFrame()

    return exfiles, exfor_df


def read_resid_prod_exfor(nuclide, inc_pt, rp_elem, rp_mass, slctd_e):
    rp_z = elemtoz(rp_elem)

    path = "".join(
        [EXP_PATH, inc_pt, "/", nuclide, "/exfor/residual/", rp_z, rp_mass, "/"]
    )

    try:
        exfiles = os.listdir(path)
    except:
        exfiles = []

    if exfiles:
        rpex_df = create_exfordf(path, exfiles, slctd_e)

    else:
        rpex_df = pd.DataFrame()

    return exfiles, rpex_df


def create_exfordf(path, exfiles, slctd_e):
    dfs = []
    for e in exfiles:
        # get dataset info from file name when os.listdir is used
        datasetname = re.split("[-.]", e)
        if "list" in e:
            continue
        elif datasetname[4] in slctd_e:
            exfor_df = pd.read_csv(
                "".join([path, e]),
                sep="\s+",
                index_col=None,
                header=None,
                usecols=[0, 1, 2, 3],
                comment="#",
                names=["Energy", "XS", "dXS", "dE"],
            )
            exfor_df["author"] = datasetname[3]
            exfor_df["entry"] = datasetname[4]
            exfor_df["year"] = datasetname[5]
            dfs.append(exfor_df)

    if dfs:
        exfor_df = pd.concat(dfs, ignore_index=True)
        exfor_df["XS"] *= 1e-3
        exfor_df["dXS"] *= 1e-3
        exfor_df["Energy"] *= 1e6
        exfor_df["dE"] *= 1e6


    else:
        exfor_df = pd.DataFrame()


    return exfor_df
