####################################################################
#
# This file is part of libraries-2021 dataexplorer, https://nds.iaea.org/dataexplorer/.
# Copyright (C) 2022 International Atomic Energy Agency (IAEA)
#
# Contact:    nds.contact-point@iaea.org
#
####################################################################

import re
import os

from config import LIB_PATH
from datahandle.list import ztoelem

def residual_sep(residual):
    z = residual[0:3]
    a = residual[3:6]
    m = residual[6:7]
    return z, a, m


def getzz(zz):
    return zz[0]


def list_resid_prod(target, mass, slct_pt3):
    lfiles = []
    path = "".join(
        [LIB_PATH, slct_pt3, "/", target, mass, "/tendl.2021/tables/residual/"]
    )
    if os.path.exists(path):
        lfiles = os.listdir(path)
    else:
        lfiles = []

    rps = []
    if len(lfiles) > 0:
        for f in lfiles:
            rfile = os.path.basename(f)
            rpfname = re.search(r"rp([0-9]{1,6}\w).", rfile).group(1)
            z, a, m = residual_sep(rpfname)
            rp_elem = ztoelem(int(z))
            rp = rp_elem + "-" + a + m
            rp = a, rp
            rps.append(rp)
        rps.sort(key=getzz, reverse=True)
        rps = [i[1] for i in rps]
    else:
        rps = ["no-data"]

    return rps
