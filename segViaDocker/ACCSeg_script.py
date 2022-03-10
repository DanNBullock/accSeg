#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Dec  2 14:57:13 2021

@author: dan
"""

import nibabel as nib
import os
startDir=os.getcwd()
#some how set a path to wma pyTools repo directory
wmaToolsDir='../wma_pyTools'
import os
os.chdir(wmaToolsDir)
import wmaPyTools.roiTools
import wmaPyTools.segmentationTools
import wmaPyTools.streamlineTools
import wmaPyTools.visTools
import numpy as np
import dipy.io.streamline
os.chdir(startDir)

import subprocess
import os
import json

# load inputs from config.json
with open('config.json') as config_json:
	config = json.load(config_json)


#quick Sarah caudal_anterior_cingulate process
#ignore these if you aren't using the path creation function
#(it's a local, project level helper function I use to automatically generate paths to specific files in a project)
#set this to the outdir you'd like for products of this processing
outDir='../testdata/output/seg/'
if not os.path.exists(outDir):
    os.makedirs(outDir)
#set to freesurfer output path for this subject
fsPath=config['fsPath']
#you may need to convert the .mgz files to .nii.gz using the mr_convert command
#also, you may need to rename the subsequent aparcDk atlas file to it's standard name:
# aparc+aseg
dkAtlas=nib.load(os.path.join(fsPath,'mri/aparc.DKTatlas+aseg.nii.gz'))

#set this to the path of the t1 for 
refT1Path=config['T1']
refAnatT1=nib.load(refT1Path)

# #performSegmentation
#extract whole brain segmentation
#set to path to target whole brain tractogram
#smaller = faster
tractogramPath=config['tractogram']
tractogramLoad=nib.streamlines.load(tractogramPath)
streamlines=wmaPyTools.streamlineTools.orientAllStreamlines(tractogramLoad.streamlines)
#save an indicator of valid streamline endpoints to segment
import dipy.tracking.utils as ut
endpointStreams=wmaPyTools.streamlineTools.downsampleToEndpoints(streamlines)
tractDensityNifti=ut.density_map(endpointStreams, refAnatT1.affine, refAnatT1.shape)
densityNifti = nib.nifti1.Nifti1Image(tractDensityNifti, refAnatT1.affine, refAnatT1.header)
nib.save(densityNifti,outDir+'tractogram_endpointDensity.nii.gz')


#dipyPlot
sideList=['left','right']
#for iInflations in range(10):
    #if you don't want to iterate across all of these inflation ranges, you can
    #either narrow the range of iterations, or just set iInflations to a specific integer (inflation) value
for iInflations in range(10):
    for iSide in sideList:
        if iSide=='left':
            sideLabel=1000
            #extract spine ROI
            #28=LeftVentralDC
            #16=brainStem
            #10=leftThalamus
            targetSpineLocations =wmaPyTools.roiTools.multiROIrequestToMask(dkAtlas,[16, 28, 10])
        elif iSide=='right':
            sideLabel=2000
            #extract spine ROI
            #60=RightVentralDC
            #16=brainStem
            #49=leftThalamus
            targetSpineLocations =wmaPyTools.roiTools.multiROIrequestToMask(dkAtlas,[ 16, 60, 49])
        #create a name stem
        tractName=iSide+'_ACC_targeted_streams_' + str(iInflations)
        #saveSpineLocations
        nib.save(nib.nifti1.Nifti1Image(targetSpineLocations.get_fdata(), targetSpineLocations.affine),outDir+'/targetSpineLocations_ROI'+str(iInflations)+'.nii.gz')
        
        
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
            #41=RightCerebralWM
            contraWMROI=wmaPyTools.roiTools.multiROIrequestToMask(dkAtlas,41)
        elif sideLabel== 2000:
            #2=LeftCerebralWM
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
        #saveROI
        nib.save(nib.nifti1.Nifti1Image(supCCparaCantBorder.get_fdata(), supCCparaCantBorder.affine),outDir+'/supCCparaCantBorder_ROI'+str(iInflations)+'.nii.gz')
        
        
        #cingulum exclusion plane created
        
        #generate roi anterior border of rostralanteriorcingulate
        antCingROI=wmaPyTools.roiTools.multiROIrequestToMask(dkAtlas,sideLabel+26,2)
        #find the anterior border of it
        antCingBorderROI=wmaPyTools.roiTools.planeAtMaskBorder(antCingROI,'anterior')
        #save ROI
        nib.save(nib.nifti1.Nifti1Image(antCingBorderROI.get_fdata(), antCingBorderROI.affine),outDir+'/antCingBorderROI_ROI'+str(iInflations)+'.nii.gz')
       
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
        #save ROI
        nib.save(nib.nifti1.Nifti1Image(supPostCCBorder.get_fdata(), supPostCCBorder.affine),outDir+'/supPostCCBorder_ROI'+str(iInflations)+'.nii.gz')
        
        #posterior traversal exclusion ROI created
        
        #additional exclusion criteria lateral to thalamus and posterior to putamen, just for fun
        #obtain posterior border of putamen
        if sideLabel== 1000:
            #left putamen
            putROI=wmaPyTools.roiTools.multiROIrequestToMask(dkAtlas,12)
        elif sideLabel== 2000:
            #right putamen
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
        #use the supermarginal gyrus instead!  Thal can cross midline, 
        #messing up interpretation of lateral here
        superMarginalROI=wmaPyTools.roiTools.multiROIrequestToMask(dkAtlas,sideLabel+31)
        medialSuperMarBorder=wmaPyTools.roiTools.planeAtMaskBorder(superMarginalROI,'medial')
        #clip the posteriorPalBorder with the lateralThalBorder, retain lateral portion
        latPostPalBorder=wmaPyTools.roiTools.sliceROIwithPlane(posteriorPalBorder,medialSuperMarBorder,'lateral')
        #save ROI
        nib.save(nib.nifti1.Nifti1Image(latPostPalBorder.get_fdata(), latPostPalBorder.affine),outDir+'/latPostPalBorder_ROI'+str(iInflations)+'.nii.gz')
       
        #posterio-lateral exclusion criteria created
        
        #it's actually faster to do it with this multi version than individually
        #this is why all of the individual segmentation steps are grayed out above
        #comboROIBool=wmaPyTools.segmentationTools.segmentTractMultiROI(streamlines, [inflatedACC,targetSpineLocations,contraWMROI,sfgROI,supCCparaCantBorder,supPostCCBorder,antCingBorderROI,latPostPalBorder], [True,True,False,False,False,False,False,False], ['any','either_end','any','either_end','any','any','any','any'])
        comboROIBool=wmaPyTools.segmentationTools.segmentTractMultiROI(streamlines, [inflatedACC,targetSpineLocations,contraWMROI,sfgROI,supCCparaCantBorder,supPostCCBorder,antCingBorderROI], [True,True,False,False,False,False,False], ['any','either_end','any','either_end','any','any','any'])
        
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

