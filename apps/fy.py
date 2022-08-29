####################################################################
#
# This file is part of libraries-2021 dataexplorer.
# Copyright (C) 2022 International Atomic Energy Agency (IAEA)
#
# Contact:    nds.contact-point@iaea.org
#
####################################################################

import re
from urllib.parse import quote, urlencode

import dash
import dash_bootstrap_components as dbc

# from dash.dash_table.Format import Format, Scheme, Trim
from dash import dcc
from dash import html
import pandas as pd
import plotly.express as px  # (version 4.7.0)
import plotly.graph_objects as go
from dash.dependencies import Input, Output
from dash.exceptions import PreventUpdate
from dash_extensions import Download

from app import app
from datahandle.checkdata import input_check
from datahandle.exfor_fy import read_exfy_a, read_exfy_za
from datahandle.genlinks import list_libfiles, list_exfiles, genzip
from datahandle.index_fy import energy_range, read_index_fy
from datahandle.library_fy import read_libfy
from datahandle.list import (
    ENERGIES,
    YIELD_TYPE,
    PARTICLE_FY,
    MT_LIST_FY,
    color_libs,
    limit_by_datapoints,
)
from datahandle.tabs import create_tabs_fy
from urlparser import parse_state, apply_default_value

# from plotly.validators.scatter.marker import SymbolValidator

defaultcolor = "h-25 text-success"

# ------------------------------------------------------------------------------
# For Fission Product Yield
#


def layout_inputs(params):
    inputs = [
        dbc.Col(
            [
                html.P(
                    [
                        "Fission yields from ",
                        html.A(
                            "ENDFTABLES and EXFORTABLES",
                            href="https://nds.iaea.org/talys",
                            className=defaultcolor,
                        ),
                    ]
                ),
            ],
            width=3,
            className=defaultcolor,
        ),
        dbc.Col(
            [
                dbc.Row(
                    [
                        dbc.Col(html.Label("Target element"), width=3),
                        # dbc.Col(apply_default_value(params)(dcc.Input)(
                        dbc.Col(
                            # dcc.Input(
                            apply_default_value(params)(dcc.Input)(
                                id="fissile_elem",
                                # options=[{'label':elem, 'value':elem} for elem in elem_list],
                                placeholder="e.g. U, u, Am, am, AM",
                                persistence=True,
                                persistence_type="memory",
                                value="Pu",
                                size="30",
                            )
                        ),
                        # dbc.Col(html.P('e.g. U, u, Am, am, AM')),
                    ]
                ),
                dbc.Row(
                    [
                        dbc.Col(html.Label("Target mass"), width=3),
                        dbc.Col(
                            apply_default_value(params)(dcc.Input)(
                                id="fissile_mass",
                                placeholder="e.g. 235, 242m (metastable)",
                                persistence=True,
                                persistence_type="memory",
                                value="239",
                                size="30",
                            )
                        ),
                        # dbc.Col(html.Dd('e.g. 235, 242m (metastable)')),
                    ]
                ),
                dbc.Row(
                    [
                        dbc.Col(html.Label("Reaction"), width=3),
                        dbc.Col(
                            apply_default_value(params)(dcc.Dropdown)(
                                id="inc_pt4",
                                options=[
                                    {"label": pt + ",f", "value": pt}
                                    for pt in PARTICLE_FY
                                ],
                                multi=False,
                                clearable=True,
                                persistence=True,
                                persistence_type="memory",
                                value="n",
                            ),
                            width=4,
                        ),
                        # dbc.Col(html.Dd('Select 0 for spontanious fission.')),
                    ]
                ),
                dbc.Row(
                    [
                        dbc.Col(html.Label("Fission yield type"), width=3),
                        dbc.Col(
                            apply_default_value(params)(dcc.Dropdown)(
                                id="fy_type",
                                options=[
                                    {"label": yt, "value": yt} for yt in YIELD_TYPE
                                ],
                                value="Independent",
                            ),
                            width=4,
                        ),
                    ]
                ),
                dbc.Row(
                    [
                        dbc.Col(html.Label("Incident Energy"), width=3),
                        dbc.Col(
                            apply_default_value(params)(dcc.Dropdown)(
                                id="inc_energy",
                                multi=False,
                                clearable=True,
                                persistence=True,
                                persistence_type="memory",
                                options=[{"label": e, "value": e} for e in ENERGIES],
                                value="eV",
                            ),
                            width=4,
                        ),
                        # dbc.Col(html.Dd('eV (thermal), keV (fast), MeV (high), 0 (SF)')),
                    ]
                ),
            ],
            className="h-25",
        ),
    ]
    return inputs


tabs_inputs_a = create_tabs_fy("a")
tabs_inputs_za = create_tabs_fy("za")

layout = (
    dbc.Container(
        [
            html.Br(),
            dcc.Location(id="url_app4", refresh=False),
            # data inputs returs from function
            dbc.Row(id="layout4"),
            # Y(A) plot
            html.Br(),
            dbc.Col(html.H5(html.Div(id="output_container_fy")), width=12),
            dbc.Row(
                [
                    # right plot
                    dbc.Col(
                        [
                            # Linear / Log Swicher
                            dcc.RadioItems(
                                id="yaxis_ya",
                                options=[
                                    {"label": i, "value": i} for i in ["Linear", "Log"]
                                ],
                                value="Linear",
                                labelStyle={"display": "inline-block"},
                            ),
                            # Main graph
                            dcc.Graph(
                                id="main_graph_a",
                                config={"displayModeBar": True},
                                figure={
                                    "layout": {
                                        "title": "Please select target and reaction.",
                                        "height": 550,
                                        "autosize": True,
                                    }
                                },
                            ),
                            html.P("Y(A) data."),
                            # tabs for Y(Z,A)
                            tabs_inputs_a,
                        ],
                        lg=6,
                    ),
                    # left plane
                    dbc.Col(
                        [
                            dbc.Row(
                                [
                                    # Linear / Log Swicher
                                    dbc.Col(
                                        dcc.RadioItems(
                                            id="yaxis_za",
                                            options=[
                                                {"label": i, "value": i}
                                                for i in ["Linear", "Log"]
                                            ],
                                            value="Log",
                                            labelStyle={"display": "inline-block"},
                                        )
                                    ),
                                    dbc.Col(html.H6("Display at A:")),
                                    dbc.Col(
                                        dcc.Input(
                                            id="fpmass",
                                            type="number",
                                            value=132,
                                            max=180,
                                        )
                                    ),
                                ],
                                justify="end",
                            ),
                            # Y(Z,A) graph
                            dcc.Graph(
                                id="sub_graph_za",
                                config={"displayModeBar": True},
                                figure={
                                    "layout": {
                                        "title": "Please select target and reaction.",
                                        "height": 550,
                                        "autosize": True,
                                    }
                                },
                            ),
                            html.P("Y(Z,A) data."),
                            # tabs for Y(Z,A)
                            tabs_inputs_za,
                        ],
                        lg=6,
                    ),
                ]
            ),
            # Hiddnen
            html.Div(id="stored_input_fy", style={"display": "none"}),
            html.Div(id="stored_lib_za", style={"display": "none"}),
            html.Div(id="stored_lib_a", style={"display": "none"}),
            html.Div(id="stored_index_a", style={"display": "none"}),
            html.Div(id="stored_index_za", style={"display": "none"}),
            html.Div(id="stored_ex_a", style={"display": "none"}),
            html.Div(id="stored_ex_za", style={"display": "none"}),
            # html.Div(id='stored_libfiles_a', style={'display': 'none'}),
            html.Div(id="stored_libfiles_za", style={"display": "none"}),
            html.Div(id="stored_exfiles_a", style={"display": "none"}),
            html.Div(id="stored_exfiles_za", style={"display": "none"}),
        ],
        fluid=True,
    ),
)
html.Br()


# URL comming in
@app.callback(Output("layout4", "children"), inputs=[Input("url_app4", "href")])
def page_load(href):
    if not href:
        return []
    state = parse_state(href)
    return layout_inputs(state)


component_fy = ["fissile_elem", "fissile_mass", "inc_pt4", "inc_energy", "fy_type"]

# URL going out
@app.callback(
    Output("url_app4", "search"), inputs=[Input(i, "value") for i in component_fy]
)
def update_url_state(*values):
    state = urlencode(dict(zip(component_fy, values)), doseq=True)
    # print(values)
    if all(values):
        return f"?{state}"
    else:
        return ""


@app.callback(
    [
        Output("output_container_fy", "children"),
        Output("stored_input_fy", "children"),
        Output("index_table_a", "selected_rows"),
        Output("index_table_a", "data"),
        Output("index_table_za", "selected_rows"),
        Output("index_table_za", "data"),
        Output("stored_lib_za", "children"),
        Output("stored_lib_a", "children"),
        #  Output('stored_libfiles_a'   , 'children'),
        Output("stored_libfiles_za", "children"),
        Output("stored_index_a", "children"),
        Output("stored_index_za", "children"),
    ],
    [
        Input("fissile_elem", "value"),
        Input("fissile_mass", "value"),
        Input("inc_pt4", "value"),
        Input("inc_energy", "value"),
        Input("fy_type", "value"),
    ],
)
def load_index(fissile_elem, fissile_mass, inc_pt4, inc_energy, fy_type):
    if fy_type:
        for i in MT_LIST_FY:
            if fy_type in i:
                j = MT_LIST_FY.index(i)
                mt = MT_LIST_FY[j][1]
    else:
        mt = ""

    if fissile_elem and fissile_mass and inc_pt4 and inc_energy and fy_type:
        # print("FPY:", fissile_elem, fissile_mass, inc_pt4, inc_energy, fy_type)
        # Input data check
        fis_elem, fis_mass = input_check(fissile_elem, fissile_mass)
        nuclide = "".join([fis_elem, fis_mass])
        min_einc, max_einc = energy_range(inc_energy)
        userinput = "".join([nuclide, "-", inc_pt4, "-", mt])

        # Read Library data
        libfilesza, lib_a_df, lib_za_df = read_libfy(
            nuclide, inc_pt4, mt, inc_energy, fy_type
        )

        # Read EXFOR data
        index_a_df, index_za_df = read_index_fy(
            nuclide, inc_pt4, mt, min_einc, max_einc
        )

        selected = "".join(
            [
                nuclide,
                "(",
                inc_pt4,
                ",f) at E:",
                inc_energy,
                ", found ",
                str(len(index_a_df)),
                " Y(A) and ",
                str(len(index_za_df)),
                " Y(Z,A) experimental dataset(s).",
            ]
        )
    else:
        index_a_df = pd.DataFrame
        index_za_df = pd.DataFrame
        selected = "No selection"

    if not index_a_df.empty:
        default_sel_a = limit_by_datapoints(index_a_df)
    else:
        default_sel_a = []

    if not index_za_df.empty:
        default_sel_za = limit_by_datapoints(index_za_df)
    else:
        default_sel_za = []

    # selected = fis_elem + fis_mass + "(" + inc_pt4 + ",f)  MF:8  MT:" + mt
    # container = "Plot for:  {}".format(selected)

    return (
        selected,
        userinput,
        default_sel_a,
        index_a_df.to_dict("records"),
        default_sel_za,
        index_za_df.to_dict("records"),
        lib_za_df.to_json(),
        lib_a_df.to_json(),
        libfilesza,
        index_a_df.to_json(),
        index_za_df.to_json(),
    )


# ------------------------------------------------------------------------------
#  Read Y(A)
#
#
@app.callback(
    [Output("stored_exfiles_a", "children"), Output("stored_ex_a", "children")],
    [
        Input("stored_input_fy", "children"),
        Input("stored_index_a", "children"),
        Input("index_table_a", "selected_rows"),
    ],
)
def build_expdf(userinput, stored_index_a, slctd_rows):
    if userinput:
        nuclide, inc_pt4, mt = userinput.split("-")
    else:
        raise PreventUpdate
    try:
        index_a_dff = pd.read_json(stored_index_a)
    except:
        raise PreventUpdate

    if not index_a_dff.empty:
        ee = index_a_dff["entry"].iloc[slctd_rows].to_list()
        nn = index_a_dff["einc"].iloc[slctd_rows].to_list()
        # ee = [index_a_dff[x].values.tolist() for x in ['entry', 'einc']]
    else:
        ee = []
        nn = []

    # Read exfor data
    # exfiles, exfor_df = read_exfy(nuclide, reaction, mt, inc_energy)
    exfilesa, exya_df = read_exfy_a(nuclide, inc_pt4, mt, ee, nn)

    return exfilesa, exya_df.to_json(double_precision=12)


# ------------------------------------------------------------------------------
#  Read Y(Z,A)
#
#
@app.callback(
    [Output("stored_exfiles_za", "children"), Output("stored_ex_za", "children")],
    [
        Input("stored_input_fy", "children"),
        Input("stored_index_za", "children"),
        Input("index_table_za", "selected_rows"),
    ],
)
def build_exza(userinput, stored_index_za, slctd_rows_za):
    if userinput:
        nuclide, inc_pt4, mt = userinput.split("-")
    else:
        raise PreventUpdate
    try:
        index_za_dff = pd.read_json(stored_index_za)
    except:
        raise PreventUpdate

    if not index_za_dff.empty:
        # print(index_za_dff)
        ee2 = index_za_dff["entry"].iloc[slctd_rows_za].to_list()
        nn2 = index_za_dff["einc"].iloc[slctd_rows_za].to_list()
        # ee = [index_a_dff[x].values.tolist() for x in ['entry', 'einc']]
    else:
        ee2 = []
        nn2 = []

    exfilesza, exza_df = read_exfy_za(nuclide, inc_pt4, mt, ee2, nn2)

    return exfilesza, exza_df.to_json(double_precision=12)


# ------------------------------------------------------------------------------
# Graph update for Y(A)
#
#
@app.callback(
    [
        Output("main_graph_a", "figure"),
        Output("exfor_table_a", "data"),
        Output("file_list_a", "children"),
    ],
    [
        Input("stored_ex_a", "children"),
        Input("stored_lib_a", "children"),
        Input("tabs-a", "active_tab"),
        Input("yaxis_ya", "value"),
        #  Input('stored_libfiles_a'    , 'children'),
        Input("stored_exfiles_a", "children"),
    ],
)
def update_ya_graph(stored_ex_a, stored_lib_a, slctd_tab, yaxis_ya, exfiles):

    fig = go.Figure(
        layout=go.Layout(
            xaxis={"title": "Mass number", "type": "linear", "dtick": 10},
            yaxis={
                "title": "Fission yields [/fission]",
                "type": "linear" if yaxis_ya == "Linear" else "log",
                "exponentformat": "power",
            },
            margin={"l": 40, "b": 40, "t": 30, "r": 0},
        )
    )

    try:
        # Re-constract library dataframe and add trace to fig
        libya_dff = pd.read_json(stored_lib_a)

        # Re-constract EXFOR dataframe and add trace to fig
        exya_dff = pd.read_json(stored_ex_a)

    except:
        raise PreventUpdate

    if not libya_dff.empty:
        ll = libya_dff["lib"].unique()
        for l in ll:
            line_color = color_libs(l)
            new_col = next(line_color)
            fig.add_trace(
                go.Scatter(
                    x=libya_dff[libya_dff["lib"] == l]["A"],
                    y=libya_dff[libya_dff["lib"] == l]["FPY"],
                    showlegend=True,
                    line_color=new_col,
                    name=l,
                    mode="lines",
                )
            )

    if not exya_dff.empty:
        ee = exya_dff["entry"].unique()
        i = 0

        for e in ee:
            nn = exya_dff[exya_dff["entry"] == e]["Einc"].unique()

            for n in nn:
                label = str(
                    exya_dff[exya_dff["entry"] == e]["author"].unique()
                    + ","
                    + "{:.2e}".format(n)
                )
                label = re.sub("\[|\]|'", "", label)

                fig.add_trace(
                    go.Scatter(
                        x=exya_dff[(exya_dff["entry"] == e) & (exya_dff["Einc"] == n)][
                            "A"
                        ],
                        y=exya_dff[(exya_dff["entry"] == e) & (exya_dff["Einc"] == n)][
                            "FPY"
                        ],
                        error_y=dict(
                            type="data",
                            array=exya_dff[
                                (exya_dff["entry"] == e) & (exya_dff["Einc"] == n)
                            ]["dFPY"],
                        ),
                        showlegend=True,
                        name=label,
                        marker=dict(size=8, symbol=i),
                        mode="markers",
                    )
                )
                i += 1

    if libya_dff.empty and exya_dff.empty:
        fig = px.scatter(title="No data found")
        fig.update_layout(title_font_color="orange")

    if slctd_tab == "ds-a":
        return fig, dash.no_update, dash.no_update

    if slctd_tab == "datatable-a":
        return fig, exya_dff.to_dict("records"), dash.no_update

    elif slctd_tab == "dl-a":
        exya_dff = exya_dff[
            ["author", "year", "entry", "Einc", "dEinc", "Z", "A", "Iso", "FPY", "dFPY"]
        ]
        csv_string = exya_dff.to_csv(index=False, encoding="utf-8")
        csv_string = "data:text/csv;charset=utf-8," + quote(csv_string)

        # libflinks = list_libfiles(libfiles)
        exflinks = list_exfiles(exfiles, slctd_tab)

        downloadcorrections = html.Div(
            [
                html.Br(),
                html.P(
                    "Download a CSV file with selected experimental dataset used for the visualization chart:"
                ),
                html.A(
                    "CSV file", download="csdata.csv", href=csv_string, target="_blank"
                ),
                html.Br(),
                html.Br(),
                html.P("Files in EXFORTABLES:"),
                html.Div(
                    [html.Button("Download zip", id="btn_zip-a"), Download(id="zip-a")]
                ),
                html.Br(),
                html.Div(children=exflinks),
                html.Br(),
                # html.Br(),
                # html.P("Files in ENDFTABLES:"),
                # html.Div(children=libflinks),
            ]
        )
        return fig, dash.no_update, downloadcorrections


@app.callback(
    Output("zip-a", "data"),
    [
        Input("btn_zip-a", "n_clicks"),
        Input("stored_exfiles_a", "children"),
        Input("tabs-a", "active_tab"),
    ],
)
def func(n_clicks, exfiles, slctd_tab):
    if exfiles:
        if n_clicks:
            return genzip(exfiles, slctd_tab)

    if not exfiles:
        if n_clicks:
            return dash.no_update


# ------------------------------------------------------------------------------
# 3. Make Y(Z, A) plot
#
#
@app.callback(
    [
        Output("sub_graph_za", "figure"),
        Output("exfor_table_za", "data"),
        Output("file_list_za", "children"),
    ],
    [
        Input("stored_lib_za", "children"),
        Input("stored_ex_za", "children"),
        Input("fpmass", "value"),
        Input("tabs-za", "active_tab"),
        Input("yaxis_za", "value"),
        Input("stored_libfiles_za", "children"),
        Input("stored_exfiles_za", "children"),
    ],
)
def update_yza_graph(
    stored_lib_za, stored_ex_za, fpmass, slctd_tab, yaxis_za, libfiles, exfiles
):
    fig2 = go.Figure(
        layout=go.Layout(
            xaxis={
                "title": "Charge number",
                "type": "linear",
                "dtick": 1,
            },
            yaxis={
                "title": "Fission yields [/fission]",
                "type": "log" if yaxis_za == "Log" else "linear",
                "exponentformat": "power",
            },
            margin={"l": 40, "b": 40, "t": 30, "r": 0},
        )
    )

    try:
        # Re-constract library/experiment dataframe to add trace to fig
        libfy_dff = pd.read_json(stored_lib_za)
        exfy_dff = pd.read_json(stored_ex_za)

    except:
        raise PreventUpdate

    if not libfy_dff.empty:
        libfy_dff = libfy_dff[libfy_dff["A"] == fpmass]
        ll = libfy_dff["lib"].unique()
        for l in ll:
            # new_col = next(line_color)
            line_color = color_libs(l)
            new_col = next(line_color)
            fig2.add_trace(
                go.Scatter(
                    x=libfy_dff[(libfy_dff["lib"] == l) & (libfy_dff["M"] == 0)]["Z"],
                    y=libfy_dff[(libfy_dff["lib"] == l) & (libfy_dff["M"] == 0)]["FPY"],
                    error_y=dict(
                        type="data",
                        array=libfy_dff[
                            (libfy_dff["lib"] == l) & (libfy_dff["M"] == 0)
                        ]["dFPY"],
                    ),
                    showlegend=True,
                    line_color=new_col,
                    name=l,
                    mode="lines",
                )
            )

    if not exfy_dff.empty:
        exfy_dff = exfy_dff[exfy_dff["A"] == fpmass]
        ee = exfy_dff["entry"].unique()

        i = 0

        for e in ee:
            nn = exfy_dff[exfy_dff["entry"] == e]["Einc"].unique()

            for n in nn:
                label = str(
                    exfy_dff[exfy_dff["entry"] == e]["author"].unique()
                    + ","
                    + "{:.2e}".format(n)
                )
                label = re.sub("\[|\]|'", "", label)

                fig2.add_trace(
                    go.Scatter(
                        x=exfy_dff[exfy_dff["entry"] == e]["Z"],
                        y=exfy_dff[exfy_dff["entry"] == e]["FPY"],
                        error_y=dict(
                            type="data", array=exfy_dff[exfy_dff["entry"] == e]["dFPY"]
                        ),
                        showlegend=True,
                        name=label,
                        marker=dict(size=8, symbol=i),
                        mode="markers",
                    )
                )
                i += 1

    if libfy_dff.empty and exfy_dff.empty:
        fig2 = px.scatter(title="No data found")
        fig2.update_layout(title_font_color="orange")

    if slctd_tab == "ds-za":
        return fig2, dash.no_update, dash.no_update

    if slctd_tab == "datatable-za":
        return fig2, exfy_dff.to_dict("records"), dash.no_update

    elif slctd_tab == "dl-za":
        exfy_dff = exfy_dff[
            ["author", "year", "entry", "Einc", "dEinc", "Z", "A", "Iso", "FPY", "dFPY"]
        ]
        csv_string = exfy_dff.to_csv(index=False, encoding="utf-8")
        csv_string = "data:text/csv;charset=utf-8," + quote(csv_string)

        libflinks = list_libfiles(libfiles)
        exflinks = list_exfiles(exfiles, slctd_tab)

        downloadcorrections = html.Div(
            [
                html.Br(),
                html.P(
                    "Download a CSV file with selected experimental dataset used for the visualization chart:"
                ),
                html.A(
                    "CSV file", download="csdata.csv", href=csv_string, target="_blank"
                ),
                html.Br(),
                html.Br(),
                html.P("Files in EXFORTABLES:"),
                html.Div(
                    [
                        html.Button("Download zip", id="btn_zip-za"),
                        Download(id="zip-za"),
                    ]
                ),
                html.Br(),
                html.Div(children=exflinks),
                html.Br(),
                html.Br(),
                html.P("Files in ENDFTABLES:"),
                html.Div(children=libflinks),
            ]
        )
        return fig2, dash.no_update, downloadcorrections


@app.callback(
    Output("zip-za", "data"),
    [
        Input("btn_zip-za", "n_clicks"),
        Input("stored_exfiles_za", "children"),
        Input("tabs-za", "active_tab"),
    ],
)
def func(n_clicks, exfiles, slctd_tab):
    if exfiles:
        if n_clicks:
            return genzip(exfiles, slctd_tab)

    if not exfiles:
        if n_clicks:
            return dash.no_update


# # ------------------------------------------------------------------------------
# if __name__ == '__main__':
#     app.run_server(debug=True, use_reloader=True)
