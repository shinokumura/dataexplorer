####################################################################
#
# This file is part of libraries-2021 dataexplorer, https://nds.iaea.org/dataexplorer/.
# Copyright (C) 2022 International Atomic Energy Agency (IAEA)
#
# Contact:    nds.contact-point@iaea.org
#
####################################################################

import plotly.graph_objects as go


def default_axis(mt):
    # reaction = reaction.split(",")
    if mt in [
        "001",
        "002",
        "018",
        "019",
        "102",
        "201",
        "202",
        "203",
        "204",
        "205",
        "206",
        "207",
    ]:  # and not nuclide.endswith("000")
        xaxis_type = "Log"
        yaxis_type = "Log"
    else:
        xaxis_type = "Linear"
        yaxis_type = "Linear"
    return xaxis_type, yaxis_type


def default_chart(xaxis_type, yaxis_type, reaction, mt):
    reaction = reaction.split(",")
    if (
        mt
        in [
            "001",
            "002",
            "018",
            "019",
            "102",
            "201",
            "202",
            "203",
            "204",
            "205",
            "206",
            "207",
            "rp",
        ]
        and reaction[0] == "n"
    ):
        #  and not nuclide.endswith("000")
        fig = go.Figure(
            layout=go.Layout(
                xaxis={
                    "title": "Incident energy [eV]",
                    "type": "log" if xaxis_type == "Log" else "linear",
                    "rangeslider": {
                        "bgcolor": "White",
                        "autorange": True,
                        "thickness": 0.15,
                    },
                },
                yaxis={
                    "title": "Cross section [barn]",
                    "type": "log" if yaxis_type == "Log" else "linear",
                    "fixedrange": False,
                },
                margin={"l": 40, "b": 40, "t": 30, "r": 0},
            )
        )

    elif mt in ["051", "052", "053"] and reaction[0] == "n":
        #  and not nuclide.endswith("000")
        fig = go.Figure(
            layout=go.Layout(
                xaxis={
                    "title": "Incident energy [eV]",
                    "type": "log" if xaxis_type == "Log" else "linear",
                    "range": [50000, 5000000] if xaxis_type == "Linear" else [5.0, 6.5],
                    "rangeslider": {
                        "bgcolor": "White",
                        "autorange": True,
                        "thickness": 0.15,
                    },
                },
                yaxis={
                    "title": "Cross section [barn]",
                    "type": "log" if yaxis_type == "Log" else "linear",
                    "fixedrange": False,
                },
                margin={"l": 40, "b": 40, "t": 30, "r": 0},
            )
        )

    elif mt in ["016", "017", "037"] and reaction[0] == "n":
        #  and not nuclide.endswith("000")
        fig = go.Figure(
            layout=go.Layout(
                xaxis={
                    "title": "Incident energy [eV]",
                    "type": "log" if xaxis_type == "Log" else "linear",
                    "range": [1000000, 50000000]
                    if xaxis_type == "Linear"
                    else [6.1, 7.5],
                    "rangeslider": {
                        "bgcolor": "White",
                        "autorange": True,
                        "thickness": 0.15,
                    },
                },
                yaxis={
                    "title": "Cross section [barn]",
                    "type": "log" if yaxis_type == "Log" else "linear",
                    "fixedrange": False,
                },
                margin={"l": 40, "b": 40, "t": 30, "r": 0},
            )
        )

    else:
        fig = go.Figure(
            layout=go.Layout(
                # template="plotly_white",
                xaxis={
                    "title": "Incident energy [eV]",
                    "type": "linear" if xaxis_type == "Linear" else "log",
                    "range": [1000000, 50000000]
                    if xaxis_type == "Linear"
                    else [6.1, 7.5],
                    "rangeslider": {
                        "bgcolor": "White",
                        "autorange": True,
                        "thickness": 0.15,
                    },
                },
                yaxis={
                    "title": "Cross section [barn]",
                    "type": "linear" if yaxis_type == "Linear" else "log",
                    "fixedrange": False,
                },
                margin={"l": 40, "b": 40, "t": 30, "r": 0},
            )
        )

    # Expornential format
    fig.update_xaxes(exponentformat="power")
    fig.update_yaxes(exponentformat="power")

    return fig
