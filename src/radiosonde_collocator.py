#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct 19 16:04:26 2021

@author: aouyed
"""

import glob
from datetime import datetime
import pandas as pd
import xarray as xr
import cross_section as cs
from datetime import timedelta
import numpy as np


class radiosonde_collocator:

    def __init__(self, parameters):
        igra_collocator(parameter)
