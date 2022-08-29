# import os
# import glob
# from config import CLOUD
# from dash_app import FS
#
#
# def path_exists(path):
#     """Checks if a path exists locally or on cloud"""
#     if CLOUD:
#         return FS.exists(path)  # TODO
#
#     return os.path.exists(path)
#
#
# def file_open(filename):
#     if CLOUD:
#         return FS.open(filename)
#
#     return open(filename)
#
#
# def file_glob(file_pattern):
#     if CLOUD:
#         return ["gs://{0}".format(fn) for fn in FS.glob(file_pattern)]
#
#     return glob.glob(file_pattern)
#
#
# def dir_list(dirname):
#     if CLOUD:
#         return ["gs://{0}".format(fn) for fn in FS.ls(dirname)]
#
#     return os.listdir(dirname)
