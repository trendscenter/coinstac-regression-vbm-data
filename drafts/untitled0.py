#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jul 15 23:19:42 2019

@author: hgazula
"""

# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""
#
import os
import pandas as pd
import nibabel as nib
import numpy as np
from memory_profiler import profile

fp = open('memory_log_compare3', 'w+')


@profile(stream=fp)
def do_this():
    df = pd.read_csv('/Users/hgazula/Desktop/sites-within-sites-ipspec/site1_covariate_mega.csv')
    df.rename(columns={'["niftifile"': "niftifile"}, inplace=True)
    df.drop(columns=['Unnamed: 5'], inplace=True)
    df.niftifile = df.niftifile.apply(lambda x: x[2:-1])
    all_files = df.niftifile.tolist()

#    arr = []
#    for idx, file in enumerate(all_files):
#        image_data = np.array(nib.load(file).dataobj)
#        arr.append(image_data)

#    for idx, file in enumerate(all_files):
#        image_data = nib.load(file).get_fdata()
#        np.save(os.path.join('npy_files', os.path.splitext(file)[0] + '_' + str(idx)), image_data)
        
    arr = []
    for idx, file in enumerate(all_files):
        arr.append(np.load(os.path.join('npy_files', os.path.splitext(file)[0] + '_' + str(idx) + '.npy')))
        
#    arr1 = np.concatenate(arr)
    arr2 = np.vstack(arr)
        
do_this()
