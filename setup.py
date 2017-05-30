# -*- coding: utf-8 -*-
"""
Created on Fri Apr 14 13:00:42 2017

@author: MGuidry
"""
import sys
from distutils.core import setup
import py2exe

sys.setrecursionlimit(1500)
data_file_dir=r'C:\Users\MGUIDRY\Documents\GitHub\2017_GA06_special\data_files'
data_files=[('data_files',[data_file_dir+r'\cropped-ddhq-icon.png',
data_file_dir+r'\2016_GA06_pres_margins.csv',    
data_file_dir+r'\2017_GA06_primary_margins.csv',    
data_file_dir+r'\GA06_BW_runoff.png',
data_file_dir+r'\GA06_runoff.csv'])]

setup(
    console=['GA06_make_images_runoff.py'],
    data_files=data_files,
    options={
        "py2exe":{
            "includes":"PIL,PyQt4,sip",
            "dist_dir": r"C:\Users\MGUIDRY\Documents\GitHub\2017_GA06_special\GA06_make_images_runoff",
            "dll_excludes": ["MSVCP90.dll"],
            "unbuffered":True,
            "optimize":2}}
    )