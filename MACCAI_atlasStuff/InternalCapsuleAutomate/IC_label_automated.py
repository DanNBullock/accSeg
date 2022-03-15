#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar 15 12:09:58 2022

@author: dan
"""

import os
os.chdir('wma_pyTools')
import wmaPyTools.roiTools
import wmaPyTools.segmentationTools
import wmaPyTools.streamlineTools
import wmaPyTools.visTools
os.chdir('..')

import nibabel as nib

sideList=['left','right']
for iIndex,iSide in enumerate(sideList):
    if iSide=='left':
        sideLabel=1000
        #extract spine ROI
    elif iSide=='right':
        sideLabel=2000
        #extract spine ROI
        
        #get the caudate. This will serve as the 
        caudateLabels=[11,50]
        caudateROI=wmaPyTools.roiTools.multiROIrequestToMask(inputAtlas,caudateLabels[iIndex])
        #get the putamen and globus palladus
        palPutLabels=[[12,13],[51,52]]
        palPutROI=wmaPyTools.roiTools.multiROIrequestToMask(inputAtlas,palPutLabels[iIndex])
        #get the white matter labels as well
        wmLabels=[2,41]
        wmROI=wmaPyTools.roiTools.multiROIrequestToMask(inputAtlas,wmLabels[iIndex])
        #intersect the inflated palPutROI with the inflated 
        roiInflateIntersection=wmaPyTools.roiTools.findROISintersection([caudateROI,palPutROI],inflateiter=7)
        #find the intersection of this with the white matter
        putativeRoughIC=wmaPyTools.roiTools.findROISintersection([roiInflateIntersection,wmROI],inflateiter=0)
        #apply anterior and posterior constraints
        #was the anterior the putamen or the caudate
        anteriorPutBorder=planarROIFromAtlasLabelBorder(inputAtlas,palPutLabels[iIndex], 'anterior')
        #anterior of the brainstem border
        anteriorBrainstemBorder=planarROIFromAtlasLabelBorder(inputAtlas,16, 'anterior')
        #cut the roi to return the constrained version of the IC
        #using the anterior border
        anteriorCutIC=sliceROIwithPlane(putativeRoughIC,anteriorPutBorder,'posterior')
        #using the posterior border
        fullCutIC=sliceROIwithPlane(anteriorCutIC,anteriorBrainstemBorder,'anterior')
        #done?