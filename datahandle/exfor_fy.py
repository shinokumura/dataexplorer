####################################################################
#
# This file is part of libraries-2021 dataexplorer, https://nds.iaea.org/dataexplorer/.
# Copyright (C) 2022 International Atomic Energy Agency (IAEA)
#
# Contact:    nds.contact-point@iaea.org
#
####################################################################

import pandas as pd
import re
import os
import fnmatch

from config import EXP_PATH_FY


# ------------------------------------------------------------------------------
# APP4: Fission Yield
#
# ------------------------------------------------------------------------------
# Read EXFOR data
#
#
def read_exfy_a(nuclide, inc_pt, mt, ee, nn):
    path = "".join([EXP_PATH_FY, inc_pt, "/", nuclide, "/exfor/", mt, "/"])
    exfiles = []
    for i in range(len(ee)):
        e = str(ee[i])
        en = nn[i] / 1e6

        if en > 0.1:
            # print (j, ee, '{:08.3F}'.format(en))
            fmt = "".join(["*-MT", mt, "*", e, "-E", "{:08.3F}".format(en), "*"])
        else:
            # print (j, ee, '{:8.2E}'.format(en))
            fmt = "".join(["*-MT", mt, "*", e, "-E", "{:8.2E}".format(en), "*"])

        exname = fnmatch.filter(os.listdir(path), fmt)
        exfiles += exname
    #print(path,exfiles)

    if exfiles:
        exya_df = create_exfy(path, exfiles)  # all included both A==0 and Z ==0

    else:
        exya_df = pd.DataFrame()

    return exfiles, exya_df


def read_exfy_za(nuclide, inc_pt, mt, ee, nn):
    path = "".join([EXP_PATH_FY, inc_pt, "/", nuclide, "/exfor/", mt, "/"])
    exfiles = []
    for i in range(len(ee)):
        e = str(ee[i])
        en = nn[i] / 1e6

        if en > 0.1:
            # print (j, ee, '{:08.3F}'.format(en))
            fmt = "".join(["*-MT", mt, "*", e, "-E", "{:08.3F}".format(en), "*"])

        else:
            # print (j, ee, '{:8.2E}'.format(en))
            fmt = "".join(["*-MT", mt, "*", e, "-E", "{:8.2E}".format(en), "*"])

        exname = fnmatch.filter(os.listdir(path), fmt)
        exfiles += exname

    if exfiles:
        exza_df = create_exfy(path, exfiles)  # all included both A==0 and Z ==0

    else:
        exza_df = pd.DataFrame()

    return exfiles, exza_df


def create_exfy(path, exfiles):
    dfs = []
    for e in exfiles:
        datasetname = re.split("[-]", e, 5)

        ef = "".join([path, e])
        # if "list" in e:
        #     continue
        # else:
        with open(ef, "r") as f:
            for line in f.readlines():
                if "# E-inc" in line:
                    line = line.split()
                    Einc, dEinc = line[3], line[6]

        exfy_df = pd.read_csv(
            ef,
            sep="\s+",
            index_col=None,
            header=None,
            comment="#",
            names=["Z", "A", "Iso", "FPY", "dFPY"],
        )

        exfy_df = exfy_df[exfy_df["Z"] != "0****"]  # to drop error file from C5
        exfy_df["Einc"] = Einc
        exfy_df["dEinc"] = dEinc
        exfy_df["author"] = datasetname[3]
        exfy_df["entry"] = datasetname[4]
        exfy_df["year"] = re.split("[.]", datasetname[-1])[-1]
        dfs.append(exfy_df)

    if dfs:
        exfy_df = pd.concat(dfs, ignore_index=True)
        exfy_df = exfy_df.astype(
            {
                "Z": "int",
                "A": "int",
                "Iso": "int",
                "FPY": "float64",
                "dFPY": "float64",
                "Einc": "float64",
                "dEinc": "float64",
            }
        )  # , errors='ignore'
        exfy_df["Einc"] *= 1e6
        exfy_df["dEinc"] *= 1e6


    else:
        exfy_df = pd.DataFrame()

    return exfy_df
