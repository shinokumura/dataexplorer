####################################################################
#
# This file is part of libraries-2021 dataexplorer, https://nds.iaea.org/dataexplorer/.
# Copyright (C) 2022 International Atomic Energy Agency (IAEA)
#
# Contact:    nds.contact-point@iaea.org
#
####################################################################

import re


def input_check(slct_target, input_mass):
    if slct_target:
        try:
            slct_target = str.capitalize(slct_target)
        except TypeError:
            pass

    if input_mass:
        mass = re.sub(r"\D+", "", input_mass)
        try:
            # iso = re.search(r'([gmnGMN])', input_mass).group(1)
            iso = re.search(r"([a-zA-Z])", input_mass).group(1)
            iso = str(iso).lower()
        except AttributeError:
            iso = ""

        input_mass = str(mass).zfill(3) + iso

    return slct_target, input_mass
