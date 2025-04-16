#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov  9 11:00:46 2021

@author: aouyed
"""

import glob
import os

files = glob.glob("*.pkl")

for file in files:
    os.rename(file, "july_" + file)
