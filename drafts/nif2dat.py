#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jun 27 17:32:07 2019

@author: hgazula
"""
import json
import os
import sys
import pandas as pd
import numpy as np
import nibabel as nib
#from memory_profiler import profile
from nipype.interfaces import afni
import tempfile

MASK = os.path.join('/Users/hgazula/Documents/coinstac-regression-vbm', 'mask_2mm.nii')
VOXEL_SIZE = (4.0, 4.0, 4.0)

def resample_nifti_images(image_file, resampled_file, voxel_dimensions, resample_method):
    """Resample the NIfTI images in a folder and put them in a new folder
    Args:
        images_location: Path where the images are stored
        voxel_dimension: tuple (dx, dy, dz)
        resample_method: NN - Nearest neighbor
                         Li - Linear interpolation
    Returns:
        None:
    """
    resample = afni.Resample()
    resample.inputs.environ = {'AFNI_NIFTI_TYPE_WARN': 'NO'}
    resample.inputs.in_file = image_file
    resample.inputs.out_file = resampled_file
    resample.inputs.voxel_size = voxel_dimensions
    resample.inputs.outputtype = 'NIFTI'
    resample.inputs.resample_mode = resample_method
    resample.run()


#@profile
def nifti_to_data(args, X):
    """Read nifti files as matrices"""
    print('entered nifti_to_data')
    try:
        mask_data = nib.load(MASK).get_data()
    except FileNotFoundError:
        raise Exception("Missing Mask at ")

    appended_data = []

    # Extract Data (after applying mask)
    for image in X.index:
        input_file = os.path.join('/Users/hgazula/Documents/coinstac-regression-vbm/test/local2/simulatorRun',
                             image)
        output_file = tempfile.NamedTemporaryFile()
        print(tempfile.tempdir)
        print(output_file.name)
        os.makedirs(os.path.dirname(os.path.join(tempfile.tempdir, output_file.name)), exist_ok=True)
        
        try:
            resample_nifti_images(input_file, output_file.name, VOXEL_SIZE,
                                      'Li')
            image_data = nib.load(output_file).get_data()

            if np.all(np.isnan(image_data)) or np.count_nonzero(
                    image_data) == 0 or image_data.size == 0:
                X.drop(index=image, inplace=True)
                continue
            else:
                appended_data.append(image_data[mask_data > 0])
                tempfile.close()
        except FileNotFoundError:
            X.drop(index=image, inplace=True)
            continue

    y = pd.DataFrame.from_records(appended_data)
    
#    if y.empty:
#        raise Exception(
#                'Could not find .nii files specified in the covariates csv')

    return X, y

#@profile
def vbm_parser(args):
    """Parse the nifti (.nii) specific inputspec.json and return the
    covariate matrix (X) as well the dependent matrix (y) as dataframes"""
    print('entered vbm_parser')
    input_list = args["input"]
    X_info = input_list["covariates"]

    X_data = X_info[0][0][:10]
    X_labels = X_info[1]
    
    X_df = pd.DataFrame.from_records(X_data)
    X_df.columns = X_df.iloc[0]
    X_df = X_df.reindex(X_df.index.drop(0))
    X_df.set_index(X_df.columns[0], inplace=True)

    X = X_df[X_labels]
    X = X.apply(pd.to_numeric, errors='ignore')
    X = pd.get_dummies(X, drop_first=True)
    X = X * 1

    X.dropna(axis=0, how='any', inplace=True)

    X, y = nifti_to_data(args, X)

    y.columns = ['{}_{}'.format('voxel', str(i)) for i in y.columns]

    return (X, y)


#@profile
def main():
    print('entered main')
    parsed_args = json.loads(sys.stdin.read())
    parsed_args["input"] = parsed_args
    (X, y) = vbm_parser(parsed_args)


main()    
#mem_usage = memory_usage(vbm_parser(parsed_args))
#print('Memory usage (in chunks of .1 seconds): %s' % mem_usage)
#print('Maximum memory usage: %s' % max(mem_usage))
