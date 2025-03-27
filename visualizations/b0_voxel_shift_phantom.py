import numpy as np
import matplotlib.pyplot as plt
import SimpleITK as sitk


def formula(value):
    G_read_percentFLASH = 5.563298 / 100
    PVM_GradCal = 42797.5
    new_value = value / (G_read_percentFLASH * PVM_GradCal)
    return new_value


# Load MR volume
# MR_Volume = sitk.ReadImage('b0_correction_analysis/Analaysis_19_09_2024/MR_CT_phantom/MR_GRE_FLASH_Shim1_original.dcm')
MR_Volume = sitk.ReadImage('b0_correction_analysis/Analaysis_19_09_2024/MR_CT_phantom/MR_GRE_FLASH_Shim2_original.dcm')
MR_Volume_Array = sitk.GetArrayFromImage(MR_Volume)

# Load corresponding B0 map
# B0_Map = sitk.ReadImage('b0_correction_analysis/Analaysis_19_09_2024/MR_CT_phantom/B0map_Shim1.dcm')
B0_Map = sitk.ReadImage('b0_correction_analysis/Analaysis_19_09_2024/MR_CT_phantom/B0map_Shim2.dcm')
B0_Map_Array = sitk.GetArrayFromImage(B0_Map)

# B0 Shift in mm
B0_Map_Array_mm = formula(B0_Map_Array)

# Assuming the shifts are in the z-direction, create a deformation field
deformation_field = np.zeros(B0_Map_Array_mm.shape + (3,), dtype=np.float64)

# Deformation in z direction
deformation_field[..., 2] = B0_Map_Array_mm

# Convert the numpy array to a SimpleITK image
deformation_field_sitk = sitk.GetImageFromArray(deformation_field, isVector=True)
deformation_field_sitk = sitk.Cast(deformation_field_sitk, sitk.sitkVectorFloat64)
deformation_field_sitk.CopyInformation(MR_Volume)

# Resample the original MR volume using the deformation field
resampler = sitk.ResampleImageFilter()
resampler.SetReferenceImage(MR_Volume)
resampler.SetInterpolator(sitk.sitkBSpline)  # sitkLinear
resampler.SetDefaultPixelValue(0)
resampler.SetTransform(sitk.DisplacementFieldTransform(deformation_field_sitk))

corrected_volume = resampler.Execute(MR_Volume)

# Convert the corrected volume to a numpy array for further processing or visualization
corrected_volume_array = sitk.GetArrayFromImage(corrected_volume)

# sitk.WriteImage(corrected_volume, 'b0_correction_analysis/Analaysis_19_09_2024/results/MR_GRE_FLASH_Shim1_B0_corrected.nii')
sitk.WriteImage(corrected_volume, 'b0_correction_analysis/Analaysis_19_09_2024/results/MR_GRE_FLASH_Shim2_B0_corrected.nii')

# Display the results
plt.figure(figsize=(12, 6))
plt.subplot(1, 3, 1)
plt.title("Original MR Slice")
plt.imshow(MR_Volume_Array[MR_Volume_Array.shape[0] // 2], cmap='gray')
plt.subplot(1, 3, 2)
plt.title("Displacement Field")
plt.imshow(B0_Map_Array_mm[B0_Map_Array_mm.shape[0] // 2], cmap='jet')
plt.subplot(1, 3, 3)
plt.title("Corrected MR Slice")
plt.imshow(corrected_volume_array[corrected_volume_array.shape[0] // 2], cmap='gray')
plt.show()
