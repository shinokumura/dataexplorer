
####################################################################
#
# This file is part of libraries-2021 dataexplorer, https://nds.iaea.org/dataexplorer/.
# Copyright (C) 2022 International Atomic Energy Agency (IAEA)
#
# Contact:    nds.contact-point@iaea.org
#
####################################################################

import dash_bootstrap_components as dbc
from dash import dcc
from dash import html
from dash.dependencies import Input, Output

# Connect to main app.py file
from app import app
from apps import xs, libs, residual, fy
from man import manual

toast = html.Div(
    children=[
        dbc.Col(
            dbc.Button("Tips", id="toast-toggle", color="primary", className="ml-auto")
        ),
        dbc.Col(
            dbc.Toast(
                [html.Div(manual)],
                id="toast",
                header="Tips for LIBRARIES-2022 Data Explorer",
                icon="primary",
                dismissable=True,
                style={
                    "position": "absolute",
                    "top": 10,
                    "right": 10,
                    "width": 850,
                    "maxWidth": "1000px",
                    "zIndex": 1,
                },
                body_style={"background-color": "white", "font-size": "large"},
            )
        ),
    ]
)

navbar = dbc.Navbar(
    [
        dbc.Col(
            html.A([
                html.Img(
                    src=app.get_asset_url("iaea-logo.png"), 
                    height="50px"
                    ),
                ], href="https://nds.iaea.org"),
        ),
        dbc.Col(
            dbc.NavbarBrand(
                "LIBRARIES-2022 Data Explorer", href="https://nds.iaea.org/talys"
            )
        ),
        toast,
    ]
)

app.layout = html.Div(
    [
        navbar,
        html.Br(),
        dbc.Nav(
            [
                dcc.Location(id="url", refresh=False),
                dbc.NavItem(
                    dbc.NavLink(
                        "Cross Section", 
                        href="/dataexplorer/xs", 
                        className="text-primary"
                    ),
                    id="nav1",
                    className="tab",
                ),
                dbc.NavItem(
                    dbc.NavLink(
                        "Multiple Cross Sections (Libs. only)",
                        href="/dataexplorer/libs",
                        className="text-primary",
                    ),
                    id="nav2",
                    className="tab",
                ),
                dbc.NavItem(
                    dbc.NavLink(
                        "Residual Production Cross Section",
                        href="/dataexplorer/residual",
                        className="text-primary",
                    ),
                    id="nav3",
                    className="tab",
                ),
                dbc.NavItem(
                    dbc.NavLink(
                        "Fission Yield", 
                        href="/dataexplorer/fy", 
                        className="text-primary"
                    ),
                    id="nav4",
                    className="tab",
                ),
            ],
            justified=True,
        ),  # className = 'tab-container',),
        html.Div(id="app-contents"),
        html.Br(),
        html.Br(),
        html.Br(),
        html.P(
            [
                "This chart was made with the data from the ",
                html.A("LIBRARIES-2022 package.", href="https://nds.iaea.org/talys", className="text-dark"),
            ], className="text-dark"
        ),
        dbc.Row(
            dbc.Col(
                html.Div(
                    [
                    "Copyright 2022, International Atomic Energy Agency - ",
                    html.A("Nuclear Data Section.", href="https://nds.iaea.org/", className="text-dark"),
                    html.Br(),
                    html.A("Terms of use.", href="https://nucleus.iaea.org/Pages/Others/Terms-Of-Use.aspx", className="text-dark"),
                    html.Br(),
                    "email:",
                    html.A("nds.contact-point@iaea.org", href="mailto:nds.contact-point@iaea.org", className="text-dark")
                    ], style={"text-align": "center"}, className="text-dark",
                )
            )
            # dbc.Col(html.Div("Copyright 2021, xxxx.", style={'text-align': 'center'}))
        ),
    ],
    className="main-wrapper",
)


@app.callback(
    [
        Output("app-contents", "children"),
        Output("nav1", "className"),
        Output("nav2", "className"),
        Output("nav3", "className"),
        Output("nav4", "className"),
    ],
    [Input("url", "pathname")],
)
def display_page(pathname):
    if pathname == "/dataexplorer/xs":
        return xs.layout, "tab-active", "tab", "tab", "tab"
    elif pathname == "/dataexplorer/libs":
        return libs.layout, "tab", "tab-active", "tab", "tab"
    elif pathname == "/dataexplorer/residual":
        return residual.layout, "tab", "tab", "tab-active", "tab"
    elif pathname == "/dataexplorer/fy":
        return fy.layout, "tab", "tab", "tab", "tab-active"
    else:
        return xs.layout, "tab-active", "tab", "tab", "tab"


@app.callback(
    Output("toast", "is_open"),
    [Input("toast-toggle", "n_clicks")],
)
def open_toast(n):
    if n:
        return True
    return False



if __name__ == "__main__":
    app.run_server(use_reloader=True)
    # app.run_server(debug=True, use_reloader=True)
