####################################################################
#
# This file is part of libraries-2021 dataexplorer, https://nds.iaea.org/dataexplorer/.
# Copyright (C) 2022 International Atomic Energy Agency (IAEA)
#
# Contact:    nds.contact-point@iaea.org
#
####################################################################

from urllib.parse import urlparse, parse_qs

# For single selection - app2
def apply_default_value_lib(params):
    def wrapper(func):
        def apply_value(*args, **kwargs):
            if "id" in kwargs and kwargs["id"] in params:
                kwargs["value"] = params[kwargs["id"]]
                if "reaction" in kwargs["id"] or "lib" in kwargs["id"]:
                    pass
                else:
                    kwargs["value"] = ",".join(map(str, kwargs["value"]))
            return func(*args, **kwargs)

        return apply_value

    return wrapper


# For single selection - app1,3,4
def apply_default_value(params):
    def wrapper(func):
        def apply_value(*args, **kwargs):
            if "id" in kwargs and kwargs["id"] in params:
                kwargs["value"] = params[kwargs["id"]]
                kwargs["value"] = ",".join(map(str, kwargs["value"]))
            return func(*args, **kwargs)

        return apply_value

    return wrapper


# Decoding url
def parse_state(url):
    # print (url)
    parse_result = urlparse(url)
    params = parse_qs(parse_result.query)
    state = dict(params)

    return state
