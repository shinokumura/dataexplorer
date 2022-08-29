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

from dash import dcc
from dash import html

import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px  # (version 4.7.0)
import plotly.graph_objects as go
from dash.dependencies import Input, Output
from dash.exceptions import PreventUpdate
from dash_extensions import Download

from app import app
from datahandle.checkdata import input_check
from datahandle.exfor_cs import read_exfor
from datahandle.figs import default_axis, default_chart
from datahandle.genlinks import list_libfiles, list_exfiles, genzip
from datahandle.index_cs import read_index
from datahandle.library_cs import read_libs
from datahandle.list import read_mt, color_libs, limit_by_datapoints
from datahandle.tabs import create_tabs
from urlparser import parse_state, apply_default_value

# ------------------------------------------------------------------------------
# lists definitions
#
mt_df = read_mt()
reaction_list = mt_df["Reaction"]
defaultcolor = "text-warning"


# ------------------------------------------------------------------------------
# App layout
# corecompornet : https://dash.plotly.com/dash-html-components/a
# bootstrap : https://dash-bootstrap-components.opensource.faculty.ai/
#


def layout_inputs(params):
    inputs = [
        # dbc.Row([
        dbc.Col(
            [
                html.P(
                    [
                        "Cross Sections from ",
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
                                id="target_elem",
                                # options=[{'label':elem, 'value':elem} for elem in elem_list],
                                placeholder="e.g. C, c, Pd, pd, PD",
                                persistence=True,
                                persistence_type="memory",
                                value="Au",
                                size="30",
                                # style={'width': "100%"}
                            )
                        ),
                        # dbc.Col(html.P('e.g. C, c, Pd, pd, PD')),
                    ]
                ),
                dbc.Row(
                    [
                        dbc.Col(html.Label("Target mass"), width=3),
                        dbc.Col(
                            apply_default_value(params)(dcc.Input)(
                                id="target_mass",
                                placeholder="e.g. 56, 0 (natural), 242m (metastable)",
                                persistence=True,
                                persistence_type="memory",
                                value="197",
                                size="30",
                            )
                        ),
                        # dbc.Col(html.P('e.g. 56, 0 (natural), 242m (metastable)')),
                    ]
                ),
                dbc.Row(
                    [
                        dbc.Col(html.Label("Reaction"), width=3),
                        dbc.Col(
                            apply_default_value(params)(dcc.Dropdown)(
                                id="reaction",
                                options=[
                                    {"label": reac, "value": reac}
                                    for reac in reaction_list
                                ],
                                persistence=True,
                                persistence_type="memory",
                                value="n,g",
                            ),
                            width=4,
                        ),
                    ]
                ),
            ],
            className="h-25",
        )
    ]
    return inputs


tabs_inputs = create_tabs("cs")

layout = (
    dbc.Container(
        [
            html.Br(),
            dcc.Location(id="url_app1", refresh=False),
            # data inputs returs from function
            dbc.Row(id="layout1"),
            html.Br(),
            # Log/Linear switch
            dbc.Row(
                [
                    # data explanation
                    dbc.Col(html.H5(html.Div(id="output_container")), width=12),
                    dbc.Col(
                        dcc.Checklist(
                            id="groupwise",
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
                    dbc.Col(html.Label("X:"), width="auto"),
                    dbc.Col(
                        dcc.RadioItems(
                            id="xaxis_type",
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
                            id="yaxis_type",
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
            # Main Graph Object
            dcc.Graph(
                id="main_graph",
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
            # hidden div tag to store data
            html.Div(id="stored_input", style={"display": "none"}),
            html.Div(id="stored_libs", style={"display": "none"}),
            html.Div(id="stored_exps", style={"display": "none"}),
            html.Div(id="stored_index", style={"display": "none"}),
            html.Div(id="stored_libfiles", style={"display": "none"}),
            html.Div(id="stored_exfiles", style={"display": "none"}),
        ],
        fluid=True,
    ),
)
html.Br()


@app.callback(Output("layout1", "children"), inputs=[Input("url_app1", "href")])
def page_load(href):
    if not href:
        return []
    state = parse_state(href)
    return layout_inputs(state)


component_ids = ["target_elem", "target_mass", "reaction"]


@app.callback(
    Output("url_app1", "search"), inputs=[Input(i, "value") for i in component_ids]
)
def update_url_state(*values):
    state = urlencode(dict(zip(component_ids, values)), doseq=True)
    if all(values):
        return f"?{state}"
    else:
        return ""


# ------------------------------------------------------------------------------
# 1. read experimental index and libraries
#
#
@app.callback(
    [
        Output("output_container", "children"),
        Output("stored_input", "children"),
        Output("xaxis_type", "value"),
        Output("yaxis_type", "value"),
        Output("index_table_cs", "selected_rows"),
        Output("index_table_cs", "data"),
        Output("stored_libs", "children"),
        Output("stored_libfiles", "children"),
        Output("stored_index", "children"),
    ],
    [
        Input("target_elem", "value"),
        Input("target_mass", "value"),
        Input("reaction", "value"),
        Input("groupwise", "value"),
    ],
)
def load_index(target_elem, target_mass, reaction, groupwise):
    if reaction:
        # input reaction to MT and exfor SF3
        mt_dff = mt_df.copy()
        mt_dff = mt_dff[mt_dff["Reaction"] == reaction]
        mt = mt_dff.iat[0, 0]
        # exforsf3 = mt_dff.iat[0,2]

    if target_elem and target_mass and reaction:
        # input check
        elem, mass = input_check(target_elem, target_mass)
        nuclide = "".join([elem, mass])
        userinput = "".join([nuclide, "-", reaction, "-", mt])
        # print("app1:", elem, mass, reaction, mt)

        # set default axis
        xaxis_type, yaxis_type = default_axis(mt)

        # read libraries
        libfiles, lib_df = read_libs(nuclide, reaction, mt, groupwise)

        # read .list file and load index dataframe
        index_df = read_index(nuclide, reaction, mt)

        if not index_df.empty:
            default_sel = limit_by_datapoints(index_df)

        else:
            default_sel = list(range(10))

        # to display selection
        selected = "".join(
            [
                nuclide,
                "(",
                reaction,
                "), found ",
                str(len(index_df)),
                " experimental dataset(s).",
            ]
        )

    else:
        selected = "No selection"
        raise PreventUpdate

    container = "{}".format(selected)

    return (
        container,
        userinput,
        xaxis_type,
        yaxis_type,
        default_sel,
        index_df.to_dict("records"),
        lib_df.to_json(),
        libfiles,
        index_df.to_json(),
    )


# ------------------------------------------------------------------------------
# 2. Read Experimental data
#
#
@app.callback(
    [Output("stored_exfiles", "children"), Output("stored_exps", "children")],
    [
        Input("stored_input", "children"),
        Input("stored_index", "children"),
        Input("index_table_cs", "selected_rows"),
    ],
)
def build_expdf(userinput, stored_index, slctd_rows):
    if userinput:
        nuclide, reaction, mt = userinput.split("-")
    else:
        raise PreventUpdate

    try:
        index_dff = pd.read_json(stored_index)
    except:
        raise PreventUpdate

    if not index_dff.empty:
        ee = index_dff["entry"].iloc[slctd_rows]
        ee = ee.astype(str).to_list()
    else:
        ee = []

    exfiles, exfor_df = read_exfor(nuclide, reaction, mt, ee)

    return exfiles, exfor_df.to_json(double_precision=12)


# ------------------------------------------------------------------------------
# 2. Update figure
#
#
@app.callback(
    [
        Output("main_graph", "figure"),
        Output("exfor_table_cs", "data"),
        Output("file_list_cs", "children"),
    ],
    [
        Input("stored_input", "children"),
        Input("tabs-cs", "active_tab"),
        Input("stored_libs", "children"),
        Input("stored_exps", "children"),
        Input("xaxis_type", "value"),
        Input("yaxis_type", "value"),
        Input("stored_libfiles", "children"),
        Input("stored_exfiles", "children"),
    ],
)
def update_figure(
    userinput,
    slctd_tab,
    stored_libs,
    stored_exps,
    xaxis_type,
    yaxis_type,
    libfiles,
    exfiles,
):
    if userinput:
        nuclide, reaction, mt = userinput.split("-")

        # Fig definition
        fig = default_chart(xaxis_type, yaxis_type, reaction, mt)
    else:
        raise PreventUpdate

    try:
        # Re-constract library dataframe and add trace to fig
        lib_dff = pd.read_json(stored_libs)

        # Re-constract EXFOR dataframe and add trace to fig
        exfor_dff = pd.read_json(stored_exps)

    except:
        exfor_dff = pd.DataFrame()
        lib_dff = pd.DataFrame()
        raise PreventUpdate

    if lib_dff.empty and exfor_dff.empty:
        fig = px.scatter(title="No data found")
        fig.update_layout(title_font_color="orange")

    if not lib_dff.empty:
        ll = lib_dff["lib"].unique()
        for l in ll:
            line_color = color_libs(l)
            new_col = next(line_color)
            # new_col = color_libs(l)
            fig.add_trace(
                go.Scatter(
                    x=lib_dff[lib_dff["lib"] == l]["Energy"],
                    y=lib_dff[lib_dff["lib"] == l]["XS"],
                    showlegend=True,
                    line_color=new_col,
                    name=l,
                    mode="lines",
                )
            )

    if not exfor_dff.empty:
        ee = exfor_dff["entry"].unique()
        exfor_dff_dt = exfor_dff.query("entry in @ee")
        exfor_dff_dt = exfor_dff_dt[
            ["author", "year", "entry", "Energy", "dE", "XS", "dXS"]
        ]
        # exfor_table = exfor_dff_dt.to_dict('records')      # for download

        i = 0
        for e in ee:
            label = (
                str(exfor_dff[exfor_dff["entry"] == e]["author"].unique())
                + ","
                + str(exfor_dff[exfor_dff["entry"] == e]["year"].unique())
            )
            label = re.sub("\[|\]|'", "", label)
            fig.add_trace(
                go.Scatter(
                    x=exfor_dff[exfor_dff["entry"] == e]["Energy"],
                    y=exfor_dff[exfor_dff["entry"] == e]["XS"],
                    error_x=dict(
                        type="data", array=exfor_dff[exfor_dff["entry"] == e]["dE"]
                    ),
                    error_y=dict(
                        type="data", array=exfor_dff[exfor_dff["entry"] == e]["dXS"]
                    ),
                    showlegend=True,
                    name=label,
                    marker=dict(size=8, symbol=i),
                    mode="markers",
                )
            )
            i += 1
    else:
        exfor_dff_dt = pd.DataFrame()
        # exfor_table = []

    # return content basend on the selected tab
    if slctd_tab == "ds-cs":
        return fig, dash.no_update, dash.no_update

    if slctd_tab == "datatable-cs":
        return fig, exfor_dff_dt.to_dict("records"), dash.no_update

    elif slctd_tab == "dl-cs":
        csv_string = exfor_dff_dt.to_csv(index=False, encoding="utf-8")
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
                    [html.Button("Download zip", id="btn_zip1"), Download(id="zip1")]
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
    Output("zip1", "data"),
    [
        Input("btn_zip1", "n_clicks"),
        Input("stored_exfiles", "children"),
        Input("tabs-cs", "active_tab"),
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
