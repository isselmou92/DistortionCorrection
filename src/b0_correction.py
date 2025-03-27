# b0_correction.py

import numpy as np
import matplotlib.pyplot as plt
import SimpleITK as sitk
import scipy.ndimage

def formula(value):
    """Converts the raw B0 map values into millimeter shifts."""
    G_read_percentFLASH = 5.563298 / 100
    PVM_GradCal = 42797.5
    new_value = value / (G_read_percentFLASH * PVM_GradCal)
    return new_value

def main():
    # ------------------------------
    # 1. Load MR volume and B0 map
    # ------------------------------
    MR_Volume = sitk.ReadImage('b0_correction_analysis/Analysis_08_10_2024/mouse/mouse_35_MR.nii')
    MR_Volume_Array = sitk.GetArrayFromImage(MR_Volume)

    B0_Map = sitk.ReadImage('b0_correction_analysis/Analysis_08_10_2024/mouse/B0_Map_Mouse.nii')

    # ------------------------------
    # 2. Registration
    # ------------------------------
    initial_transform = sitk.CenteredTransformInitializer(
        MR_Volume,
        B0_Map,
        sitk.Euler3DTransform(),
        sitk.CenteredTransformInitializerFilter.GEOMETRY
    )

    registration_method = sitk.ImageRegistrationMethod()
    registration_method.SetMetricAsMattesMutualInformation(numberOfHistogramBins=50)
    registration_method.SetMetricSamplingStrategy(registration_method.RANDOM)
    registration_method.SetMetricSamplingPercentage(0.01)
    registration_method.SetInterpolator(sitk.sitkLinear)
    registration_method.SetOptimizerAsGradientDescent(
        learningRate=1.0, numberOfIterations=100,
        convergenceMinimumValue=1e-6, convergenceWindowSize=10
    )
    registration_method.SetOptimizerScalesFromPhysicalShift()

    registration_method.SetInitialTransform(initial_transform, inPlace=False)
    registration_method.SetShrinkFactorsPerLevel(shrinkFactors=[4, 2, 1])
    registration_method.SetSmoothingSigmasPerLevel(smoothingSigmas=[2, 1, 0])
    registration_method.SmoothingSigmasAreSpecifiedInPhysicalUnitsOn()

    final_transform = registration_method.Execute(
        sitk.Cast(MR_Volume, sitk.sitkFloat32),
        sitk.Cast(B0_Map, sitk.sitkFloat32)
    )

    # Resample B0 map to align with MR volume
    B0_Map_Resampled = sitk.Resample(
        B0_Map,
        MR_Volume,
        final_transform,
        sitk.sitkLinear,
        0.0,
        B0_Map.GetPixelID()
    )

    # ------------------------------
    # 3. Upsampling
    # ------------------------------
    B0_Map_Resampled_Array = sitk.GetArrayFromImage(B0_Map_Resampled)
    MR_Volume_Array = sitk.GetArrayFromImage(MR_Volume)

    original_shape = B0_Map_Resampled_Array.shape
    target_shape = (112, 128, 128)  # Adjust if needed
    zoom_factors = (
        target_shape[0] / original_shape[0],
        target_shape[1] / original_shape[1],
        target_shape[2] / original_shape[2]
    )

    B0_Map_Upsampled_Array = scipy.ndimage.zoom(B0_Map_Resampled_Array, zoom_factors, order=3)
    MR_Volume_Upsampled_Array = scipy.ndimage.zoom(MR_Volume_Array, zoom_factors, order=3)

    B0_Map_Upsampled = sitk.GetImageFromArray(B0_Map_Upsampled_Array)
    MR_Volume_Upsampled = sitk.GetImageFromArray(MR_Volume_Upsampled_Array)

    B0_Map_Upsampled.SetOrigin(B0_Map.GetOrigin())
    B0_Map_Upsampled.SetSpacing([
        orig_sp / zf for orig_sp, zf in zip(B0_Map.GetSpacing(), zoom_factors)
    ])
    B0_Map_Upsampled.SetDirection(B0_Map.GetDirection())

    MR_Volume_Upsampled.SetOrigin(MR_Volume.GetOrigin())
    MR_Volume_Upsampled.SetSpacing([
        orig_sp / zf for orig_sp, zf in zip(MR_Volume.GetSpacing(), zoom_factors)
    ])
    MR_Volume_Upsampled.SetDirection(MR_Volume.GetDirection())

    # ------------------------------
    # 4. Create displacement field
    # ------------------------------
    B0_Map_Array_mm = formula(B0_Map_Upsampled_Array)

    # Assuming shift is in z-direction
    deformation_field = np.zeros(B0_Map_Array_mm.shape + (3,), dtype=np.float64)
    deformation_field[..., 2] = B0_Map_Array_mm

    deformation_field_sitk = sitk.GetImageFromArray(deformation_field, isVector=True)
    deformation_field_sitk = sitk.Cast(deformation_field_sitk, sitk.sitkVectorFloat64)
    deformation_field_sitk.CopyInformation(MR_Volume_Upsampled)

    # ------------------------------
    # 5. Apply displacement field
    # ------------------------------
    resampler = sitk.ResampleImageFilter()
    resampler.SetReferenceImage(MR_Volume_Upsampled)
    resampler.SetInterpolator(sitk.sitkBSpline)
    resampler.SetDefaultPixelValue(0)
    resampler.SetTransform(sitk.DisplacementFieldTransform(deformation_field_sitk))

    corrected_volume = resampler.Execute(MR_Volume_Upsampled)
    corrected_volume_array = sitk.GetArrayFromImage(corrected_volume)

    # ------------------------------
    # 6. Save results and visualize
    # ------------------------------
    sitk.WriteImage(corrected_volume, 'b0_correction_analysis/Analysis_08_10_2024/mouse/mouse_35_mr_b0_corrected.nii')

    # Quick visualization
    mid_slice_MR = MR_Volume_Upsampled_Array.shape[0] // 2
    mid_slice_B0 = B0_Map_Array_mm.shape[0] // 2
    mid_slice_corrected = corrected_volume_array.shape[0] // 2

    plt.figure(figsize=(12, 6))
    plt.subplot(1, 3, 1)
    plt.title("Original MR Slice")
    plt.imshow(MR_Volume_Upsampled_Array[mid_slice_MR], cmap='gray')

    plt.subplot(1, 3, 2)
    plt.title("Displacement Field (Z-shift)")
    plt.imshow(B0_Map_Array_mm[mid_slice_B0], cmap='jet')

    plt.subplot(1, 3, 3)
    plt.title("Corrected MR Slice")
    plt.imshow(corrected_volume_array[mid_slice_corrected], cmap='gray')

    plt.show()

if __name__ == "__main__":
    main()
