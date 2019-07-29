#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jun 14 16:39:44 2019

@author: hgazula
"""
import nibabel as nib
import os
import sys
from types import ModuleType, FunctionType
from gc import get_referents
import numpy as np
# Custom objects know their class.
# Function objects seem to know way too much, including modules.
# Exclude modules as well.
BLACKLIST = type, ModuleType, FunctionType
from memory_profiler import memory_usage, profile
from time import sleep


def getsize(obj):
    """sum size of object & members."""
    if isinstance(obj, BLACKLIST):
        raise TypeError('getsize() does not take argument of type: '+ str(type(obj)))
    seen_ids = set()
    size = 0
    objects = [obj]
    while objects:
        need_referents = []
        for obj in objects:
            if not isinstance(obj, BLACKLIST) and id(obj) not in seen_ids:
                seen_ids.add(id(obj))
                size += sys.getsizeof(obj)
                need_referents.append(obj)
        objects = get_referents(*need_referents)
    return size


def get_size(obj, seen=None):
    """Recursively finds size of objects"""
    size = sys.getsizeof(obj)
    if seen is None:
        seen = set()
    obj_id = id(obj)
    if obj_id in seen:
        return 0
    # Important mark as seen *before* entering recursion to gracefully handle
    # self-referential objects
    seen.add(obj_id)
    if isinstance(obj, dict):
        size += sum([get_size(v, seen) for v in obj.values()])
        size += sum([get_size(k, seen) for k in obj.keys()])
    elif hasattr(obj, '__dict__'):
        size += get_size(obj.__dict__, seen)
    elif hasattr(obj, '__iter__') and not isinstance(obj, (str, bytes, bytearray)):
        size += sum([get_size(i, seen) for i in obj])
    return size

@profile
def f():
#    MASK = '/computation/mask_2mm.nii'
    MASK = '/Users/hgazula/Documents/coinstac-regression-vbm/mask_2mm.nii'
    mask_data = nib.load(MASK).get_data()
    
    list_files = '/Users/hgazula/Documents/coinstac-regression-vbm/test_file'
    with open(list_files, 'r') as f:
        files = [line.rstrip('\n') for line in f]
    
    appended_data = []
    print('starting loading files')
    for file in files:
        file_path = os.path.join('/Users/hgazula/Documents/coinstac-regression-vbm/test/local2/simulatorRun', file)
        try:
            image_data = nib.load(file_path).get_data()
            if np.all(np.isnan(image_data)) or np.count_nonzero(image_data) == 0 or image_data.size == 0:
                    continue
            appended_data.append(image_data[mask_data > 0])
        except:
            continue
    print('ending loading files')
    
    print(len(appended_data))
    return appended_data

mem_usage = memory_usage(f)
print('Memory usage (in chunks of .1 seconds): %s' % mem_usage)
print('Maximum memory usage: %s' % max(mem_usage))