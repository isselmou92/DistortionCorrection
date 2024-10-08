import numpy as np
import matplotlib.pyplot as plt
import SimpleITK as sitk
import scipy.ndimage
from scipy.ndimage import map_coordinates


def formula(value):
    G_read_percentFLASH = 5.563298 / 100
    PVM_GradCal = 42797.5
    new_value = value / (G_read_percentFLASH * PVM_GradCal)
    return new_value


# Load MR volume
MR_Volume = sitk.ReadImage('b0_correction_analysis/Analysis_08_10_2024/mouse/mouse_35_MR.nii')
MR_Volume_Array = sitk.GetArrayFromImage(MR_Volume)

# Load corresponding B0 map
B0_Map = sitk.ReadImage('b0_correction_analysis/Analysis_08_10_2024/mouse/B0_Map_Mouse.nii')
B0_Map_Array = sitk.GetArrayFromImage(B0_Map)

# Skip registration step and directly resample B0 map to match MR volume

# Resample B0 Map to match MR Volume without registration
B0_Map_Resampled = sitk.Resample(B0_Map, MR_Volume, sitk.Transform(), sitk.sitkLinear, 0.0, B0_Map.GetPixelID())

# Upsample the registered B0 map
B0_Map_Resampled_Array = sitk.GetArrayFromImage(B0_Map_Resampled)
MR_Volume_Array = sitk.GetArrayFromImage(MR_Volume)

original_shape = B0_Map_Resampled_Array.shape
# target_shape = (78, 90, 90)
target_shape = (112, 128, 128)
zoom_factors = (target_shape[0] / original_shape[0],
                target_shape[1] / original_shape[1],
                target_shape[2] / original_shape[2])

# Upsample the volumes
B0_Map_Upsampled_Array = scipy.ndimage.zoom(B0_Map_Resampled_Array, zoom_factors, order=3)
MR_Volume_Upsampled_Array = scipy.ndimage.zoom(MR_Volume_Array, zoom_factors, order=3)

# Convert the upsampled numpy arrays back to SimpleITK images
B0_Map_Upsampled = sitk.GetImageFromArray(B0_Map_Upsampled_Array)
MR_Volume_Upsampled = sitk.GetImageFromArray(MR_Volume_Upsampled_Array)

# Copy the metadata (origin, spacing, direction) from the original images
B0_Map_Upsampled.SetOrigin(B0_Map.GetOrigin())
B0_Map_Upsampled.SetSpacing(
    [original_spacing / zoom for original_spacing, zoom in zip(B0_Map.GetSpacing(), zoom_factors)])
B0_Map_Upsampled.SetDirection(B0_Map.GetDirection())

MR_Volume_Upsampled.SetOrigin(MR_Volume.GetOrigin())
MR_Volume_Upsampled.SetSpacing(
    [original_spacing / zoom for original_spacing, zoom in zip(MR_Volume.GetSpacing(), zoom_factors)])
MR_Volume_Upsampled.SetDirection(MR_Volume.GetDirection())

# B0 Shift in mm
B0_Map_Array_mm = formula(B0_Map_Upsampled_Array)

# Assuming the shifts are in the z-direction, create a deformation field
deformation_field = np.zeros(B0_Map_Array_mm.shape + (3,), dtype=np.float64)

# Deformation in z direction
deformation_field[..., 2] = B0_Map_Array_mm

# Convert the numpy array to a SimpleITK image
deformation_field_sitk = sitk.GetImageFromArray(deformation_field, isVector=True)
deformation_field_sitk = sitk.Cast(deformation_field_sitk, sitk.sitkVectorFloat64)
deformation_field_sitk.CopyInformation(MR_Volume_Upsampled)

# Resample the upsampled MR volume using the deformation field
resampler = sitk.ResampleImageFilter()
resampler.SetReferenceImage(MR_Volume_Upsampled)
resampler.SetInterpolator(sitk.sitkBSpline)  # sitkLinear
resampler.SetDefaultPixelValue(0)
resampler.SetTransform(sitk.DisplacementFieldTransform(deformation_field_sitk))

corrected_volume = resampler.Execute(MR_Volume_Upsampled)

# Convert the corrected volume to a numpy array for further processing or visualization
corrected_volume_array = sitk.GetArrayFromImage(corrected_volume)

# Write to file
sitk.WriteImage(corrected_volume,
                'b0_correction_analysis/Analysis_08_10_2024/mouse/mouse_35_mr_b0_corrected.nii')


# Display the results
plt.figure(figsize=(12, 6))
plt.subplot(1, 3, 1)
plt.title("Original MR Slice")
plt.imshow(MR_Volume_Upsampled_Array[MR_Volume_Upsampled_Array.shape[0] // 2], cmap='gray')
plt.subplot(1, 3, 2)
plt.title("Displacement Field")
plt.imshow(B0_Map_Array_mm[B0_Map_Array_mm.shape[0] // 2], cmap='jet')
plt.subplot(1, 3, 3)
plt.title("Corrected MR Slice")
plt.imshow(corrected_volume_array[corrected_volume_array.shape[0] // 2], cmap='gray')
plt.show()

## Apply phantom displacementfield on mouse volume

# Load rigid mouse MR
Mouse_Rigid_B0 = sitk.ReadImage(
    'b0_correction_analysis/Analysis_08_10_2024/mouse/mouse_35_mr_b0_corrected.nii')
Mouse_Rigid_B0_Array = sitk.GetArrayFromImage(Mouse_Rigid_B0)

# Load cropped phantom displacement field
Phantom_Displacement_Field = sitk.ReadImage(
    'b0_correction_analysis/Analysis_08_10_2024/mouse/Cropped_Displacement_Field_Mouse_Dimensions.nii')
Phantom_Displacement_Field_Array = sitk.GetArrayFromImage(Phantom_Displacement_Field)

# Create grid for original coordinates
nx, ny, nz = Mouse_Rigid_B0_Array.shape
x, y, z = np.arange(nx), np.arange(ny), np.arange(nz)
X, Y, Z = np.meshgrid(x, y, z, indexing='ij')

# Resample the phantom displacement field to match the MRI volume shape
zoom_factors = (
    Mouse_Rigid_B0_Array.shape[0] / Phantom_Displacement_Field_Array.shape[0],
    Mouse_Rigid_B0_Array.shape[1] / Phantom_Displacement_Field_Array.shape[1],
    Mouse_Rigid_B0_Array.shape[2] / Phantom_Displacement_Field_Array.shape[2],
)

# Apply zoom to the displacement field for each component (x, y, z)
Phantom_Displacement_Field_Array_Resampled = np.zeros(Mouse_Rigid_B0_Array.shape + (3,))
for i in range(3):
    Phantom_Displacement_Field_Array_Resampled[..., i] = scipy.ndimage.zoom(
        Phantom_Displacement_Field_Array[..., i], zoom_factors, order=3
    )

# Apply the displacement field (displacement is now in the last dimension)
displaced_X = X + Phantom_Displacement_Field_Array_Resampled[..., 0]
displaced_Y = Y + Phantom_Displacement_Field_Array_Resampled[..., 1]
displaced_Z = Z + Phantom_Displacement_Field_Array_Resampled[..., 2]

# Interpolate
Mouse_Rigid_B0_with_Phantom_Displacement_Field = map_coordinates(Mouse_Rigid_B0_Array,
                                                                 [displaced_X, displaced_Y, displaced_Z], order=3,
                                                                 mode='reflect')

# Convert the result back to a SimpleITK image
Mouse_Rigid_B0_with_Phantom_Displacement_Field_Volume = sitk.GetImageFromArray(
    Mouse_Rigid_B0_with_Phantom_Displacement_Field)
Mouse_Rigid_B0_with_Phantom_Displacement_Field_Volume.CopyInformation(Mouse_Rigid_B0)

# Save the final volume
sitk.WriteImage(Mouse_Rigid_B0_with_Phantom_Displacement_Field_Volume,
                "b0_correction_analysis/Analysis_08_10_2024/mouse/Mouse_B0_Corrected_with_Phantom_Displacement_Field_Volume_MR_resolution.nii")
