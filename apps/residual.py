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

import dash
from dash import dcc
from dash import html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
from dash.exceptions import PreventUpdate
from dash_extensions import Download

from urllib.parse import quote, urlencode
import re

from datahandle.list import PARTICLE, read_mt, color_libs, limit_by_datapoints
from datahandle.index_cs import read_index_rp
from datahandle.exfor_cs import read_resid_prod_exfor
from datahandle.library_cs import read_resid_prod_lib
from datahandle.list_rp import list_resid_prod
from datahandle.checkdata import input_check
from datahandle.figs import default_chart
from datahandle.tabs import create_tabs
from datahandle.genlinks import list_libfiles, list_exfiles, genzip
from urlparser import parse_state, apply_default_value
from app import app

# ------------------------------------------------------------------------------
# lists definitions
#
mt_df = read_mt()
reaction_list = mt_df["Reaction"]
defaultcolor = "h-25 text-danger"

# ------------------------------------------------------------------------------
#
# For residual production
#
tooltip = html.Div(
    [
        html.P(
            [
                html.Span(
                    "Residual products in TENDL-2021",
                    id="tooltip-target",
                    style={
                        "textDecoration": "underline",
                        "cursor": "pointer",
                        "float": "right",
                    },
                )
            ]
        ),
        dbc.Tooltip(
            id="tooltip-origin",
            target="tooltip-target",
            style={"background": "SteelBlue"},
        ),
        html.Br(),
    ]
)

# ------------------------------------------------------------------------------
#
# Input part
#
def layout_inputs(params):
    inputs = [
        dbc.Col(
            [
                html.P(
                    [
                        "Residual Production from ",
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
                        dbc.Col(
                            apply_default_value(params)(dcc.Input)(
                                id="target_elem3",
                                # options=[{'label':elem, 'value':elem} for elem in elem_list],
                                # multi=False,
                                placeholder="e.g. C, c, Pd, pd, PD",
                                persistence=True,
                                persistence_type="memory",
                                value="Mo",
                                size="30",
                                # style={'width': "100%"}
                            ),
                            width=4,
                        ),
                        # dbc.Col(html.Dd('e.g. C, c, Pd, pd, PD')),
                    ]
                ),
                dbc.Row(
                    [
                        dbc.Col(html.Label("Target mass"), width=3),
                        dbc.Col(
                            apply_default_value(params)(dcc.Input)(
                                id="target_mass3",
                                # type="number",
                                placeholder="e.g. 56, 0 (natural), 242m (metastable)",
                                persistence=True,
                                persistence_type="memory",
                                value="100",
                                size="30",
                            ),
                            width=4,
                        ),
                        # dbc.Col(html.Dd('e.g. 56, 0 (natural), 242m (metastable)')),
                    ]
                ),
                dbc.Row(
                    [
                        dbc.Col(html.Label("Reaction"), width=3),
                        dbc.Col(
                            apply_default_value(params)(dcc.Dropdown)(
                                id="inc_pt",
                                options=[
                                    {"label": pt + ",x", "value": pt} for pt in PARTICLE
                                ],
                                multi=False,  # if True, input becomes list object
                                persistence=True,
                                persistence_type="memory",
                                value="p",
                            ),
                            width=4,
                        ),
                    ]
                ),
                dbc.Row(
                    [
                        dbc.Col(html.Label("Residual element"), width=3),
                        dbc.Col(
                            apply_default_value(params)(dcc.Input)(
                                id="rp_elem",
                                placeholder="e.g. F, f, Mo, mo, MO",
                                # multi=False,
                                persistence=True,
                                persistence_type="memory",
                                value="Tc",
                                size="30",
                            ),
                            width=4,
                        ),
                        # dbc.Col(html.Dd('e.g. F, f, Mo, mo, MO')),
                    ]
                ),
                dbc.Row(
                    [
                        dbc.Col(html.Label("Residual mass"), width=3),
                        dbc.Col(
                            apply_default_value(params)(dcc.Input)(
                                id="rp_mass",
                                placeholder="e.g. 56, 99g (ground), 99m(metastable)",
                                # multi=False,
                                persistence=True,
                                persistence_type="memory",
                                value="99m",
                                size="30",
                            ),
                            width=4,
                        ),
                        # dbc.Col(html.Dd('e.g. 56, 99g (ground), 99m(metastable)')),
                    ]
                ),
            ],
            className="h-25",
        ),
    ]
    return inputs


tabs_inputs = create_tabs("rp")

layout = (
    dbc.Container(
        [
            html.Br(),
            dcc.Location(id="url_app3", refresh=False),
            # data inputs returs from function
            dbc.Row(id="layout3"),
            # to show possible residual products
            tooltip,
            html.Br(),
            # Log/Linear switch
            dbc.Row(
                [
                    # data explanation
                    dbc.Col(html.H5(html.Div(id="output_container_rp")), width=12),
                    dbc.Col(html.Label("X:"), width="auto"),
                    dbc.Col(
                        dcc.RadioItems(
                            id="xaxis_type3",
                            options=[
                                {"label": i, "value": i} for i in ["Linear", "Log"]
                            ],
                            value="Linear",
                            persistence=True,
                            persistence_type="memory",
                            labelStyle={"display": "inline-block"},
                        ),
                        width="auto",
                    ),
                    dbc.Col(html.Label("Y:"), width="auto"),
                    dbc.Col(
                        dcc.RadioItems(
                            id="yaxis_type3",
                            options=[
                                {"label": i, "value": i} for i in ["Linear", "Log"]
                            ],
                            value="Linear",
                            persistence=True,
                            persistence_type="memory",
                            labelStyle={"display": "inline-block"},
                        ),
                        width="auto",
                    ),
                ],
                justify="end",
            ),
            # Main Graph Object
            dcc.Graph(
                id="main_graph_rp",
                config={
                    "displayModeBar": True,
                    "scrollZoom": True,
                    "modeBarButtonsToAdd": ["drawline", "drawopenpath", "eraseshape"],
                    "modeBarButtonsToRemove": ["lasso2d"],
                },
                figure={
                    "layout": {
                        "title": "Please select target and reaction.",
                        "height": 550,
                    }
                },
            ),
            html.P(
                "Use the vertical sliders to zoom in on energy.",
                style={"text-align": "center"},
            ),
            # Tables and download file list in Tabs
            tabs_inputs,
            # Hidden table
            html.Div(id="stored_input_rp", style={"display": "none"}),
            html.Div(id="stored_libs_rp", style={"display": "none"}),
            html.Div(id="stored_exps_rp", style={"display": "none"}),
            html.Div(id="stored_index_rp", style={"display": "none"}),
            html.Div(id="stored_libfiles_rp", style={"display": "none"}),
            html.Div(id="stored_exfiles_rp", style={"display": "none"}),
        ],
        fluid=True,
    ),
)
html.Br()


@app.callback(Output("layout3", "children"), inputs=[Input("url_app3", "href")])
def page_load(href):
    if not href:
        return []
    state = parse_state(href)
    return layout_inputs(state)


component_ids = ["target_elem3", "target_mass3", "inc_pt", "rp_elem", "rp_mass"]


@app.callback(
    Output("url_app3", "search"), inputs=[Input(i, "value") for i in component_ids]
)
def update_url_state(*values):
    state = urlencode(dict(zip(component_ids, values)), doseq=True)
    if all(values):
        return f"?{state}"
    else:
        return ""


# ------------------------------------------------------------------------------
# Read selection of residual product from tendl.2019
#


@app.callback(
    Output("tooltip-origin", "children"),
    [
        Input("target_elem3", "value"),
        Input("target_mass3", "value"),
        Input("inc_pt", "value"),
    ],
)
def update_rpdropdown(target_elem3, target_mass3, inc_pt):
    if target_elem3 and target_mass3 and inc_pt:
        target, mass = input_check(target_elem3, target_mass3)

        rps = list_resid_prod(target, mass, inc_pt)
        rps = ", ".join([str(elem) for elem in rps])

    else:
        # raise PreventUpdate
        rps = []
    return rps


# ------------------------------------------------------------------------------
# 1. Data read and index_table output
#
#
@app.callback(
    [
        Output("output_container_rp", "children"),
        Output("stored_input_rp", "children"),
        Output("index_table_rp", "selected_rows"),
        Output("index_table_rp", "data"),
        Output("stored_libs_rp", "children"),
        Output("stored_libfiles_rp", "children"),
        Output("stored_index_rp", "children"),
    ],
    [
        Input("target_elem3", "value"),
        Input("target_mass3", "value"),
        Input("inc_pt", "value"),
        Input("rp_elem", "value"),
        Input("rp_mass", "value"),
    ],
)
def load_index_rp(target_elem3, target_mass3, inc_pt, rp_elem, rp_mass):
    if rp_elem and rp_mass:
        # input check
        elem, mass = input_check(target_elem3, target_mass3)
        nuclide = "".join([elem, mass])
        rp_elem, rp_mass = input_check(rp_elem, rp_mass)
        userinput = "".join([nuclide, "-", inc_pt, "-", rp_elem, "-", rp_mass])

        # print("app3:", nuclide, inc_pt, rp_elem, rp_mass)

        # read libraries
        rplibfiles, rplib_df = read_resid_prod_lib(nuclide, inc_pt, rp_elem, rp_mass)

        # read EXFOR index file
        rpindex_df = read_index_rp(nuclide, inc_pt, rp_elem, rp_mass)

        if not rpindex_df.empty:
            default_sel = limit_by_datapoints(rpindex_df)
        else:
            default_sel = list(range(10))

        # To display
        selected = (
            nuclide
            + "("
            + inc_pt
            + ",x)"
            + rp_elem
            + rp_mass
            + ", found "
            + str(len(rpindex_df))
            + " experimental dataset(s)."
        )

    else:
        selected = "No selection"
        raise PreventUpdate

    container = "{}".format(selected)

    return (
        container,
        userinput,
        default_sel,
        rpindex_df.to_dict("records"),
        rplib_df.to_json(double_precision=12),
        rplibfiles,
        rpindex_df.to_json(double_precision=12),
    )


# ------------------------------------------------------------------------------
# 2. read experimental data
#
#
@app.callback(
    [Output("stored_exfiles_rp", "children"), Output("stored_exps_rp", "children")],
    [
        Input("stored_input_rp", "children"),
        Input("stored_index_rp", "children"),
        Input("index_table_rp", "selected_rows"),
    ],
)
def build_expdf(userinput, stored_index_rp, slctd_rows):
    if userinput:
        nuclide, inc_pt, rp_elem, rp_mass = userinput.split("-")
    else:
        raise PreventUpdate

    try:
        index_dff_rp = pd.read_json(stored_index_rp)
    except:
        raise PreventUpdate

    if not index_dff_rp.empty:
        ee = index_dff_rp["entry"].iloc[slctd_rows]
        ee = ee.astype(str).to_list()
    else:
        ee = []

    exrpfiles, rpex_df = read_resid_prod_exfor(nuclide, inc_pt, rp_elem, rp_mass, ee)

    return exrpfiles, rpex_df.to_json(double_precision=12)


# ------------------------------------------------------------------------------
# Main Figure Update
#
@app.callback(
    [
        Output("main_graph_rp", "figure"),
        Output("exfor_table_rp", "data"),
        Output("file_list_rp", "children"),
    ],
    [
        Input("stored_input_rp", "children"),
        Input("tabs-rp", "active_tab"),
        Input("stored_libs_rp", "children"),
        Input("stored_exps_rp", "children"),
        Input("xaxis_type3", "value"),
        Input("yaxis_type3", "value"),
        Input("stored_libfiles_rp", "children"),
        Input("stored_exfiles_rp", "children"),
    ],
)
def update_figure_rp(
    userinput,
    slctd_tab_rp,
    stored_libs_rp,
    stored_exps_rp,
    xaxis_type,
    yaxis_type,
    libfiles,
    exfiles,
):
    if userinput:
        nuclide, inc_pt, rp_elem, rp_mass = userinput.split("-")
        reaction = "".join([inc_pt, ",x"])
        fig = default_chart(xaxis_type, yaxis_type, reaction, "rp")
    else:
        raise PreventUpdate

    try:
        # Re-constract library dataframe and add trace to fig
        rplib_dff = pd.read_json(stored_libs_rp)

        # Re-constract EXFOR dataframe and add trace to fig
        rpex_dff = pd.read_json(stored_exps_rp)

    except:
        rplib_dff = pd.DataFrame()
        rpex_dff = pd.DataFrame()
        raise PreventUpdate

    if rplib_dff.empty and rpex_dff.empty:
        fig = px.scatter(title="No data found")
        fig.update_layout(title_font_color="orange")

    if not rplib_dff.empty:
        ll = rplib_dff["lib"].unique()
        for l in ll:
            # new_col = next(line_color)
            line_color = color_libs(l)
            new_col = next(line_color)
            fig.add_trace(
                go.Scatter(
                    x=rplib_dff[rplib_dff["lib"] == l]["Energy"],
                    y=rplib_dff[rplib_dff["lib"] == l]["XS"],
                    showlegend=True,
                    line_color=new_col,
                    name=l,
                    mode="lines",
                )
            )

    if not rpex_dff.empty:
        ee = rpex_dff["entry"].unique()
        rpex_dff_dt = rpex_dff.query("entry in @ee")
        rpex_dff_dt = rpex_dff_dt[
            ["author", "year", "entry", "Energy", "dE", "XS", "dXS"]
        ]

        i = 0
        for e in ee:
            label = (
                str(rpex_dff[rpex_dff["entry"] == e]["author"].unique())
                + ","
                + str(rpex_dff[rpex_dff["entry"] == e]["year"].unique())
            )
            label = re.sub("\[|\]|'", "", label)
            fig.add_trace(
                go.Scatter(
                    x=rpex_dff[rpex_dff["entry"] == e]["Energy"],
                    y=rpex_dff[rpex_dff["entry"] == e]["XS"],
                    error_x=dict(
                        type="data", array=rpex_dff[rpex_dff["entry"] == e]["dE"]
                    ),
                    error_y=dict(
                        type="data", array=rpex_dff[rpex_dff["entry"] == e]["dXS"]
                    ),
                    showlegend=True,
                    name=label,
                    marker=dict(size=6, symbol=i),
                    mode="markers",
                )
            )
            i += 1
    else:
        rpex_dff_dt = pd.DataFrame()

    # return content basend on the selected tab
    if slctd_tab_rp == "ds-rp":
        return fig, dash.no_update, dash.no_update

    elif slctd_tab_rp == "datatable-rp":
        return fig, rpex_dff_dt.to_dict("records"), dash.no_update

    elif slctd_tab_rp == "dl-rp":
        csv_string = rpex_dff_dt.to_csv(index=False, encoding="utf-8")
        csv_string = "data:text/csv;charset=utf-8," + quote(csv_string)

        libflinks = list_libfiles(libfiles)
        exflinks = list_exfiles(exfiles, slctd_tab_rp)

        downloadcorrections = html.Div(
            [
                html.Br(),
                html.P(
                    "Download a CSV file with selected experimental dataset used for the visualization chart:"
                ),
                html.A(
                    "CSV file", download="rpdata.csv", href=csv_string, target="_blank"
                ),
                html.Br(),
                html.Br(),
                html.P("Files in EXFORTABLES:"),
                html.Div(
                    [html.Button("Download zip", id="btn_zip3"), Download(id="zip3")]
                ),
                html.Br(),
                html.Div(children=exflinks),
                html.Br(),
                html.Br(),
                html.P("Files in ENDFTABLES:"),
                html.Div(children=libflinks),
            ]
        )

        return fig, dash.no_update, downloadcorrections


@app.callback(
    Output("zip3", "data"),
    [
        Input("btn_zip3", "n_clicks"),
        Input("stored_exfiles_rp", "children"),
        Input("tabs-rp", "active_tab"),
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
