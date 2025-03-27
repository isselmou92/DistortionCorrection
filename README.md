# B0 Correction and Phantom Displacement Field Application
## Repository Description

This repository provides Python scripts for correcting geometric distortions in ultra-high field (15.2T) MR images caused by magnetic field inhomogeneities (ΔB0) and gradient non-linearities (GNL). It implements a two-step distortion correction (2SDC) method—first correcting ΔB0 distortions using registered static field maps, and then applying a phantom-based displacement map to correct GNL-induced distortions. The method has been validated on phantom data and in-vivo mouse brain MR images.
This repository contains two Python scripts for:
1. **B0 Correction** of MRI data (using a registered B0 map).
2. **Phantom Displacement** application on the B0-corrected volume.

Below you’ll find instructions on how to install dependencies, run the scripts, and understand the expected input and output data.

---

## Table of Contents
1. [Repository Structure](#repository-structure)
2. [Dependencies](#dependencies)
3. [Installation](#installation)
4. [Usage](#usage)
   1. [B0 Correction](#1-b0-correction)
   2. [Apply Phantom Displacement](#2-apply-phantom-displacement)
5. [Example Directory Layout](#example-directory-layout)
6. [Outputs](#outputs)
7. [Citation](#citation)
8. [License](#license)

---

## Repository Structure

A simple layout could be:

