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
from dash import html
from dash import dcc
import zipfile
from dash_extensions.snippets import send_bytes
from urllib.parse import quote as urlquote

from config import EXP_PATH, DATA_ROOT_FOLDER


def list_libfiles(libfiles):
    libflinks = []
    for lf in libfiles:
        
        filename = os.path.basename(lf)
        dirname = os.path.dirname(lf)
        linkdir = dirname.replace(DATA_ROOT_FOLDER, "")

        fullpath = os.path.join(linkdir, filename)
        a = html.A(
            filename, download=filename, href=fullpath, target="_blank"
        )

        libflinks.append(a)
        libflinks.append(html.Br())

    return libflinks


def list_exfiles(exfiles, slctd_tab):
    if slctd_tab == "dl-cs":
        dirname = "xs/"
    if slctd_tab == "dl-rp":
        dirname = "residual/"
    if slctd_tab == "dl-a" or slctd_tab == "dl-za":
        dirname = "FY/"

    exflinks = []

    for ef in exfiles:
        if ".list" in ef:
            continue
        else:
            datasetname = re.split("[-.]", ef)


        if slctd_tab == "dl-a" or slctd_tab == "dl-za":
            fullpath = "".join(
                [
                    "libraries/",
                    dirname,
                    datasetname[0],
                    "/",
                    datasetname[1],
                    "/exfor/",
                    datasetname[2].replace("MT", ""),
                    "/",
                    ef,
                ]
            )

        elif slctd_tab == "dl-rp":
            fullpath = "".join(
                [
                    "libraries/",
                    datasetname[0],
                    "/",
                    datasetname[1],
                    "/exfor/",
                    dirname,
                    datasetname[2].replace("rp", ""),
                    "/",
                    ef,
                ]
            )

        else:
            fullpath = "".join(
                [
                    "libraries/",
                    datasetname[0],
                    "/",
                    datasetname[1],
                    "/exfor/",
                    dirname,
                    datasetname[2].replace("MT", ""),
                    "/",
                    ef,
                ]
            )

        a = html.A(ef, download=ef, href=fullpath, target="_blank")
        exflinks.append(a)
        exflinks.append(html.Br())

    return exflinks


def genzip(exfiles, slctd_tab):
    if slctd_tab == "dl-cs":
        dirname = "xs/"
    if slctd_tab == "dl-rp":
        dirname = "residual/"
    if slctd_tab == "dl-a" or slctd_tab == "dl-za":
        dirname = "FY/"

    def write_archive(bytes_io):
        with zipfile.ZipFile(bytes_io, mode="w") as zf:
            for ef in exfiles:
                if ".list" in ef:
                    continue
                else:
                    datasetname = re.split("[-.]", ef)

                if slctd_tab == "dl-a" or slctd_tab == "dl-za":
                    fullpath = "".join(
                        [
                            EXP_PATH,
                            dirname,
                            datasetname[0],
                            "/",
                            datasetname[1],
                            "/exfor/",
                            datasetname[2].replace("MT", ""),
                            "/",
                            ef,
                        ]
                    )

                elif slctd_tab == "dl-rp":
                    fullpath = "".join(
                        [
                            EXP_PATH,
                            datasetname[0],
                            "/",
                            datasetname[1],
                            "/exfor/",
                            dirname,
                            datasetname[2].replace("rp", ""),
                            "/",
                            ef,
                        ]
                    )

                else:
                    fullpath = "".join(
                        [
                            EXP_PATH,
                            datasetname[0],
                            "/",
                            datasetname[1],
                            "/exfor/",
                            dirname,
                            datasetname[2].replace("MT", ""),
                            "/",
                            ef,
                        ]
                    )

                zf.write(fullpath, arcname="".join(["exfortables/", ef]))

    return send_bytes(write_archive, "exfortables.zip")
