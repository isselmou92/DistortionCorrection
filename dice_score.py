import nibabel as nib
import numpy as np
import matplotlib.pyplot as plt

def load_nifti(file_path):
    """Load a NIfTI file and return the image data."""
    img = nib.load(file_path)
    return img.get_fdata()

def dice_coefficient(seg1, seg2):
    """Compute the Dice coefficient between two binary phantom_segmentations."""
    intersection = np.sum((seg1 > 0) & (seg2 > 0))
    volume_sum = np.sum(seg1 > 0) + np.sum(seg2 > 0)
    if volume_sum == 0:
        return 1.0  # Both phantom_segmentations are empty
    return 2.0 * intersection / volume_sum

def visualize_slice(slice1, slice2, slice3, slice_idx):
    """Visualize slices of the three phantom_segmentations."""
    fig, axs = plt.subplots(1, 3, figsize=(15, 5))
    axs[0].imshow(slice1, cmap='gray')
    axs[0].set_title('Segmentation 1')
    axs[1].imshow(slice2, cmap='gray')
    axs[1].set_title('Segmentation 2')
    axs[2].imshow(slice3, cmap='gray')
    axs[2].set_title('Segmentation 3')
    plt.suptitle(f'Slice {slice_idx}')
    plt.show()

def main():
    # Load the three phantom_segmentations
    seg1_path = 'b0_correction_analysis/data/phantom_segmentations/CT_Segmentation-CT_segmentation-label.nii'
    seg2_path = 'b0_correction_analysis/data/phantom_segmentations/B0_Segmentation-label.nii'
    seg3_path = 'b0_correction_analysis/data/phantom_segmentations/Segmentation-mr_volume_no_b0-label.nii'

    seg1 = load_nifti(seg1_path)
    seg2 = load_nifti(seg2_path)
    seg3 = load_nifti(seg3_path)

    # Compute Dice scores
    dice_seg2 = dice_coefficient(seg1, seg2)
    dice_seg3 = dice_coefficient(seg1, seg3)

    print(f"Dice score for Segmentation CT and Segmentation B0-Corrected: {dice_seg2:.4f}")
    print(f"Dice score for Segmentation CT and Segmentation Non-Corrected: {dice_seg3:.4f}")

    # Visualize some slices
    # slice_idx = seg1.shape[2] // 2  # Choose a middle slice for visualization
    # visualize_slice(seg1[:, slice_idx, :], seg2[:, slice_idx, :], seg3[:, slice_idx, :], slice_idx)

if __name__ == '__main__':
    main()
