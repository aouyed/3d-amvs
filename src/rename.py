#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May 27 17:04:16 2022

@author: aouyed
"""
import shutil
import os
import glob
from tqdm import tqdm

files = glob.glob("../data/processed/tvl1_coarse_january_5_t10_01*")
for file in tqdm(files):
    dirstring = os.path.dirname(os.path.realpath(file))
    base = os.path.basename(file)
    new_file = os.path.join(dirstring, base[:26] + "tdelta_6_Lambda_0_" + base[26:])
    old_file = os.path.join(dirstring, base)
    # os.rename(old_file, new_file)
    shutil.copyfile(old_file, new_file)
