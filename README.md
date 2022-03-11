# Anterior Cingulate Cortex segmentation
An anatomically defined, subject specific tractography segmention of connections to the human anterior cingulate cortex.

## Overview description

This repository contains a number dockerized scripts used for processing anatomical
and dwi data to be used in the modeling of connections to the anterior cingulate cortex
in humans.

## Author, funding sources, references

### Authors
- [Dan Bullock](https://github.com/DanNBullock/) ([bullo092@umn.edu](mailto:bullo092@umn.edu))

### Contributors

- [Henry Braun](https://github.com/hbraunDSP)

### PI
- [Sarah Heilbronner](https://med.umn.edu/bio/department-of-neuroscience/sarah-heilbronner) ([heilb028@umn.edu](mailto:heilb028@umn.edu))

### Funding
[![NIH-NIBIB-1T32EB031512-01](https://img.shields.io/badge/NIH_NIBIB-1T32EB031512--01-blue.svg)](https://reporter.nih.gov/project-details/10205698)
[![NIMH-5P50MH119569-02](https://img.shields.io/badge/NIMH-5P50MH119569--02-blue.svg)](https://reporter.nih.gov/project-details/10123009)
[![NIMH-5R01MH118257-04](https://img.shields.io/badge/NIMH-5R01MH118257--04-blue.svg)](https://reporter.nih.gov/project-details/10122991)
[![NIDA-1P30DA048742-01A1](https://img.shields.io/badge/NIDA-1P30DA048742--01A1-blue.svg)](https://reporter.nih.gov/project-details/10025457)

* [Dan Bullock](https://github.com/DanNBullock/)'s work is supported by the following sources:
    - The University of Minnesota’s Neuroimaging Postdoctoral Fellowship Program, College of Science and Engineering's, and the Medical School's NIH funded T32 Neuroimaging Training Grant. NOGA: [1T32EB031512-01](https://reporter.nih.gov/project-details/10205698) 

- [Sarah Heilbronner](https://med.umn.edu/bio/department-of-neuroscience/sarah-heilbronner)'s work is supported by the following sources:
    - The University of Minnesota’s Neurosciences' and Medical School's NIMH grant for the investigation of "Neural Basis of Psychopathology, Addictions and Sleep Disorders Study Section[NPAS]". NOGA: [5P50MH119569-02-04](https://reporter.nih.gov/project-details/10123009) 
    - The University of Minnesota’s Neurosciences' Translational Neurophysiology grant. NOGA: [5R01MH118257-04](https://reporter.nih.gov/project-details/10122991)
    - The University of Minnesota’s Neurosciences' Addiction Connectome grant. NOGA: [1P30DA048742-01A1](https://reporter.nih.gov/project-details/10025457)
    
### Using this repository

#### Overarching pipeline sequencing

This repository is designed to facilitate a platform-independent method for performing a segmentation of the anterior cingulate cortex given relatively raw anatomical (T1) and diffusion (DWI) data.  To this end it makes use of the following existing brainlife app dockerizations:

1. [Align T1 to ACPC Plane (HCP-based)](https://brainlife.io/app/5b96d5ed059cf9002719250b): found in **acpcAlignViaDocker**
2. [Freesurfer 7.1.1](https://brainlife.io/app/5fe1056057aacd480f2f8e48): found in **fsViaDocker** 
3. [mrtrix3 preproces](https://brainlife.io/app/5a813e52dc4031003b8b36f9): found in **preProcViaDocker**
4. [RACE-Track | MRTrix3 Anatomical Informed Tractography](https://brainlife.io/app/5aac2437f0b5260027e24ae1): found in **trackViaDocker**

This is followed by a dockerized run of the ACC segmentation itself, contained in **segViaDocker** (which does not currently have a corresponding brainlife app). The performance of this final step should (if successful) result in the creation of several ACC tract variants (based on inflation iterations) and corresponding quality assurance and quantification outputs, as specified in **ACCSeg_script.py**.

#### Input file structuring

Input files for **T1** and **DWI** should be placed into the **testdata** directory.

The **acpcAlignViaDocker** step expects a (presumably unaligned) T1 nifti image in this directory (i.e. testdata/t1.nii.gz), as indicated
in the **input** field of the corresponding **config.json**.

The **preProcViaDocker** step expects two subdirectories this directory corresponding to the ap and pa components of a dwi image (i.e. testdata/ap & testdata/pa).  In each of these sub directories the following three files are expected: *dwi.bvecs*, *dwi.bvals*, *dwi.nii.gz*, as indicated the corresponding config.json.  Note that, for data sets without ap & pa sessions, it will be necessary to reconfigure the config.json for this process.

#### Usage notes

Initial testing has revealed the following issues to keep in mind when using this pipeline:

1.  Freesurfer requires the presence of a freesurfer license on the system on which the docker run is submitted from. Specifically, the **main** file found within the **fsViaDocker** directory will look for a **FREESURFER_LICENSE** environmental variable and will error out if such a variable is not found.  Within the user's bashrc profile, it is recomended to set up this variable in some fashion equivalent to this:
> FREESURFER_LICENSE=$(</usr/local/freesurfer/license.txt)

2.  Docker (or perhaps more accurately, singularity) may not always handle bind paths in an ideal fashion.  Testing has demonstrated that running
of the ACC segmentation pipeline on a mounted drive in linux results in bind path issues (e.g. directory contents not being available to the internal operations of the container).  Running the ACC segmentation pipeline from the desktop appears to avoid this issue (thanks to Brad Caron for this suggestion).

#### Omnibus script usage

To run this sequence of processing steps as a contiguous pipeline users should run the **bigMain** file contained within the primary accSeg directory (currently on the _dockerized_ branch).
