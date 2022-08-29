
####################################################################
#
# This file is part of libraries-2021 dataexplorer, https://nds.iaea.org/dataexplorer/.
# Copyright (C) 2022 International Atomic Energy Agency (IAEA)
#
# Contact:    nds.contact-point@iaea.org
#
####################################################################

import dash_bootstrap_components as dbc
from dash import html
from dash import dash_table
from dash.dash_table.Format import Format, Scheme


def create_tabs(pageparam):
    tabs = dbc.Tabs(
        id="".join(["tabs-", pageparam]),
        active_tab="".join(["ds-", pageparam]),
        children=[
            # first tab
            dbc.Tab(
                label="Dataset List",
                tab_id="".join(["ds-", pageparam]),
                children=[
                    html.Br(),
                    html.P(
                        "Add more data to the chart by selecting dataset from the following table. Use filter function, e.g. >2000 in Year field. "
                    ),
                    # Index Table
                    dash_table.DataTable(
                        id="".join(["index_table_", pageparam]),
                        columns=[
                            {"name": "Author", "id": "author"},
                            {"name": "Year", "id": "year"},
                            {"name": "#Entry", "id": "entry"},
                            {"name": "Points", "id": "points"},
                            {
                                "name": "E_min[eV]",
                                "id": "emin",
                                "type": "numeric",
                                "format": Format(precision=3, scheme=Scheme.exponent),
                            },
                            {
                                "name": "E_max[eV]",
                                "id": "emax",
                                "type": "numeric",
                                "format": Format(precision=3, scheme=Scheme.exponent),
                            },
                        ],
                        filter_action="native",
                        sort_action="native",
                        sort_mode="single",
                        row_selectable="multi",
                        page_action="none",
                        style_table={"height": "400px", "overflowY": "auto"}
                        # fill_width=False
                    ),
                ],  # end of first tab children
            ),  # end of first tab
            # start second tab
            dbc.Tab(
                label="Raw Data",
                tab_id="".join(["datatable-", pageparam]),
                children=[
                    html.Br(),
                    html.P("Selected experimental data in the chart."),
                    html.P("Use filter function e.g. '>0.1' in Energy. "),
                    dash_table.DataTable(
                        id="".join(["exfor_table_", pageparam]),
                        columns=[
                            {"name": "Author", "id": "author"},
                            {"name": "Year", "id": "year"},
                            {"name": "#Entry", "id": "entry"},
                            {
                                "name": "Energy[eV]",
                                "id": "Energy",
                                "type": "numeric",
                                "format": Format(precision=4, scheme=Scheme.exponent),
                            },
                            {
                                "name": "dEnergy[eV]",
                                "id": "dE",
                                "type": "numeric",
                                "format": Format(precision=4, scheme=Scheme.exponent),
                            },
                            {
                                "name": "XS[b]",
                                "id": "XS",
                                "type": "numeric",
                                "format": Format(precision=4, scheme=Scheme.exponent),
                            },
                            {
                                "name": "dXS[b]",
                                "id": "dXS",
                                "type": "numeric",
                                "format": Format(precision=2, scheme=Scheme.exponent),
                            },
                        ],
                        filter_action="native",
                        sort_action="native",
                        sort_mode="single",
                        # page_action='native',
                        # page_current=0,
                        # page_size = 25
                        page_action="none",
                        style_table={"height": "400px", "overflowY": "auto"},
                    ),
                ],  # end of second tab children
            ),  # end of second tab
            dbc.Tab(
                label="Download Data Files",
                tab_id="".join(["dl-", pageparam]),
                children=[
                    html.Div(
                        id="".join(["file_list_", pageparam]),
                    )
                ],
            ),
        ],
    )
    # ])
    return tabs


def create_tabs_fy(pageparam):
    tabs = dbc.Tabs(
        id="".join(["tabs-", pageparam]),
        active_tab="".join(["ds-", pageparam]),
        children=[
            # first tab
            dbc.Tab(
                label="Dataset List",
                tab_id="".join(["ds-", pageparam]),
                children=[
                    html.Br(),
                    html.P(
                        "Add more data to the chart by selecting dataset from the following table."
                    ),
                    # Index Table
                    dash_table.DataTable(
                        id="".join(["index_table_", pageparam]),
                        columns=[
                            {"name": "Author", "id": "author"},
                            {"name": "Year", "id": "year"},
                            {"name": "#Entry", "id": "entry"},
                            {"name": "Points", "id": "points"},
                            {
                                "name": "E_inc[eV]",
                                "id": "einc",
                                "type": "numeric",
                                "format": Format(precision=4, scheme=Scheme.exponent),
                            },
                        ],
                        editable=False,
                        filter_action="native",
                        sort_action="native",
                        sort_mode="single",
                        column_selectable="single",
                        row_selectable="multi",
                        page_action="none",
                        style_table={"height": "300px", "overflowY": "auto"},
                    ),
                ],  # end of first tab children
            ),  # end of first tab
            # start second tab
            dbc.Tab(
                label="Raw Data",
                tab_id="".join(["datatable-", pageparam]),
                children=[
                    html.Br(),
                    html.P("Selected experimental data in the chart."),
                    html.P("Use filter function e.g. '>0.1' in E_inc. "),
                    dash_table.DataTable(
                        id="".join(["exfor_table_", pageparam]),
                        columns=[
                            {"name": "Author", "id": "author"},
                            {"name": "Year", "id": "year"},
                            {"name": "#Entry", "id": "entry"},
                            {
                                "name": "E_inc[eV]",
                                "id": "Einc",
                                "type": "numeric",
                                "format": Format(precision=4, scheme=Scheme.exponent),
                            },
                            {"name": "A", "id": "A", "type": "numeric"},
                            {"name": "Z", "id": "Z", "type": "numeric"},
                            {"name": "Iso", "id": "Iso", "type": "numeric"},
                            {
                                "name": "Yield",
                                "id": "FPY",
                                "type": "numeric",
                                "format": Format(precision=4, scheme=Scheme.exponent),
                            },
                            {
                                "name": "dYield",
                                "id": "dFPY",
                                "type": "numeric",
                                "format": Format(precision=2, scheme=Scheme.exponent),
                            },
                        ],
                        filter_action="native",
                        sort_action="native",
                        sort_mode="single",
                        # page_action='native',
                        # page_current=0,
                        # page_size = 25
                        page_action="none",
                        style_table={"height": "300px", "overflowY": "auto"},
                    ),
                ],  # end of second tab children
            ),  # end of second tab
            dbc.Tab(
                label="Download Data Files",
                tab_id="".join(["dl-", pageparam]),
                children=[
                    html.Div(
                        id="".join(["file_list_", pageparam]),
                    )
                ],
            ),
        ],
    )
    # ])
    return tabs
