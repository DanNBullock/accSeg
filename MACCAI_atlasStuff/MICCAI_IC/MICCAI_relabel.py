#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar 15 11:23:48 2022

@author: dan
"""

import os
os.chdir('wma_pyTools')
import wmaPyTools.roiTools
import wmaPyTools.segmentationTools
import wmaPyTools.streamlineTools
import wmaPyTools.visTools
os.chdir('..')

import pandas as pd
import nibabel as nib

toMergeLabels=pd.read_csv('MACCAI_atlasStuff/MICCAI_IC/toMergeLAbels')
miccaiAtlas=nib.load()