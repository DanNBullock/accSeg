#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Dec  2 14:57:13 2021

@author: dan
"""

import nibabel as nib
import os
#some how set a path to wma pyTools repo directory
wmaToolsDir='/media/dan/storage/gitDir/wma_pyTools'
import os
os.chdir(wmaToolsDir)
import wmaPyTools.roiTools
import wmaPyTools.segmentationTools
import wmaPyTools.streamlineTools
import wmaPyTools.visTools
import numpy as np
import dipy.io.streamline

#quick Sarah caudal_anterior_cingulate process
#ignore these if you aren't using the path creation function
#(it's a local, project level helper function I use to automatically generate paths to specific files in a project)
projectDictionary=makeMetaDictionary()
testSubjectPaths=projectDictionary['100206']
#set this to the outdir you'd like for products of this processing
outDir=testSubjectPaths['outDir']
#set to freesurfer output path for this subject
fsPath=testSubjectPaths['freesurfer_2']
#you may need to convert the .mgz files to .nii.gz using the mr_convert command
#also, you may need to rename the subsequent aparcDk atlas file to it's standard name:
# aparc+aseg
dkAtlas=nib.load(os.path.join(fsPath,'mri/aparc.DKTatlas+aseg.nii.gz'))

#set this to the path of the t1 for 
refT1Path=testSubjectPaths['t1_2']
refAnatT1=nib.load(refT1Path)

# #performSegmentation
#extract whole brain segmentation
#set to path to target whole brain tractogram
tractogramPath=testSubjectPaths['tractogram_2']
tractogramLoad=nib.streamlines.load(tractogramPath)
streamlines=wmaPyTools.streamlineTools.orientAllStreamlines(tractogramLoad.streamlines)

#dipyPlot
sideList=['left','right']
#for iInflations in range(10):
    #if you don't want to iterate across all of these inflation ranges, you can
    #either narrow the range of iterations, or just set iInflations to a specific integer (inflation) value
for iInflations in range(10):
    for iSide in sideList:
        if iSide=='left':
            sideLabel=1000
            targetSpineLocations =wmaPyTools.roiTools.multiROIrequestToMask(dkAtlas,[28, 16, 10])
        elif iSide=='right':
            sideLabel=2000
            targetSpineLocations =wmaPyTools.roiTools.multiROIrequestToMask(dkAtlas,[ 16, 60, 49])
        #create a name stem
        tractName=iSide+'_ACC_targeted_streams_' + str(iInflations)
        #extract spine ROI
       
        #targetSpineLocationsBoolOut=WMA_pyFuncs.applyNiftiCriteriaToTract_DIPY_Test(streamlines, targetSpineLocations, True, 'either_end')
        
        #generate ACC ROI
        inflatedACC=wmaPyTools.roiTools.multiROIrequestToMask(dkAtlas,sideLabel+2,iInflations+1)
        #accIntersectBoolOut=WMA_pyFuncs.applyNiftiCriteriaToTract_DIPY_Test(streamlines, inflatedACC, True, 'any')
        
        #generate superior frontal gyrus exclusion roi, no desire to inflate
        sfgROI=wmaPyTools.roiTools.multiROIrequestToMask(dkAtlas,sideLabel+28)
        #use it as an exclusion criterion
        #sfgExcludeBoolOut=WMA_pyFuncs.applyNiftiCriteriaToTract_DIPY_Test(streamlines, sfgROI, False, 'either_end')
        
        #generate roi for WM
        if sideLabel== 1000:
            contraWMROI=wmaPyTools.roiTools.multiROIrequestToMask(dkAtlas,41)
        elif sideLabel== 2000:
            contraWMROI=wmaPyTools.roiTools.multiROIrequestToMask(dkAtlas,2)
        #use it as an exclusion criterion
        #contraWMExcludeBoolOut=WMA_pyFuncs.applyNiftiCriteriaToTract_DIPY_Test(streamlines, contraWMROI, False, 'any')
        
        #generate roi for paracentral gyrus
        paraCGROI=wmaPyTools.roiTools.multiROIrequestToMask(dkAtlas,sideLabel+17)
        #find the anterior border of it
        paraCGAntBorderROI=wmaPyTools.roiTools.planeAtMaskBorder(paraCGROI,'anterior')
        #now lets clip this at the top of the CC
        #get the superior CC planar border, 253 is central
        ccROI=wmaPyTools.roiTools.multiROIrequestToMask(dkAtlas,253)
        supCCBorder=wmaPyTools.roiTools.planeAtMaskBorder(ccROI,'superior')
        #now cut the paraCentralPlanar ROI with it
        supCCparaCantBorder=wmaPyTools.roiTools.sliceROIwithPlane(paraCGAntBorderROI,supCCBorder,'superior')
        #cingulum exclusion plane created
        
        #generate roi anterior border of rostralanteriorcingulate
        antCingROI=wmaPyTools.roiTools.multiROIrequestToMask(dkAtlas,sideLabel+26,2)
        #find the anterior border of it
        antCingBorderROI=wmaPyTools.roiTools.planeAtMaskBorder(antCingROI,'anterior')
        #no further modification needed; anterior tranversal exclusion plane created
        
        #generate roi for posterior CC
        posteriorCC=wmaPyTools.roiTools.multiROIrequestToMask(dkAtlas,251)
        #find the anterior border of it
        posteriorCCborder=wmaPyTools.roiTools.planeAtMaskBorder(posteriorCC,'posterior')
        #now lets clip this at the top of the bottom of the posterior CC ROI
        inferiorPosteriorCCborder=wmaPyTools.roiTools.planeAtMaskBorder(posteriorCC,'posterior')
        infPostCCBorder=wmaPyTools.roiTools.planeAtMaskBorder(posteriorCC,'inferior')
        #now cut the posteriorCC ROI with it
        supPostCCBorder=wmaPyTools.roiTools.sliceROIwithPlane(posteriorCCborder,infPostCCBorder,'superior')
        #posterior traversal exclusion ROI created
        
        #additional exclusion criteria lateral to thalamus and posterior to putamen, just for fun
        #obtain posterior border of putamen
        if sideLabel== 1000:
            putROI=wmaPyTools.roiTools.multiROIrequestToMask(dkAtlas,12)
        elif sideLabel== 2000:
            putROI=wmaPyTools.roiTools.multiROIrequestToMask(dkAtlas,51)
        #find it's posterior border
        posteriorPalBorder=wmaPyTools.roiTools.planeAtMaskBorder(putROI,'posterior')
        
        #obtain thalamus ROI
        #THIS IS TOO MUCH, COMMENT OUT FOR NOW
        if sideLabel== 1000:
            thalROI=wmaPyTools.roiTools.multiROIrequestToMask(dkAtlas,10)
        elif sideLabel== 2000:
            thalROI=wmaPyTools.roiTools.multiROIrequestToMask(dkAtlas,49)
        #get it's lateral border
        lateralThalBorder=wmaPyTools.roiTools.planeAtMaskBorder(thalROI,'lateral')
        #clip the posteriorPalBorder with the lateralThalBorder, retain lateral portion
        latPostPalBorder=wmaPyTools.roiTools.sliceROIwithPlane(posteriorPalBorder,lateralThalBorder,'lateral')
        #posterio-lateral exclusion criteria created
        
        #it's actually faster to do it with this multi version than individually
        #this is why all of the individual segmentation steps are grayed out above
        comboROIBool=wmaPyTools.segmentationTools.segmentTractMultiROI(streamlines, [inflatedACC,targetSpineLocations,contraWMROI,sfgROI,supCCparaCantBorder,supPostCCBorder,antCingBorderROI,latPostPalBorder], [True,True,False,False,False,False,False,False], ['any','either_end','any','either_end','any','any','any','any'])
        print('multi seg complete')
        #saves the output tractogram
        wmaPyTools.streamlineTools.stubbornSaveTractogram(streamlines[comboROIBool],os.path.join(outDir,tractName+'.trk'))
        #dipy plot of the anatomy
        wmaPyTools.visTools.dipyPlotTract(streamlines[comboROIBool],refAnatT1=None, tractName=os.path.join(outDir,tractName))
        #tile density plot
        wmaPyTools.visTools.multiTileDensity(streamlines[comboROIBool],refAnatT1,outDir,tractName=tractName,noEmpties=True)
        #gif visualizations
        wmaPyTools.visTools.densityGifsOfTract(streamlines[comboROIBool],refAnatT1,saveDir=outDir,tractName=tractName)
        #save as vtk output.
        dipy.io.streamline.save_vtk_streamlines(streamlines[comboROIBool], os.path.join(outDir,tractName+'.vtk'), to_lps=True, binary=False)

