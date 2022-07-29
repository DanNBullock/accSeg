#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jun 14 10:53:43 2022

@author: dan


"""

import os
import sys

#make sure that wma_pyTools is right in the working directory, or that
#the package can otherwise be imported effectively
sys.path.append('wma_pyTools')
# startDir=os.getcwd()
import pandas as pd
import wmaPyTools.roiTools
import wmaPyTools.analysisTools
import wmaPyTools.segmentationTools
import wmaPyTools.streamlineTools
import wmaPyTools.visTools
import numpy as np
import nibabel as nib
from dipy.tracking.utils import reduce_labels
from dipy.tracking import utils
import itertools
from dipy.tracking.streamline import Streamlines

import os
import json
import numpy as np
import nibabel as nib
import shutil


# load inputs from config.json
with open('config.json') as config_json:
	config = json.load(config_json)


#select the label indexes of interest
#USING THE UNREDUCED (i.e. continuous, renumbered indexing) index!
#NOTE, THESE LABELS ARE SPECIFIC TO aparc.DKTatlas+aseg
# caudalanteriorcingulate    1002    45    77
# rostral anterior cingulate 1026    68    100         
# lateral orbitofrontal      1012    54    86
# pars triangularis          1020    62    94
# superior frontal           1028    70    102
# caudal middle frontal      1003    46    78
# medialorbitofrontal        1014    56    88
# parsorbitalis              1019    61    93
# rostralmiddlefrontal       1027    69   101
# frontalpole                DNE
#reduced
# if side == 'left':
#     newLabels=[45, 46, 54, 62, 68, 70, 56, 61, 69]
# elif side == 'right':
#     newLabels=[77, 100, 86, 94, 102, 78, 88, 93, 101]
#nonReduced
#if the input tractogram only targets a subset of the cortical areas (i.e.
# left/right), only include the indexes for the relevant areas.
# unclear what will happen if null return for found streamlines
targetLabels=[1002,1026,1012,1020,1028,1003,1014,1019,1027,2002,2026,2012,2020,2028,2003,2014,2019,2027]

parcellationPath=os.path.join(config['freesurfer'],'mri','aparc.DKTatlas+aseg.mgz')
refT1Path=config['anat']
tckPath=config['tractogram']
#e.g. https://surfer.nmr.mgh.harvard.edu/fswiki/FsTutorial/AnatomicalROI/FreeSurferColorLUT
lutPath=os.path.join('wma_pyTools','refData','FreesurferLookup.csv')
saveFigDir=os.path.join('testdata','figs')

#load entities
parcellaton=nib.load(parcellationPath)
refT1=nib.load(refT1Path)
tckIn=nib.streamlines.load(tckPath)
lookupTable=pd.read_csv(lutPath)

#perform inflate & deIsland of input parcellation
inflatedAtlas,deIslandReport,inflationReport= wmaPyTools.roiTools.preProcParc(parcellaton,deIslandBool=True,inflateIter=2,retainOrigBorders=False,maintainIslandsLabels=None,erodeLabels=[2,41])    

#orient all the steamlines, potentially not necessary given redundancy with 
#subsequent steps
orientedStreams=wmaPyTools.streamlineTools.orientAllStreamlines(tckIn.streamlines)

#perform inflate & deIsland of input parcellation
inflatedAtlas,deIslandReport,inflationReport= wmaPyTools.roiTools.preProcParc(parcellaton,deIslandBool=True,inflateIter=2,retainOrigBorders=False,maintainIslandsLabels=None,erodeLabels=[2,41])    

# requires up to date version of wma_pyTools (July 15,2022)
classificationDicts=wmaPyTools.streamlineTools.manualSelectStreams_byEndpoint(orientedStreams,inflatedAtlas,lookupTable,targetLabels)

#apply the initial culling, to remove extraneous streamlines 
#first requires doing a DIPY quickbundling
#we cleaned in a previous step with the big script, don't need it here.
#clusters=wmaPyTools.streamlineTools.quickbundlesClusters(orientedStreams, thresholds = [30,20,10,5], nb_pts=100)

#use those clusters to identify the streamlines to be culled
#survivingStreamsIndicies, culledStreamIndicies=wmaPyTools.streamlineTools.cullViaClusters(clusters,orientedStreams,5)
#convert survivingStreamsIndicies into a bool vec
#survivingStreamsBoolVec=np.zeros(len(orientedStreams),dtype=bool)
#survivingStreamsBoolVec[survivingStreamsIndicies]=True

for iSubsections in list(classificationDicts.keys()):
    
    #obtain the current WMC structure
    currWMC=classificationDicts[iSubsections]
    
    #extract information from current WMC
    currSubSectionBoolVec=currWMC['index']
    #there should only be one
    currName=currWMC['names'][0]
    
    #set and, if necessary, create path tout output directory
    currFigDir=os.path.join(saveFigDir,currName)
    if not os.path.exists(currFigDir):
        os.makedirs(currFigDir)
        
    #perform an and/all operation on the survivingStreamsBoolVec and
    #currSubSectionBoolVec
    #we cleaned in a previous step with the big script, don't need it here.
    #currValidStreams=np.all([currSubSectionBoolVec,survivingStreamsBoolVec],axis=0)
    
    #just saving now
    subTckSavePath=os.path.join(saveFigDir,currName+'.tck')
    #for whatever reason, treating the classification as a bolean index DIDN'T
    #work
    streamsSelect=Streamlines(list(itertools.compress(orientedStreams,currSubSectionBoolVec)))
    wmaPyTools.streamlineTools.stubbornSaveTractogram(streamsSelect,savePath=subTckSavePath)
    
    #generate plot-based visualizations
    wmaPyTools.visTools.multiPlotsForTract(streamsSelect,atlas=inflatedAtlas,atlasLookupTable=lookupTable,refAnatT1=refT1,outdir=currFigDir,tractName=currName,makeGifs=False,makeTiles=True,makeFingerprints=True,makeSpagetti=True)
    
    #generate density nifti & save it
    tractDensityNifti=utils.density_map(streamsSelect, refT1.affine, refT1.shape)
    densityNifti = nib.nifti1.Nifti1Image(tractDensityNifti, refT1.affine, refT1.header)
    nib.save(densityNifti,os.path.join(currFigDir,currName+'_density.nii.gz'))
    