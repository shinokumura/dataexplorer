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

from config import LIB_PATH
from datahandle.list import elemtoz, LIB_LIST_MIN, LIB_LIST_RP, ISOMERIC

# ------------------------------------------------------------------------------
# APP2: Libraries
def read_libs(nuclide, slct_reac, mt, groupwise):
    lib_list = LIB_LIST_MIN
    reac = slct_reac.split(",")

    liblist = []
    libfiles = []
    for lib in lib_list:
        path = "".join([LIB_PATH, reac[0], "/", nuclide, "/", lib, "/tables/xs/"])

        filename = "".join(
            [
                reac[0],
                "-",
                nuclide,
                "-MT",
                mt,
                "-G1102."
                if (
                    "G" in groupwise
                    and mt in ["001", "002", "018", "102"]
                    and not nuclide.endswith("000")
                    and reac[0] == "n"
                )
                else ".",
                lib,
                ".dat"
            ]
        )

        lfname = "".join([path, filename])

        if os.path.exists(lfname):
            # Library file name list for download
            liblist.append([lfname, lib])

    lib_df = create_libdf(liblist)

    if liblist:
        libfiles = [i[0] for i in liblist]

    return libfiles, lib_df


# ------------------------------------------------------------------------------
# APP3: Residual CS
#
#
def read_resid_prod_lib(nuclide, inc_pt, rp_elem, rp_mass):
    lib_list = LIB_LIST_RP
    rp_z = elemtoz(rp_elem)

    liblist = []
    libfiles = []
    for lib in lib_list:
        path = "".join([LIB_PATH, inc_pt, "/", nuclide, "/", lib, "/tables/residual/"])
        lfname = "".join([path, inc_pt, "-", nuclide, "-rp", rp_z, rp_mass, ".", lib, ".dat"])

        if os.path.exists(lfname):
            # Library file name list for download
            liblist.append([lfname, lib])

    lib_df = create_libdf(liblist)

    if liblist:
        libfiles = [i[0] for i in liblist]

    return libfiles, lib_df


def create_libdf(libfiles):
    dfs = []
    for i in range(0, len(libfiles)):
        l = libfiles[i][0]
        lib = libfiles[i][1]

        try:  # due to null file such as g + S  33 : (g,a)
            lib_df = pd.read_csv(
                l,
                sep="\s+",
                index_col=None,
                header=None,
                usecols=[0, 1],
                comment="#",
                names=["Energy", "XS"],
            )
            lib_df["lib"] = lib
            dfs.append(lib_df)

            if lib_df["XS"].sum() == 0:
                lib_df.drop(lib_df[(lib_df["lib"] == lib)].index, inplace=True)

        except:
            continue

    if dfs:
        lib_df = pd.concat(dfs, ignore_index=True)
        lib_df["XS"] *= 1e-3
        lib_df["Energy"] *= 1e6

    else:
        lib_df = pd.DataFrame()


    return lib_df


# ------------------------------------------------------------------------------
# APP2: Libraries only, for multiple selection of reaction and library
#
#
def read_libs_lib(nuclide, slct_mt_df, slct_lib, groupwise):
    liblist = []
    libfiles = []

    for reac, mt in zip(slct_mt_df["Reaction"], slct_mt_df["MT"]):
        reac = reac.split(",")
        for lib in slct_lib:
            for iso in ISOMERIC:
                lfname = "".join(
                    [
                        LIB_PATH,
                        reac[0],
                        "/",
                        nuclide,
                        "/",
                        lib,
                        "/tables/xs/",
                        reac[0],
                        "-",
                        nuclide,
                        "-MT",
                        mt,
                        iso,
                        "-G1102."
                        if (
                            "G" in groupwise
                            and mt in ["001", "002", "018", "102"]
                            and not nuclide.endswith("000")
                            and reac[0] == "n"
                        )
                        else ".",
                        lib,
                        ".dat"
                    ]
                )
                if os.path.exists(lfname):
                    liblist.append([mt, lib, lfname, iso])

    lib_df2 = create_libdf_lobs(liblist)

    if liblist:
        libfiles = [i[2] for i in liblist]

    return libfiles, lib_df2


def create_libdf_lobs(libfiles):
    dfs2 = []
    for i in range(0, len(libfiles)):
        l = libfiles[i][1]
        mt = libfiles[i][0]
        iso = libfiles[i][3]

        try:  # due to null file such as g + S  33 : (g,a)
            lib_df2 = pd.read_csv(
                libfiles[i][2],
                sep="\s+",
                index_col=None,
                header=None,
                # usecols=[0, 1, 2, 3],
                comment="#",
                names=["Energy", "XS", "xslow", "xsupp"],
            )

            lib_df2["lib"] = l
            lib_df2["MT"] = mt
            lib_df2["isomeric"] = iso

            if lib_df2["XS"].sum() == 0:
                lib_df2.drop(
                    lib_df2[
                        (lib_df2["lib"] == l)
                        & (lib_df2["MT"] == mt)
                        & (lib_df2["isomeric"] == iso)
                    ].index,
                    inplace=True,
                )

            if lib_df2["xslow"].sum() == 0:
                lib_df2["xslow"] = lib_df2["xslow"].replace(0, np.nan)

            if lib_df2["xsupp"].sum() == 0:
                lib_df2["xsupp"] = lib_df2["xsupp"].replace(0, np.nan)

            dfs2.append(lib_df2)

        except:
            continue

    if dfs2:
        lib_df2 = pd.concat(dfs2, ignore_index=True)
        lib_df2["XS"] *= 1e-3
        lib_df2["xslow"] *= 1e-3
        lib_df2["xsupp"] *= 1e-3
        lib_df2["Energy"] *= 1e6

    else:
        lib_df2 = pd.DataFrame()


    return lib_df2
