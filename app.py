####################################################################
#
# This file is part of libraries-2021 dataexplorer, https://nds.iaea.org/dataexplorer/.
# Copyright (C) 2022 International Atomic Energy Agency (IAEA)
#
# Contact:    nds.contact-point@iaea.org
#
####################################################################

import dash
import dash_bootstrap_components as dbc

# or [CERULEAN, COSMO, CYBORG, DARKLY, FLATLY, JOURNAL, LITERA, LUMEN, LUX, MATERIA, MINTY, PULSE, SANDSTONE, SIMPLEX, SKETCHY, SLATE, SOLAR, SPACELAB, SUPERHERO, UNITED, YETI]


app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.FLATLY],
    url_base_pathname="/dataexplorer/",  # if DEVENV
    # routes_pathname_prefix='/', # if Prod
    # requests_pathname_prefix='/dataexplorer/', # if Prod
    suppress_callback_exceptions=True,
    meta_tags=[
        {
            "name": "IAEA Nuclear Data Section",
            "content": "Nuclear Reaction data plot, LIBRARIES-2020, TALYS",
        },
        {"http-equiv": "X-UA-Compatible", "content": "IE=edge"},
        {"name": "viewport", "content": "width=device-width, initial-scale=1.0"},
    ],
)

# server = app.server   # for PROD/INT env
# app.title = "LIBRARIES-2021 Data Explorer"

if __name__ == '__main__':
    app.run_server(debug=True, use_reloader=True)
