# B0 Correction and Phantom Displacement Field Application
## Repository Description

This repository provides Python scripts for correcting geometric distortions in ultra-high field (15.2T) MR images caused by magnetic field inhomogeneities (ΔB0) and gradient non-linearities (GNL). It implements a two-step distortion correction (2SDC) method—first correcting ΔB0 distortions using registered static field maps, and then applying a phantom-based displacement map to correct GNL-induced distortions. The method has been validated on phantom data and in-vivo mouse brain MR images.
This repository contains two Python scripts for:
1. **B0 Correction** of MRI data (using a registered B0 map).
2. **Phantom Displacement Field** application on the B0-corrected volume.

Below you’ll find instructions on how to install dependencies, run the scripts, and understand the expected input and output data.

---

## Table of Contents
1. [Repository Structure](#repository-structure)
2. [Dependencies](#dependencies)
3. [Installation](#installation)
4. [Usage](#usage)
   1. [B0 Correction](#1-b0-correction)
   2. [Apply Phantom Displacement Field](#2-apply-phantom-displacement)
5. [Example Directory Layout](#example-directory-layout)
6. [Outputs](#outputs)
7. [Citation](#citation)
8. [License](#license)

---

## Repository Structure

A layout could be:

```console
b0_correction_analysis/
└── Analysis_08_10_2024/
    └── mouse/
        ├── mouse_35_MR.nii
        ├── B0_Map_Mouse.nii
        ├── Cropped_Displacement_Field_Mouse_Dimensions.nii
        ├── mouse_35_mr_b0_corrected.nii                                # (created by b0_correction.py)
        └── Mouse_B0_Corrected_with_Phantom_Displacement_Field_Volume_MR_resolution.nii   # (created by phantom_displacement.py)
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


