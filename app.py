####################################################################
#
# This file is part of libraries-2021 dataexplorer, https://nds.iaea.org/dataexplorer/.
# Copyright (C) 2022 International Atomic Energy Agency (IAEA)
#
# Contact:    nds.contact-point@iaea.org
#
# Change logs: 
#    First release: 2021-08-20
#    Update libraries: 2022-09-05, JENDL4.0 and TENDL2019 have been replced by JENDL5.0 and TENDL2021
#
####################################################################

import dash
import dash_bootstrap_components as dbc
from config import DEVENV

# Style selection [CERULEAN, COSMO, CYBORG, DARKLY, FLATLY, JOURNAL, LITERA, LUMEN, LUX, MATERIA, MINTY, PULSE, SANDSTONE, SIMPLEX, SKETCHY, SLATE, SOLAR, SPACELAB, SUPERHERO, UNITED, YETI]

if DEVENV:
    app = dash.Dash(
        __name__,
        external_stylesheets=[dbc.themes.FLATLY],
        url_base_pathname="/dataexplorer-2022/",
        suppress_callback_exceptions=True,
        meta_tags=[
            {
                "name": "IAEA Nuclear Data Section",
                "content": "Nuclear Reaction data plot, LIBRARIES-2022, TALYS",
            },
            {"http-equiv": "X-UA-Compatible", "content": "IE=edge"},
            {"name": "viewport", "content": "width=device-width, initial-scale=1.0"},
        ],
    )
    if __name__ == '__main__':
        app.run_server(debug=True, use_reloader=True)

else:
    app = dash.Dash(
        __name__,
        external_stylesheets=[dbc.themes.FLATLY],
        routes_pathname_prefix='/', # if Prod
        requests_pathname_prefix='/dataexplorer-2022/', # if Prod
        suppress_callback_exceptions=True,
        meta_tags=[
            {
                "name": "IAEA Nuclear Data Section",
                "content": "Nuclear Reaction data plot, LIBRARIES-2022, TALYS",
            },
            {"http-equiv": "X-UA-Compatible", "content": "IE=edge"},
            {"name": "viewport", "content": "width=device-width, initial-scale=1.0"},
        ],
    )
    server = app.server   # for PROD/INT env
    app.title = "LIBRARIES-2022 Data Explorer"


#if __name__ == '__main__':
#    app.run_server(debug=True, use_reloader=True)
