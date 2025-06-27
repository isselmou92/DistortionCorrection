# Pipeline for system-dependent geometric distortion correction in UHF-MR images 
## Repository Description

Ultra-high field (UHF) magnetic resonance (MR) systems are advancing in clinical and especially preclinical imaging research offering the potential to enhance radiation research. However, system-dependent factors, such as magnetic field inhomogeneities (ΔB0) and gradient non-linearities (GNL), induce geometric distortions compromising the sub-millimetre accuracy required for radiation research. 

The geometric distortion corrections are performed using the **two-step distortion correction (2SDC)** method, which separately addresses ΔB0- and GNL-related displacements in two consecutive steps.

- In the first step, ΔB0 displacements affecting only the frequency encoding direction  are independently corrected via the Python script [`B0_Correction.py`](src/B0_correction.py) using a pre-acquired static field map, resulting in an ΔB0-corrected MR image.

- In the second step, a phantom-driven displacement map containing the GNL-induced displacements, which can be obtained with non-rigid registration, is applied to the ΔB0-corrected MR image via a second custom Python script [`Phantom_displacement_GNL.py`](src/Phantom_displacement_GNL.py) to correct specifically for GNL. This application is possible by assuming that the GNL distortion is sequence-independent, remaining constant across scans and subjects.

Our 2SDC method has been specifically validated on preclinical in-vivo mouse brain MR images at 15.2T (Bruker BioSpin, Germany).

### Included Scripts
The following two in-house developed Python scripts are included and need to be applied to your MR dataset to correct system-dependent geometric distortions, as described above: 
- [`B0_Correction.py`](src/B0_correction.py)
- [`Phantom_displacement_GNL.py`](src/Phantom_displacement_GNL.py)

Below, you'll find instructions for installing dependencies, running the scripts, and understanding the required input and expected output data. 

## Table of Contents
1. [Repository Structure](#repository-structure)
2. [Dependencies](#dependencies)
3. [Installation](#installation)
4. [Usage](#usage)
   1. [B0 Correction](#1-b0-correction)
   2. [Apply Phantom Displacement Field](#2-phantom-displacement-field-for-gnl-correction)
5. [Citation](#citation)
---

## Repository Structure

A layout could be:

```console
b0_correction_analysis/
└── Analysis/
    └── data/
        ├──  MR Volume
        ├──  static field map
        ├──  Displacement Field with Diemensions of MR Volume.nii
        ├──  ΔB0-corrected MR volume.nii   # (created by B0_correction.py)
        └──  ΔB0+GNL corrected MR volume   # (created by Phantom_displacement_GNL.py)
```

## Dependencies
- **Python 3.x**  
- **numpy** (e.g., `>=1.21.0`)
- **matplotlib** (e.g., `>=3.4.2`)
- **SimpleITK** (e.g., `>=2.1.1`)
- **scipy** (e.g., `>=1.7.1`)

These dependencies are included in the `requirements.txt` file.

## Installation

Clone this repository:

```console
git clone https://github.com/isselmou92/DistortionCorrection.git
cd B0_correction_project
```
To innstall dependencies. You can use pip:

```console
pip install -r requirements.txt
```
Make sure you have a suitable C++ compiler if you’re on Windows (some libraries may need it).

## Usage
### 1. B0 Correction
Run the [`B0_Correction.py`](src/B0_correction.py) script. By default, it expects two Nifti MR images, as described in the following example: 
- MR volume intended to be corrected
  
- Static field map of the same subject 

#### b0_correction script’s workflow: 

- Reads the input MR volume and static field map.
  
- Registers the static field map to the MR volume using a Mattes Mutual Information metric. 

- Resamples and upsamples the static field map and MR volume. 

- Converts the static field map voxel values in frequencies (Hz) to spatial displacement values in millimetres (mm), according to the formula d=ΔB0/G, where ΔB0 corresponds to the static field inhomogeneity present in each voxel of the static field map and G is the gradient strength along the frequency encoding direction. A ΔB0-spatial field map is generated.


The script sets the z-axis as the frequency encoding direction. However, the user needs to reset the frequency direction and the G parameter, according to their image acquisition. 

- Applies the ΔB0-spatial field map in mm to the MR volume, resulting in a ΔB0-corrected MR image. 

- Writes the ΔB0-corrected MR volume to a Nifti file. 

Displays a figure with three subplots:

- Original MR volume in slices 

- ΔB0-spatial field map in mm 

- ΔB0-corrected MR image in slices

### 2. Phantom Displacement Field for GNL correction
Once the ΔB0-corrected MR image is created, run the second script for GNL correction [`Phantom_displacement_GNL.py`](src/Phantom_displacement_GNL.py)

By default, it expects two Nifti MR images, as described in the following example: 
- ΔB0-corrected MR volume intended to be corrected for GNL.

- A displacement map of a phantom, obtained after non-rigid registration with a CT image of the same object, which includes GNL-induced displacements in mm per each voxel.

#### phantom_displacement_GNL script’s workflow: 


- Reads the newly created ΔB0-corrected MR volume from the previous script.

- Reads the phantom displacement field.
  
- Resamples the phantom field to match the ΔB0-corrected MR volume dimensions.

- Applies this phantom displacement field to the ΔB0-corrected MR image by shifting the voxels in each spatial direction (x,y,z) according to the displacements indicated in the phantom displacement map.

- Writes the ΔB0+GNL corrected MR volume to a Nifti file.
## Citation
```console
S. Stocchiero, I. Abdarahmane, E. Poblador Rodriguez, V. Froehlich, M. Zeilinger, and D. Georg, “Assessment and mitigiation of geometric distortions in MR images at 15.2T for preclinical radiation research,” Medical Physics, 2025, doi: 10.1002/mp.17963.
```
