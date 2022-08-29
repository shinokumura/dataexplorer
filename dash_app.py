# import dash
# import dash_bootstrap_components as dbc
# # import gcsfs
# # import config

# dash_app = dash.Dash(
#     __name__,
#     external_stylesheets=[dbc.themes.FLATLY],
#     url_base_pathname="/nucleardataexplorer/",
#     suppress_callback_exceptions=True,
#     meta_tags=[
#         {
#             "name": "Nuclear Data Section - IAEA",
#             "content": "Nuclear Reaction data plot, LIBRARIES-2020, TALYS",
#         },
#         {"http-equiv": "X-UA-Compatible", "content": "IE=edge"},
#         {"name": "viewport", "content": "width=device-width, initial-scale=1.0"},
#     ],
# )

# dash_app.title = "LIBRARIES-2021 Data Explorer"

# # FS = None
# # if config.CLOUD:
# #     FS = gcsfs.GCSFileSystem()
