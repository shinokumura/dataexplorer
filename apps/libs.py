####################################################################
#
# This file is part of libraries-2021 dataexplorer.
# Copyright (C) 2022 International Atomic Energy Agency (IAEA)
#
# Contact:    nds.contact-point@iaea.org
#
####################################################################

import pandas as pd
import plotly.express as px  # (version 4.7.0)
import plotly.graph_objects as go

# from plotly.validators.scatter.marker import SymbolValidator

from dash import html
from dash import dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
from dash.exceptions import PreventUpdate
from urllib.parse import urlencode

from datahandle.list import LIB_LIST_MAX, read_mt, color_libs
from datahandle.library_cs import read_libs_lib
from datahandle.checkdata import input_check
from urlparser import parse_state, apply_default_value_lib
from datahandle.genlinks import list_libfiles
from app import app

# ------------------------------------------------------------------------------
# lists definitions
#
mt_df = read_mt()
reaction_list = mt_df["Reaction"]
defaultcolor = "h-25 text-info"

# ------------------------------------------------------------------------------
# App layout


def layout_inputs(params):
    inputs = [
        dbc.Col(
            [
                html.P(
                    [
                        "Multiple Reaction Cross Sections from ",
                        html.A(
                            "ENDFTABLES",
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
                        dbc.Col(
                            apply_default_value_lib(params)(dcc.Input)(
                                id="target_elem2",
                                placeholder="e.g. C, c, Pd, pd, PD",
                                persistence=True,
                                persistence_type="memory",
                                value="Ta",
                                size="30",
                            ),
                            width=6,
                        ),
                        # dbc.Col(html.P('e.g. C, c, Pd, pd, PD')),
                    ]
                ),
                dbc.Row(
                    [
                        dbc.Col(html.Label("Target mass"), width=3),
                        dbc.Col(
                            apply_default_value_lib(params)(dcc.Input)(
                                id="target_mass2",
                                placeholder="e.g. 56, 0 (natural), 242m (metastable)",
                                persistence=True,
                                persistence_type="memory",
                                value="181",
                                size="30",
                            ),
                            width=6,
                        ),
                        # dbc.Col(html.P('e.g. 56, 0 (natural), 242m (metastable)')),
                    ]
                ),
                dbc.Row(
                    [
                        dbc.Col(html.Label("Reaction"), width=3),
                        dbc.Col(
                            apply_default_value_lib(params)(dcc.Dropdown)(
                                id="reaction2",
                                options=[
                                    {"label": reac, "value": reac}
                                    for reac in reaction_list
                                ],
                                multi=True,  # if True, input becomes list object
                                persistence=True,
                                persistence_type="memory",
                                value=["g,xn", "g,2n"]
                                # style={'width': "100%"}
                            ),
                            width=6,
                        ),
                    ]
                ),
                dbc.Row(
                    [
                        dbc.Col(html.Label("Library"), width=3),
                        dbc.Col(
                            apply_default_value_lib(params)(dcc.Dropdown)(
                                id="libs",
                                options=[
                                    {"label": lib, "value": lib} for lib in LIB_LIST_MAX
                                ],
                                multi=True,
                                persistence=True,
                                persistence_type="memory",
                                value=["iaea.pd", "endfb8.0", "jendl5.0"],
                                # style={'width': "100%"}
                            ),
                            width=6,
                        ),
                    ]
                ),
            ],
            className="h-25",
        ),
    ]
    return inputs


layout = (
    dbc.Container(
        [
            html.Br(),
            dcc.Location(id="url_app2", refresh=False),
            # data inputs returs from function
            dbc.Row(id="layout2"),
            html.Br(),
            dbc.Row(
                [
                    # data explanation
                    dbc.Col(html.H5(html.Div(id="output_container_lib")), width=12),
                    # Group wise data switch
                    dbc.Col(
                        dcc.Checklist(
                            id="groupwise_lib",
                            options=[
                                {
                                    "label": " Groupwise (Use 1102 groupwise data if exists)",
                                    "value": "G",
                                }
                            ],
                            value=["G"],
                        ),
                        width="auto",
                    ),
                    # Log/Linear switch
                    dbc.Col(html.Label("X:"), width="auto"),
                    dbc.Col(
                        dcc.RadioItems(
                            id="xaxis_type2",
                            options=[
                                {"label": i, "value": i} for i in ["Linear", "Log"]
                            ],
                            value="Log",
                            persistence=True,
                            persistence_type="memory",
                            labelStyle={"display": "inline-block"},
                        ),
                        width="auto",
                    ),
                    dbc.Col(html.Label("Y:"), width="auto"),
                    dbc.Col(
                        dcc.RadioItems(
                            id="yaxis_type2",
                            options=[
                                {"label": i, "value": i} for i in ["Linear", "Log"]
                            ],
                            value="Log",
                            persistence=True,
                            persistence_type="memory",
                            labelStyle={"display": "inline-block"},
                        ),
                        width="auto",
                    ),
                ],
                justify="end",
            ),
            # Figure and table
            dcc.Graph(
                id="main_graph_lib",
                config={
                    "displayModeBar": True,
                    "scrollZoom": True,
                    "modeBarButtonsToAdd": ["drawline", "drawopenpath", "eraseshape"],
                    "modeBarButtonsToRemove": ["lasso2d"],
                },
                figure={
                    "layout": {
                        "title": "Please select target and reaction.",
                        "height": 650,
                    }
                },
            ),
            html.P(
                "Use the vertical sliders to zoom in on energy.",
                style={"text-align": "center"},
            ),
            dbc.Tabs(
                id="tabs-libs",
                active_tab="dl-libs",
                children=[
                    dbc.Tab(
                        label="Download Data Files",
                        tab_id="dl-libs",
                        children=[html.Div(id="file_list_lib")],
                    )
                ],
            ),
            html.Div(id="stored_libs_lib", style={"display": "none"}),
            html.Div(id="stored_libfiles_lib", style={"display": "none"}),
        ],
        fluid=True,
    ),
)
html.Br()


# URL comming in
@app.callback(Output("layout2", "children"), inputs=[Input("url_app2", "href")])
def page_load(href):
    if not href:
        return []
    state = parse_state(href)
    return layout_inputs(state)


component_ids = ["target_elem2", "target_mass2", "reaction2", "libs"]


# URL going out
@app.callback(
    Output("url_app2", "search"), inputs=[Input(i, "value") for i in component_ids]
)
def update_url_state(*values):
    state = urlencode(dict(zip(component_ids, values)), doseq=True)
    if all(values):
        return f"?{state}"
    else:
        return ""


# ------------------------------------------------------------------------------
# 1. Data read and index_table output
#
#
@app.callback(
    [
        Output("output_container_lib", "children"),
        Output("stored_libs_lib", "children"),
        Output("stored_libfiles_lib", "children"),
    ],
    [
        Input("target_elem2", "value"),
        Input("target_mass2", "value"),
        Input("reaction2", "value"),
        Input("libs", "value"),
        Input("groupwise_lib", "value"),
    ],
)
def builddf2(target_elem2, target_mass2, reaction2, libs, groupwise):
    mt_dff2 = mt_df.copy()
    # inputed reaction and mass to string

    if reaction2:
        reaction2 = list(reaction2)
        slct_mt_df = mt_dff2[mt_dff2.Reaction.isin(reaction2)]
    else:
        slct_mt_df = []

    if libs:
        libs = list(libs)
    else:
        libs = []

    if target_elem2 and target_mass2 and reaction2 and libs:
        elem, mass = input_check(target_elem2, target_mass2)
        nuclide = "".join([elem, mass])
        # print("app2:", nuclide, reaction2, libs)
        selected = nuclide + "(" + "), (".join(r for r in reaction2) + ")"

        libfiles, lib_df2 = read_libs_lib(nuclide, slct_mt_df, libs, groupwise)

    else:
        selected = "No selection"
        raise PreventUpdate

    container = "{}".format(selected)

    return container, lib_df2.to_json(double_precision=13), libfiles


# ------------------------------------------------------------------------------
# 2. Update figure
#
#
@app.callback(
    [Output("main_graph_lib", "figure"), Output("file_list_lib", "children")],
    [
        Input("stored_libs_lib", "children"),
        Input("stored_libfiles_lib", "children"),
        Input("xaxis_type2", "value"),
        Input("yaxis_type2", "value"),
    ],
)
def update_graph_lib(stored_libs_lib, libfiles, xaxis_type2, yaxis_type2):
    # Fig definition
    fig = go.Figure(
        layout=go.Layout(
            # template="plotly_white",
            xaxis={
                "title": "Incident energy [eV]",
                "type": "log" if xaxis_type2 == "Log" else "linear",
                "rangeslider": {
                    "bgcolor": "White",
                    "autorange": True,
                    "thickness": 0.15,
                },
            },
            yaxis={
                "title": "Cross section [barn]",
                "type": "log" if yaxis_type2 == "Log" else "linear",
                "fixedrange": False,
            },
            margin={"l": 40, "b": 40, "t": 30, "r": 0},
        )
    )

    # Expornential format
    fig.update_xaxes(exponentformat="power")
    fig.update_yaxes(exponentformat="power")

    # Re-constract library dataframe and add trace to fig
    try:
        lib_dff2 = pd.read_json(stored_libs_lib)
    except:
        raise PreventUpdate

    # Color difinitions
    # line_color = color_cycle()

    if lib_dff2.empty:
        fig = px.scatter(title="No data found")
        fig.update_layout(title_font_color="orange")

    else:
        mm = lib_dff2["MT"].unique()
        ll = lib_dff2["lib"].unique()
        iso = lib_dff2["isomeric"].unique()
        plot_df = pd.DataFrame()

        for l in ll:
            # new_col = next(line_color)
            line_color = color_libs(l)
            for m in mm:
                mt = str(m).zfill(3)
                new_col = next(line_color)
                for i in iso:
                    plot_df = lib_dff2[
                        (lib_dff2["lib"] == l)
                        & (lib_dff2["MT"] == m)
                        & (lib_dff2["isomeric"] == i)
                    ]
                    labeln = l + "-MT:" + mt + i

                    if i == "":
                        ls = "solid"
                    elif i == "g":
                        ls = "dot"
                    elif i == "m":
                        ls = "dash"

                    x = plot_df["Energy"]
                    y = plot_df["XS"]
                    y_upper = plot_df["xsupp"]
                    y_lower = plot_df["xslow"]

                    trace_upper = go.Scatter(
                        x=x,  # x, then x reversed
                        y=y_upper,  # upper, then lower reversed
                        line=dict(width=0),
                        fillcolor="rgba(191, 191, 191, 0.5)",
                        hoverinfo="skip",
                        showlegend=False,
                        mode="lines",
                    )
                    trace_mean = go.Scatter(
                        x=x,
                        y=y,
                        showlegend=True,
                        name=labeln,
                        mode="lines",
                        line_color=new_col,
                        # line=dict(color='rgb(31, 119, 180)'),
                        fillcolor="rgba(191, 191, 191, 0.5)",
                        line_dash=ls,
                        fill="tonexty",
                    )
                    trace_lower = go.Scatter(
                        x=x,  # x, then x reversed
                        y=y_lower,  # upper, then lower reversed
                        line=dict(width=0),
                        fillcolor="rgba(191, 191, 191, 0.5)",
                        fill="tonexty",
                        hoverinfo="skip",
                        showlegend=False,
                        mode="lines",
                    )
                    fig.add_trace(trace_upper)
                    fig.add_trace(trace_mean)
                    fig.add_trace(trace_lower)

    # for download
    libflinks = list_libfiles(libfiles)
    downloadcorrections = html.Div(
        [
            html.Br(),
            html.P("Files in ENDFTABLES:"),
            html.Div(children=libflinks),
        ]
    )

    return fig, downloadcorrections


# # ------------------------------------------------------------------------------
# if __name__ == '__main__':
#     app.run_server(debug=True, use_reloader=True)
