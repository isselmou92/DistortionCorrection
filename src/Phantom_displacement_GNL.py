# phantom_displacement.py

import numpy as np
import SimpleITK as sitk
import scipy.ndimage
from scipy.ndimage import map_coordinates

def main():
    # 1. Load the B0-corrected mouse MR volume
    Mouse_Rigid_B0 = sitk.ReadImage(
        'b0_correction_analysis/Analysis_08_10_2024/mouse/mouse_35_mr_b0_corrected.nii'
    )
    Mouse_Rigid_B0_Array = sitk.GetArrayFromImage(Mouse_Rigid_B0)

    # 2. Load the cropped phantom displacement field
    Phantom_Displacement_Field = sitk.ReadImage(
        'b0_correction_analysis/Analysis_08_10_2024/mouse/Cropped_Displacement_Field_Mouse_Dimensions.nii'
    )
    Phantom_Displacement_Field_Array = sitk.GetArrayFromImage(Phantom_Displacement_Field)

    # 3. Create mesh grid for the original coordinates
    nx, ny, nz = Mouse_Rigid_B0_Array.shape
    x = np.arange(nx)
    y = np.arange(ny)
    z = np.arange(nz)
    X, Y, Z = np.meshgrid(x, y, z, indexing='ij')

    # 4. Resample the phantom displacement field to match the MRI volume shape
    zoom_factors = (
        Mouse_Rigid_B0_Array.shape[0] / Phantom_Displacement_Field_Array.shape[0],
        Mouse_Rigid_B0_Array.shape[1] / Phantom_Displacement_Field_Array.shape[1],
        Mouse_Rigid_B0_Array.shape[2] / Phantom_Displacement_Field_Array.shape[2],
    )

    Phantom_Displacement_Field_Array_Resampled = np.zeros(Mouse_Rigid_B0_Array.shape + (3,))
    for i in range(3):
        Phantom_Displacement_Field_Array_Resampled[..., i] = scipy.ndimage.zoom(
            Phantom_Displacement_Field_Array[..., i],
            zoom_factors,
            order=3
        )

    # 5. Apply the displacement field
    displaced_X = X + Phantom_Displacement_Field_Array_Resampled[..., 0]
    displaced_Y = Y + Phantom_Displacement_Field_Array_Resampled[..., 1]
    displaced_Z = Z + Phantom_Displacement_Field_Array_Resampled[..., 2]

    # 6. Interpolate the B0-corrected volume with the phantom displacement
    Mouse_Rigid_B0_with_Phantom_Displacement_Field = map_coordinates(
        Mouse_Rigid_B0_Array,
        [displaced_X, displaced_Y, displaced_Z],
        order=3,
        mode='reflect'
    )

    # 7. Convert back to a SimpleITK image and save
    Mouse_Rigid_B0_with_Phantom_Displacement_Field_Volume = sitk.GetImageFromArray(
        Mouse_Rigid_B0_with_Phantom_Displacement_Field
    )
    Mouse_Rigid_B0_with_Phantom_Displacement_Field_Volume.CopyInformation(Mouse_Rigid_B0)

    sitk.WriteImage(
        Mouse_Rigid_B0_with_Phantom_Displacement_Field_Volume,
        "b0_correction_analysis/Analysis_08_10_2024/mouse/Mouse_B0_Corrected_with_Phantom_Displacement_Field_Volume_MR_resolution.nii"
    )

if __name__ == "__main__":
    main()
